# -*- coding: utf-8 -*-
r"""题型名前缀去除器.py — 2026-09-05 选必1成书修复路线·版式修订轮②·T4（工具先建后用）

口径（规格书T4）：题型标题「题型序号 教材节标题：具体题型（来源括注）」→「题型序号 具体题型（来源括注）」；
  保留来源括注；只动题型标题段。
识别三要件（全部满足才动）：①父链续层编号起段（^\d+(\.\d+)+\s，深度≥3 级——2级为节标题层）；
  ②全角冒号前缀恰为当前教材节标题名（节名取自最近节标题段文字去统计段；位置归属口径）；
  ③段级底纹 C6D4E3（T6b 撤底纹后为左侧竖条 w:pBdr/w:left——两形兼容，幂等重跑安全）。
  讲部标题「N.N.N.k 知识讲解｜…」无全角冒号，天然排除；节名不符者原样保留并登记。
  衔接件题型标题同法处置；知识清单件无题型标题（0 处置登记）。
断言：改写仅限「节名：」前缀 span（零意外字符逐段比对）；改写数＋不符登记数＝题型标题总数；
      幂等（二跑改写 0）。
模式：默认就地改写（留 .bak_题型名）；--dry-run 列全部改写前后对照，不落盘。
用法:
  python 工具/题型名前缀去除器.py <docx...> [--dry-run] [--report r.md]
"""
import sys, io, os, re, zipfile, time
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def pfill(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    sh = ppr.find(q('shd'))
    return sh.get(q('fill')) if sh is not None else None
def has_left_bar(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return False
    pb = ppr.find(q('pBdr'))
    return pb is not None and pb.find(q('left')) is not None

SEC_TTL_RE = re.compile(r'^(\d+\.\d+(?:\.\d+)?)[\s　]+\S')
GRP_TTL_RE = re.compile(r'^(\d+(?:\.\d+)+)([\s　]+)(\S)')
LECT_RE = re.compile(r'^\d+(?:\.\d+)*\s*(?:方法讲解|知识讲解)[｜|]')
STATS_MARK_RE = re.compile(r'　(?:本节)?\d+题[:：]?')
GRP_STANDALONE_RE = re.compile(r'^\d+题：')


def wt_nodes(p):
    return [t for t in p.iter(q('t'))]


def del_span(p, a, b):
    off = 0
    removed = ''
    for r in list(p.findall(q('r'))):
        ts = r.findall(q('t'))
        if not ts:
            continue
        txt = ''.join(t.text or '' for t in ts)
        ra, rb = off, off + len(txt)
        off = rb
        if rb <= a or ra >= b:
            continue
        cs, ce = max(a - ra, 0), min(b - ra, len(txt))
        removed += txt[cs:ce]
        keep = txt[:cs] + txt[ce:]
        ts[0].text = keep
        ts[0].set(XMLSPACE, 'preserve')
        for t in ts[1:]:
            t.text = ''
        if not keep and not [c for c in r if etree.QName(c).localname not in ('rPr', 't')]:
            p.remove(r)
    return removed


def sec_name_of(title_txt):
    """节标题文字 → 节名（去序号与行末统计段）。"""
    t = STATS_MARK_RE.split(title_txt)[0]
    m = re.match(r'^\d+\.\d+(?:\.\d+)?[\s　]+', t)
    return t[m.end():].strip() if m else t.strip()


def process(path, dry):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    els = list(body)

    n_rew = n_skip_done = 0
    mismatch = []
    rows = []
    cur_sec_name = None
    for i, c in enumerate(els):
        if c.tag != q('p'):
            continue
        txt = ptext(c)
        if pfill(c) == 'ADC2DA' and SEC_TTL_RE.match(txt):
            cur_sec_name = sec_name_of(txt)
            continue
        gm = GRP_TTL_RE.match(txt)
        if not gm or LECT_RE.match(txt):
            continue
        if gm.group(1).count('.') < 2:
            continue                      # 2级编号＝节标题层，非题型标题
        is_grp_title = (pfill(c) == 'C6D4E3') or has_left_bar(c)
        if not is_grp_title:
            continue
        # 题型标题本体（去行末统计段；T3 后形态标题行本无统计段）
        body_txt = STATS_MARK_RE.split(txt)[0]
        name_start = gm.start(3)
        if '：' not in body_txt[gm.end(1):]:
            n_skip_done += 1           # 已无「节名：」前缀（幂等/本无）
            continue
        prefix = body_txt[gm.end(1):].lstrip(' 　')
        colon_at = prefix.find('：')
        cand = prefix[:colon_at]
        if cur_sec_name is not None and cand == cur_sec_name:
            # 删除 span：[具体题型名起点 − (节名＋全角冒号) 长, 具体题型名起点)
            stripped_body = txt[:len(txt) - len(txt.lstrip())]
            tgt_start = txt.find('：', name_start) + 1
            src_start = tgt_start - (len(cand) + 1)
            removed = del_span(c, src_start, tgt_start)
            assert removed == cand + '：', '前缀删除文本不符: %r' % removed
            n_rew += 1
            rows.append((gm.group(1), txt[:56], ptext(c)[:56]))
        else:
            mismatch.append('题型%s 冒号前缀「%s」≠ 当前节名「%s」（原样保留）'
                            % (gm.group(1), cand[:20], (cur_sec_name or '?')[:20]))

    lines = []
    lines.append('## T4 题型名前缀去除器 — %s%s' % (os.path.basename(path), '（dry-run）' if dry else ''))
    lines.append('改写 %d｜已无前缀/幂等 %d｜节名不符保留 %d' % (n_rew, n_skip_done, len(mismatch)))
    for a, b, c_ in rows[:10]:
        lines.append('  %s｜%s ⇒ %s' % (a, b, c_))
    if len(rows) > 10:
        lines.append('  …共 %d 处改写对照' % len(rows))
    for mrec in mismatch[:10]:
        lines.append('  ! ' + mrec)
    lines.append('')

    if not dry and n_rew:
        import shutil
        bak = path + '.bak_题型名'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.t4tmp'
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
    assert argv, '用法: python 工具/题型名前缀去除器.py <docx...> [--dry-run] [--report r.md]'
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
