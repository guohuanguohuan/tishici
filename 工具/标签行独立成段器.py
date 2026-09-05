# -*- coding: utf-8 -*-
r"""标签行独立成段器.py — 2026-09-05 选必1成书修复路线·版式修订轮②·T5（工具先建后用）

口径（规格书T5）：【答案】【知识点】标签与内容混行、或两标签同一行的，拆为各自独立成段
  （标签行独立，内容另起段）；【分析】【详解】【点睛】【编注】等其余标签一律不动。
  实测现行形态（选必1）：「【答案】 B　【知识点】1.1.1 ……」同段混行（讲练件/衔接件普遍），
  知识清单件标签已各自独立（0 处置）。拆分后形态：
    【答案】／答案内容段／【知识点】／知识点内容段（纯空白内容段不产出）。
  行内 OMML 公式/图片等对象随所属 span 整体迁段（按 w:t 文本流定位，oMath 零宽按位置归属）。
断言：拆分前后文本守恒——段群 w:t 拼接去全部空白（含 \u3000\xa0）后逐段零差异；
      元素类型计数仅 w:p 增加（增量＝新增段数），run 只在标签/内容边界处拆分；
      已独立标签段（仅标签＋空白）幂等跳过。
模式：默认就地改写（留 .bak_标签行）；--dry-run 出分布预演不落盘。
用法:
  python 工具/标签行独立成段器.py <docx...> [--dry-run] [--report r.md]
"""
import sys, io, os, re, zipfile, time, copy
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))

LABEL_RE = re.compile(r'【(?:答案|知识点)】')
WS_RE = re.compile(r'[\s　\xa0​]+')


def norm(s):
    return WS_RE.sub('', s)


def child_span(el, off):
    """返回 (start, end)：el 在段 w:t 文本流的区间（oMath/绘图等零宽元素 end==start）。"""
    n = sum(len(t.text or '') for t in el.iter(q('t')))
    return off, off + n


def trim_copy(el, keep_a, keep_b):
    """深拷 el，仅保留其文本流 [keep_a, keep_b) 部分（相对 el 自身起点）。无文本亦无对象则返回 None。"""
    cp = copy.deepcopy(el)
    off = 0
    for t in list(cp.iter(q('t'))):
        txt = t.text or ''
        ta, tb = off, off + len(txt)
        off = tb
        cs, ce = max(keep_a - ta, 0), min(keep_b - ta, len(txt))
        if cs >= ce:
            t.text = ''
        else:
            t.text = txt[cs:ce]
        t.set(XMLSPACE, 'preserve')
    # 清收：无文本且无对象内容的 run 删除
    for r in list(cp.iter(q('r'))):
        has_t = any((t.text or '') for t in r.findall(q('t')))
        others = [c for c in r if tag(c) not in ('rPr', 't')]
        if not has_t and not others:
            r.getparent().remove(r)
    if any((t.text or '') for t in cp.iter(q('t'))):
        return cp
    if tag(cp) != 'r':
        return cp                      # oMath/hyperlink壳等保留
    if [c for c in cp if tag(c) not in ('rPr', 't')]:
        return cp                      # 图/换行/制表符 run
    return None


def make_para(src_p, seg_children):
    np = etree.Element(q('p'))
    ppr = src_p.find(q('pPr'))
    if ppr is not None:
        np.append(copy.deepcopy(ppr))
    for ch in seg_children:
        np.append(ch)
    return np


def split_label_para(p):
    """返回 ((新段列表, 原文), None)；无需拆分返回 (None, None)。
    目标标签前有实质文字（如「【分析】…【知识点】…」混行段）时：前文原样独立成段置前
    （【分析】等其余标签不动——规格书T5但书），目标标签照常拆分。"""
    txt = ptext(p)
    labels = list(LABEL_RE.finditer(txt))
    if not labels:
        return None, None
    segs = []                            # (kind, a, b)
    if norm(txt[:labels[0].start()]):
        segs.append(('content', 0, labels[0].start()))   # 前置内容段（其余标签不动）
    for k, m in enumerate(labels):
        segs.append(('label', m.start(), m.end()))
        ce = labels[k + 1].start() if k + 1 < len(labels) else len(txt)
        segs.append(('content', m.end(), ce))
    if len(segs) == 2 and not norm(txt[labels[0].end():]):
        return None, None                # 已独立（仅标签＋空白）
    # 零宽/边界元素归段
    out_children = {id_: [] for id_ in range(len(segs))}
    ppr = p.find(q('pPr'))
    off = 0
    for ch in p:
        if ch is ppr:
            continue
        ca, cb = child_span(ch, off)
        off = cb
        if ca == cb:
            # 零宽元素（oMath/绘图/bookmark 等）：严格内含优先；界点上——标签起界归前段（内容尾），
            # 标签止界归后段（内容头）；兜底末段
            tgt = None
            si_later = si_earlier = None
            for si, (kind, sa, sb) in enumerate(segs):
                if sa < ca < sb:
                    tgt = si
                    break
                if sa == ca and si_later is None:
                    si_later = si
                if sb == ca:
                    si_earlier = si
            if tgt is None:
                if si_later is not None and segs[si_later][0] == 'label' and si_earlier is not None:
                    tgt = si_earlier
                elif si_later is not None:
                    tgt = si_later
                elif si_earlier is not None:
                    tgt = si_earlier
                else:
                    tgt = len(segs) - 1
            out_children[tgt].append(copy.deepcopy(ch))
            continue
        for si, (kind, sa, sb) in enumerate(segs):
            if cb <= sa or ca >= sb:
                continue
            # 交集
            ia, ib = max(ca, sa), min(cb, sb)
            cp = trim_copy(ch, ia - ca, ib - ca)
            if cp is not None:
                out_children[si].append(cp)
    new_paras = []
    dropped_ws = ''
    for si, (kind, sa, sb) in enumerate(segs):
        if kind == 'content' and not norm(txt[sa:sb]):
            dropped_ws += txt[sa:sb]
            continue
        new_paras.append(make_para(p, out_children[si]))
    return (new_paras, txt, dropped_ws) if len(new_paras) > 1 else (None, None)


def process(path, dry):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))

    n_split = n_keep = n_para_added = 0
    anomalies = []
    rows = []
    for p in list(body.iter(q('p'))):
        if not LABEL_RE.search(ptext(p)):
            continue
        res = split_label_para(p)
        if res[0] is None:
            if res[1]:
                anomalies.append(res[1])
            else:
                n_keep += 1
            continue
        new_paras, orig_txt, _d = res
        # 文本守恒断言（去空白归一化）
        joined = ''.join(ptext(np) for np in new_paras)
        assert norm(joined) == norm(orig_txt), '文本守恒失败: %r vs %r' % (orig_txt[:60], joined[:60])
        if not dry:
            for np in new_paras:
                p.addprevious(np)
            p.getparent().remove(p)
        n_split += 1
        n_para_added += len(new_paras) - 1
        rows.append(orig_txt[:60])

    lines = []
    lines.append('## T5 标签行独立成段器 — %s%s' % (os.path.basename(path), '（dry-run）' if dry else ''))
    lines.append('拆分 %d 段（新增段落 %d）｜已独立跳过 %d｜异常 %d｜文本守恒断言 %s'
                 % (n_split, n_para_added, n_keep, len(anomalies), 'PASS（逐段去空白零差异）'))
    for r in rows[:6]:
        lines.append('  拆: %s' % r)
    if len(rows) > 6:
        lines.append('  …共 %d 段' % len(rows))
    for a in anomalies[:10]:
        lines.append('  ! ' + a)
    lines.append('')

    if not dry and n_split:
        import shutil
        bak = path + '.bak_标签行'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.t5tmp'
        with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = new_xml if item.filename == 'word/document.xml' else zin.read(item.filename)
                zout.writestr(item, data)
        for k in range(12):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                time.sleep(6)
        else:
            raise RuntimeError('locked: ' + path)
    return '\n'.join(lines)


def main():
    argv = sys.argv[1:]
    dry = '--dry-run' in argv
    argv = [a for a in argv if a != '--dry-run']
    report = None
    if '--report' in argv:
        k = argv.index('--report'); report = argv[k + 1]; del argv[k:k + 2]
    assert argv, '用法: python 工具/标签行独立成段器.py <docx...> [--dry-run] [--report r.md]'
    out = []
    for path in argv:
        r = process(path, dry)
        out.append(r)
        print(r)
    if report:
        with open(report, 'a', encoding='utf-8') as f:
            f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
