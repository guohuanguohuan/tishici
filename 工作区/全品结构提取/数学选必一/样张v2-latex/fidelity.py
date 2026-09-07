# -*- coding: utf-8 -*-
"""保真对比：20 条精选公式 truth vs pandoc 逐对输出 + 全量归一化粗检"""
import json
import re

D = json.load(open(r"C:\提示词\工作区\全品结构提取\数学选必一\样张v2-latex\formulas.json", encoding='utf-8'))
omml, pandoc = D['omml'], D['pandoc']

SEL = [0, 3, 9, 40, 41, 43, 67, 76, 85, 87, 97, 98, 160, 161, 188, 199, 206, 244, 258, 280]

def norm(s):
    s = s.replace(' ', '').replace('\n', '')
    for a, b in [(r'\left', ''), (r'\right', ''), (r'\,', ''), (r'\;', ''), (r'\!', ''),
                 ("\\ACC{'⃑'}", r'\overrightarrow'), ("\\ACC{'⃗'}", r'\overrightarrow'),
                 (r'\overset{⃑}', r'\overrightarrow'),
                 ('⋅', r'\cdot'), ('∙', r'\cdot'), ('×', r'\times'), ('∥', r'\parallel'),
                 ('⟨', r'\langle'), ('〈', r'\langle'), ('⟩', r'\rangle'), ('〉', r'\rangle'),
                 ('°', r'^\circ'), ('∘', r'\circ'), ('≠', r'\neq'), ('≤', r'\leq'), ('≥', r'\geq'),
                 ('∈', r'\in'), ('⊥', r'\bot'), ('∵', r'\because'), ('∴', r'\therefore'),
                 ('−', '-'), ('–', '-'), ('{', ''), ('}', ''), ('π', r'\pi'), ('λ', r'\lambda'),
                 ('μ', r'\mu'), ('α', r'\alpha'), ('β', r'\beta'), ('θ', r'\theta'), ('△', r'\triangle'),
                 (r'\ACC', r'\overrightarrow'), (r'\CASES', 'cases'), (r'\MATRIX', 'matrix'),
                 (r'\NARY', 'nary'), (r'\text{lim}', 'lim'), (r'\frac', 'frac'),
                 (r'\sqrt', 'sqrt'), (r'\angle', 'angle'),
                 (r'\lbrack', '['), (r'\rbrack', ']'),
                 ('cos', r'\cos'), ('sin', r'\sin'), ('tan', r'\tan')]:
        s = s.replace(a, b)
    s = re.sub(r'\\begin\{array\}\{[^}]*\}', 'array', s)
    s = re.sub(r'\\end\{array\}', 'endarray', s)
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    s = re.sub(r'cases\[(.+?)\]', r'\\{\1}', s)
    s = re.sub(r'\\overrightarrow|\\cdot|\\times|\\parallel|\\langle|\\rangle|\\neq|\\leq|\\geq|\\in|\\bot|\\because|\\therefore|\\pi|\\lambda|\\mu|\\alpha|\\beta|\\theta|\\triangle|\\cos|\\sin|\\tan|\\circ|\\cdots', '', s)
    return s

print('=== 20 条精选对比 ===')
for i in SEL:
    t, p = omml[i]['truth'], pandoc[i]
    print(f'--- [{i:03d}] ctx={omml[i]["ctx"][:22]!r}')
    print(f'  truth: {t[:150]}')
    print(f'  pandoc:{p[:150]}')
    print(f'  粗检: {"≈一致" if norm(t) == norm(p) else "需人工判"}')

print()
print('=== 全量 282 归一化粗检 ===')
same = 0
diffs = []
for i in range(min(len(omml), len(pandoc))):
    if norm(omml[i]['truth']) == norm(pandoc[i]):
        same += 1
    else:
        diffs.append(i)
print(f'归一化后完全一致: {same}/{len(omml)}')
print(f'需人工复核: {len(diffs)} 条 -> {diffs[:40]}')
