# -*- coding: utf-8 -*-
r"""创作句线性数学签名.py — 2026-09-02 A''成品轮新建（公共规则§7排版自检⑥「创作句零线性数学」＋看板A''增补
「通式句/正文线性数学全量公式化231条（创作句131优先）」）。

识别与转换：
  · 签名＝普通 w:t 文本中的「线性数学连缀」——Unicode 数学符（√ ² ³ ¹ ⁿ ₀-₉ ± × ÷ ≤ ≥ ≠ ∈
    ∉ ∞ ∝ ∠ ⊥ ∥ ∧ ∨ ∪ ∩ ⊂ ⊆ ≌ ∽ ≈）与邻接字母/数字/括号/运算符构成的表达式片段
    （≥2字符的连缀；单孤字符不转——叙述性标点不算）；上下标字符（²³¹ⁿ₀-₉）与字母连缀（x²、a₁）
    为强签名（≥2字符即转）。
  · 转换＝整片段塞 m:oMath > m:r > m:t（文本直迁——「√塞m:t文本（√6无上划线可接受）」先例；
    rPr 按 OMML 默认 Cambria Math，不挂底纹不挂色）；片段从原 w:t 中切出，前后文字保留原 run。
  · 优先级：--priority creation 只处理创作句段（题型通式句【编注】起段＋〔基〕/〔进〕图例行）；
    --priority all 处理全部正文段（看板「正文线性数学」口径——含题干/详解中的线性数学残留）。
  · 幂等：已是 m:t 内容不碰；零文字增删断言（切出迁入不增删字符——w:t流与m:t流拼接恒等）。

用法: python 创作句线性数学签名.py <docx...> [--report r.txt] [--dry-run] [--priority creation|all]
"""
import sys, io, zipfile, os, re, time, argparse
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def mq(t): return '{%s}%s' % (M, t)
def tag(e): return etree.QName(e).localname if isinstance(e.tag, str) else '?'

SUPS = '²³¹ⁿ'
SUBS = '₀₁₂₃₄₅₆₇₈₉'
MATHCH = '√±×÷≤≥≠∈∉∞∝∠⊥∥∧∨∪∩⊂⊆≌∽≈' + SUPS + SUBS
# 强签名：上下标与字母/数字连缀
STRONG = re.compile(r'[A-Za-z0-9a-z][%s]|[%s][A-Za-z0-9]' % (re.escape(SUPS + SUBS), re.escape(SUPS + SUBS)))
# 一般连缀：数学符与字母/数字/括号/运算/数学符 相邻构成的片段
PIECE = re.compile(r'[A-Za-z0-9()\[\]{}.,+\-−=<>%s]{1,}(?:[%s][A-Za-z0-9()\[\]{}.,+\-−=<>%s]{1,})+'
                   % (re.escape(MATHCH), re.escape(MATHCH), re.escape(MATHCH)))
# 创作句段判定
CREA_HEAD = re.compile(r'^【编注】|^〔基〕|^〔进〕')


def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def make_omath(text):
    om = etree.Element(mq('oMath'))
    mr = etree.SubElement(om, mq('r'))
    mt = etree.SubElement(mr, mq('t'))
    mt.text = text
    return om


def convert_para(p, stats):
    """段内线性数学→oMath（只处理 w:r 直接子级的 w:t；返回处理片段数）。"""
    n = 0
    for r in list(p.findall(q('r'))):
        ts = r.findall(q('t'))
        if not ts:
            continue
        for t in ts:
            s = t.text or ''
            if not s:
                continue
            # 找候选片段（强签名片段优先；一般连缀次之）
            cands = []
            for m in STRONG.finditer(s):
                cands.append((m.start(), m.end()))
            for m in PIECE.finditer(s):
                cands.append((m.start(), m.end()))
            # 合并重叠区间
            cands.sort()
            merged = []
            for a, b in cands:
                if merged and a <= merged[-1][1]:
                    merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
                else:
                    merged.append((a, b))
            # 过滤：纯数字/纯字母/单字符不转；含数学符或上下标才转
            def keep(seg):
                if len(seg) < 2:
                    return False
                return any(c in MATHCH for c in seg)
            merged = [(a, b) for a, b in merged if keep(s[a:b])]
            if not merged:
                continue
            # 重建：原run按片段切分——文本片段保留，数学片段转oMath（插到run后）
            prev_end = 0
            new_children = []          # (kind, content)
            for a, b in merged:
                if a > prev_end:
                    new_children.append(('txt', s[prev_end:a]))
                new_children.append(('math', s[a:b]))
                prev_end = b
            if prev_end < len(s):
                new_children.append(('txt', s[prev_end:]))
            # 原t清空第一段txt；其余逐个新建run/omath插原run之后
            rpr = r.find(q('rPr'))
            rpr_bytes = etree.tostring(rpr) if rpr is not None else None
            first_txt = next((c for k, c in new_children if k == 'txt'), None)
            t.text = ''
            anchor_after = t
            first_done = False
            for kind, content in new_children:
                if kind == 'txt' and not first_done:
                    t.text = content
                    t.set(XMLSPACE, 'preserve')
                    first_done = True
                    continue
                if kind == 'txt':
                    nr = etree.Element(q('r'))
                    if rpr_bytes is not None:
                        nr.append(etree.fromstring(rpr_bytes))
                    nt = etree.SubElement(nr, q('t'))
                    nt.text = content
                    nt.set(XMLSPACE, 'preserve')
                    anchor_after.addnext(nr)
                    anchor_after = nr
                else:
                    om = make_omath(content)
                    anchor_after.addnext(om)
                    anchor_after = om
                    n += 1
                    stats['片段→oMath'] += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--report')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--priority', choices=['creation', 'all'], default='creation')
    args = ap.parse_args()
    out = []
    for path in args.files:
        z = zipfile.ZipFile(path)
        parts = {n: z.read(n) for n in z.namelist()}
        z.close()
        doc = etree.fromstring(parts['word/document.xml'])
        body = doc.find(q('body'))
        # 文字流断言基线（w:t + m:t 全拼接）
        flow_before = [t.text or '' for t in doc.iter(q('t'))] + \
                      [t.text or '' for t in doc.iter(mq('t'))]
        stats = Counter()
        for p in body.iter(q('p')):
            line = para_text(p)
            if args.priority == 'creation' and not CREA_HEAD.match(line.strip()):
                continue
            convert_para(p, stats)
        flow_after = [t.text or '' for t in doc.iter(q('t'))] + \
                     [t.text or '' for t in doc.iter(mq('t'))]
        assert sorted(''.join(flow_before)) == sorted(''.join(flow_after)), \
            '%s 字符流不恒等（线性数学转换增删字符）' % path
        out.append('◆ %s（%s）' % (os.path.basename(path), args.priority))
        out.append('  线性数学→oMath：%d 片段%s' % (stats['片段→oMath'],
                                                '，dry-run 未写回' if args.dry_run else ''))
        if not args.dry_run:
            parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True,
                                                        encoding='UTF-8', standalone=True)
            tmp = path + '.a2lin'
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
