# -*- coding: utf-8 -*-
"""OMML 语义提取器：遍历截断 docx 中所有 m:oMath，输出结构化"真值"伪 TeX（供保真对比基准）。
同时从 sec.tex 按顺序抽取 pandoc 转出的 TeX，按出现顺序对齐，输出对照表 formulas.json。"""
import json
import re
from docx import Document
from docx.oxml.ns import qn

M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
DOC = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v2-latex\1.1.1-源节.docx"
TEX = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v2-latex\sec.tex"
OUT = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v2-latex\formulas.json"

def t_of(el):
    """取 m:t 文本（该元素直接文本内容拼接）"""
    return ''.join(t.text or '' for t in el.iter(M + 't'))

def omml_to_pseudo(el):
    """递归把 OMML 元素转成伪 TeX（真值语义）"""
    tag = el.tag
    if tag == M + 'oMath' or tag == M + 'oMathPara' or tag == M + 'e' or tag == M + 'oMathParaPr':
        return join_children(el)
    if tag == M + 'r':
        return t_of(el)
    if tag == M + 'f':  # 分数
        num = child(el, 'num'); den = child(el, 'den')
        return r'\frac{' + conv(num) + r'}{' + conv(den) + r'}'
    if tag == M + 'sSup':
        return '{' + conv(child(el, 'e')) + '}^{' + conv(child(el, 'sup')) + '}'
    if tag == M + 'sSub':
        return '{' + conv(child(el, 'e')) + '}_{' + conv(child(el, 'sub')) + '}'
    if tag == M + 'sSubSup':
        return '{' + conv(child(el, 'e')) + '}_{' + conv(child(el, 'sub')) + '}^{' + conv(child(el, 'sup')) + '}'
    if tag == M + 'd':  # 定界符
        dPr = el.find(M + 'dPr')
        beg, end, sep = '(', ')', '|'
        if dPr is not None:
            b = dPr.find(M + 'begChr'); e = dPr.find(M + 'endChr')
            s = dPr.find(M + 'sepChr')
            if b is not None: beg = b.get(M + 'val') or ''
            if e is not None: end = e.get(M + 'val') or ''
            if s is not None: sep = s.get(M + 'val') or ''
        parts = [conv(c) for c in el.findall(M + 'e')]
        inner = (' ' + sep + ' ').join(parts) if len(parts) > 1 else (parts[0] if parts else '')
        return r'\left' + beg + inner + r'\right' + end
    if tag == M + 'rad':  # 根式
        deg = child(el, 'deg'); e = child(el, 'e')
        if deg is not None and conv(deg).strip():
            return r'\sqrt[' + conv(deg) + ']{' + conv(e) + '}'
        return r'\sqrt{' + conv(e) + '}'
    if tag == M + 'acc':  # 重音（向量箭头等）
        base = conv(child(el, 'e'))
        dPr = el.find(M + 'accPr')
        chr_el = dPr.find(M + 'chr') if dPr is not None else None
        c = chr_el.get(M + 'val') if chr_el is not None else '⃞'
        return r'\ACC{' + repr(c) + '}{' + base + '}'
    if tag == M + 'bar':
        pos = el.find(M + 'barPr') if el.find(M + 'barPr') is not None else None
        cmd = r'\underline' if (pos is not None and pos.find(M + 'pos') is not None
                                and pos.find(M + 'pos').get(M + 'val') == 'bot') else r'\overline'
        return cmd + '{' + conv(child(el, 'e')) + '}'
    if tag == M + 'eqArr':  # 方程组/分段
        rows = [conv(e) for e in el.findall(M + 'e')]
        return r'\CASES{' + r' \\ '.join(rows) + '}'
    if tag == M + 'm':  # 矩阵
        rows = []
        for mr in el.findall(M + 'mr'):
            rows.append(' & '.join(conv(e) for e in mr.findall(M + 'e')))
        return r'\MATRIX[' + r' \\ '.join(rows) + ']'
    if tag == M + 'nary':
        nPr = el.find(M + 'naryPr')
        chr_el = nPr.find(M + 'chr') if nPr is not None else None
        c = chr_el.get(M + 'val') if chr_el is not None else '∫'
        sub = conv(child(el, 'sub')); sup = conv(child(el, 'sup'))
        return r'\NARY{' + c + '}{' + sub + '}{' + sup + '}{' + conv(child(el, 'e')) + '}'
    if tag == M + 'limLow':
        return conv(child(el, 'e')) + r'_{\text{lim}}{' + conv(child(el, 'lim')) + '}'
    if tag == M + 'limUpp':
        return conv(child(el, 'e')) + r'^{\text{lim}}{' + conv(child(el, 'lim')) + '}'
    if tag == M + 'func':
        return conv(child(el, 'fName')) + '(' + conv(child(el, 'e')) + ')'
    if tag == M + 'box' or tag == M + 'groupChr' or tag == M + 'borderBox':
        return conv(child(el, 'e'))
    # 兜底
    inner = join_children(el)
    return inner

def child(el, name):
    return el.find(M + name)

def join_children(el):
    return ''.join(omml_to_pseudo(c) for c in el if isinstance(c.tag, str))

def conv(el):
    if el is None:
        return ''
    return omml_to_pseudo(el)

# ---- 遍历 docx ----
doc = Document(DOC)
omath_list = []
for pel in doc.element.body.iter(qn('w:p')):
    for om in pel.iter(M + 'oMath'):
        pseudo = conv(om)
        plain = t_of(om)
        ctx = ''.join(t.text or '' for t in pel.iter() if t.tag == qn('w:t'))[:28]
        omath_list.append({'i': len(omath_list), 'ctx': ctx, 'plain': plain, 'truth': pseudo})

# ---- 从 sec.tex 抽 pandoc 数学（按顺序）----
tex = open(TEX, encoding='utf-8').read()
pandoc_math = []
for mch in re.finditer(r'\\\((.+?)\\\)', tex, re.S):
    pandoc_math.append(mch.group(1).strip())

print(f'docx OMML 公式数: {len(omath_list)}')
print(f'tex 数学片段数: {len(pandoc_math)}')

data = {'omml': omath_list, 'pandoc': pandoc_math}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print('已写', OUT)

# 打印全部真值（前 100 条）供人工挑选
for o in omath_list:
    print(f"[{o['i']:03d}] ctx={o['ctx']!r}")
    print(f"      truth: {o['truth'][:160]}")
