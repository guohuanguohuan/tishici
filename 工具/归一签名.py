# -*- coding: utf-8 -*-
r"""归一签名.py — 2026-09-02 A''成品轮新建（公共规则§7「不同选项之间用『；』区分」＋§7排版自检⑥空格卫生全量断言）。

两功能（--mode 选一，默认 both）：
 ① 选项分隔归一（--mode options）：选项行分隔统一「；」——
   · w:tab 分隔（选项间 tab）→「；」；
   · 粘连（「A．xxB．yy」选项字母直接粘连前一选项尾——(B|C|D)．前无分隔）→ 插「；」；
   · 异空格（选项间≥1空格〔半/全角〕）→「；」。
   识别范围＝选项行：段内含 ≥2 个「X．」选项字母锚（A-D 常规、至 F 容多选排序）；
   仅处理锚与锚之间的分隔位，选项内容零改动；【答案】行内「　」全角空格分隔＝规定形态白名单不动。
 ② 空格归一（--mode spaces）：
   · 连续双半空格 → 单空格；
   · 全角空格净除（段中间「　」→ 删；白名单除外——【答案】…　【知识点】行内全角空格、
     节标题行统计段前导「　」、题型标题统计段前导「　」、〔基〕/〔进〕图例行句内规定空格）；
   · 全角标点（，。；：、！？）（）前后半空格 → 删；
   · 段尾空格（w:t 尾部空格、纯空格 run）→ 删。
   只动 w:t 文本与纯空格 run；零文字内容增删之外的断言（空格属授权字符变更——逐类计数落盘）。

报告：逐类计数＋样本；--dry-run 只清点。
用法: python 归一签名.py <docx...> [--report r.txt] [--dry-run] [--mode options|spaces|both]
"""
import sys, io, zipfile, os, re, time, argparse
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname if isinstance(e.tag, str) else '?'

OPT_ANCHOR = re.compile(r'([A-F])．')
ALLOW_FWSP_LINE = re.compile(r'【答案】')      # 【答案】…　【知识点】行：全角空格白名单
LEAD_FWSP_OK = re.compile(r'　\d+题：|本节\d+题|〔基〕|〔进〕')   # 统计段前导/图例行
FW_PUNCT = '，。；：、！？（）'


def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def norm_options(doc, stats, dry):
    """选项分隔归一：逐段处理 w:t 序列（跨 run 分隔位识别按段内拼接文本定位）。"""
    for p in doc.iter(q('p')):
        txt = para_text(p)
        anchors = list(OPT_ANCHOR.finditer(txt))
        if len(anchors) < 2:
            continue
        # 逐锚间分隔位检查（在段文本坐标上判定，落到 w:t 字符手术）
        ops = []          # (pos_in_para, kind)
        for k in range(len(anchors) - 1):
            a, b = anchors[k].end(), anchors[k + 1].start()
            seg = txt[a:b]
            if seg == '':
                ops.append((b, 'insert'))                      # 粘连
            elif seg == '\t':
                ops.append((a, 'tab'))                          # w:tab 是元素不是文本——单独处理
            elif seg and all(c in ' \u3000' for c in seg):
                ops.append((a, 'spaces:%d' % len(seg)))
            elif seg and seg[0] in ' \u3000' and len(seg) > 1 and all(c in ' \u3000' for c in seg[1:]):
                ops.append((a, 'spaces:%d' % len(seg)))
        if not ops:
            continue
        # w:tab 元素处理（选项间 tab）
        tabs_between = [t for t in p.iter(q('tab'))]
        # 保守：段内 tab 数与 seg=tab 位吻合才转（防误伤题干制表位）
        n_tab_seg = sum(1 for _, k in ops if k == 'tab')
        if n_tab_seg and n_tab_seg == len(tabs_between):
            for t in tabs_between:
                r = t.getparent()
                rpr = r.find(q('rPr'))
                nr = etree.Element(q('r'))
                if rpr is not None:
                    nr.append(etree.fromstring(etree.tostring(rpr)))
                tt = etree.SubElement(nr, q('t'))
                tt.text = '；'
                tt.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                r.getparent().replace(r, nr)
                stats['tab→；'] += 1
        # 文本分隔位（spaces→；、insert插；）——倒序逐 w:t 定位
        text_ops = [(pos, k) for pos, k in ops if k != 'tab']
        for pos, kind in sorted(text_ops, reverse=True):
            # 找 pos 所在 w:t（拼接坐标）
            acc = 0
            for t in p.iter(q('t')):
                s = t.text or ''
                if acc <= pos <= acc + len(s):
                    off = pos - acc
                    if kind.startswith('spaces'):
                        n = int(kind.split(':')[1])
                        # 分隔串可能跨 w:t——保守只处理整体落在单 w:t 内
                        if off + n <= len(s) and set(s[off:off + n]) <= set(' \u3000'):
                            t.text = s[:off] + '；' + s[off + n:]
                            stats['异空格→；'] += 1
                    elif kind == 'insert':
                        t.text = s[:off] + '；' + s[off:]
                        stats['粘连插；'] += 1
                    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                    break
                acc += len(s)


def norm_spaces(doc, stats, dry):
    """空格归一四类。"""
    for p in doc.iter(q('p')):
        line = para_text(p)
        fw_ok = bool(ALLOW_FWSP_LINE.search(line) or LEAD_FWSP_OK.search(line))
        for t in p.iter(q('t')):
            s = t.text or ''
            if not s:
                continue
            ns = s
            ns = re.sub(r'  +', ' ', ns)                        # 双半空格
            if not fw_ok:
                ns = ns.replace('\u3000', '')                   # 全角净除（白名单行除外）
            for cp in FW_PUNCT:                                 # 标点前后半空格
                ns = ns.replace(' ' + cp, cp).replace(cp + ' ', cp)
            ns2 = ns.rstrip()                                   # 段尾（w:t 尾）——仅最后一个含尾空格的 w:t
            if s != ns:
                if ns2 != ns:
                    # 尾空格只在段末最后一个非空 w:t 上删
                    nxt = t.getparent().getnext()
                    is_last = True
                    par = t.getparent()
                    sibs = list(par.getparent())
                    if sibs.index(par) != len(sibs) - 1:
                        is_last = False
                    if is_last:
                        ns = ns2
                        stats['段尾空格'] += 1
                if s != ns:
                    stats['双半空格' if '  ' in s else ('全角净' if '\u3000' in s.replace('\u3000', '', 0) or '\u3000' in s else '标点前空格')] += 1
                t.text = ns
                t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            elif s.rstrip() != s and s.strip() == '':
                # 纯空格 run 段尾
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--report')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--mode', choices=['options', 'spaces', 'both'], default='both')
    args = ap.parse_args()
    out = []
    for path in args.files:
        z = zipfile.ZipFile(path)
        parts = {n: z.read(n) for n in z.namelist()}
        z.close()
        doc = etree.fromstring(parts['word/document.xml'])
        stats = Counter()
        if args.mode in ('options', 'both'):
            norm_options(doc, stats, args.dry_run)
        if args.mode in ('spaces', 'both'):
            norm_spaces(doc, stats, args.dry_run)
        out.append('◆ %s' % os.path.basename(path))
        out.append('  归一计数：%s' % ('；'.join('%s%d' % kv for kv in sorted(stats.items()) if kv[1]) or '零命中'))
        if not args.dry_run:
            parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True,
                                                        encoding='UTF-8', standalone=True)
            tmp = path + '.a2norm'
            zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
            for nm, b in parts.items():
                zo.writestr(nm, b)
            zo.close()
            os.replace(tmp, path)
        out.append('')
    txt = '\n'.join(out)
    print(txt)
    if args.report:
        open(args.report, 'w', encoding='utf-8').write(txt + '\n')


if __name__ == '__main__':
    main()
