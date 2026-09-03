# -*- coding: utf-8 -*-
"""FX5-G probe 14: 灰底越界 scan — C9C9C9 shading on 【答案】 lines extending beyond value"""
import re
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

tree = etree.parse(DOC)
body = tree.getroot().find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

def run_shaded(r):
    rPr = r.find(f'{{{W}}}rPr')
    if rPr is None:
        return False
    shd = rPr.find(f'{{{W}}}shd')
    return shd is not None and shd.get(f'{{{W}}}fill') == 'C9C9C9'

flagged = 0
for i, p in enumerate(paras):
    # full text
    def alltext(el):
        out = []
        for c in el.iter():
            if c.tag == f'{{{W}}}t' and c.text is not None:
                out.append(c.text)
            elif c.tag == f'{{{M}}}t' and c.text is not None:
                out.append(c.text)
        return ''.join(out)
    ft = alltext(p)
    if '【答案】' not in ft:
        continue
    # walk runs: shaded runs and their text
    seq = []
    for child in p:
        tag = child.tag.split('}')[1]
        if tag == 'r':
            t = ''.join(c.text or '' for c in child.findall(f'{{{W}}}t'))
            seq.append(('R' if run_shaded(child) else 'r', t))
        elif tag == 'oMath':
            # does the oMath contain shd?
            n_shd = len(child.findall(f'.//{{{W}}}shd'))
            seq.append(('MATH' + (f'({n_shd}shd)' if n_shd else ''), alltext(child)))
        elif tag == 'oMathPara':
            n_shd = len(child.findall(f'.//{{{W}}}shd'))
            seq.append(('MP' + (f'({n_shd}shd)' if n_shd else ''), alltext(child)))
    # heuristic flags: shaded text containing separator/narrative
    issues = []
    for kind, t in seq:
        if kind == 'R' and t:
            # shaded run containing full-width ；or 。or narrative CN words
            if '；' in t or '。' in t or '，' in t:
                issues.append(('punct-in-shade', t))
            # shaded run that is pure narrative (CJK len>4 no digits/letters/math)
    # also print compact for review
    compact = ''.join(('<S>' + t + '</S>' if k == 'R' and t else (k if k.startswith(('MATH', 'MP')) else t)) for k, t in seq)
    if any(k == 'R' and t for k, t in seq) or any(k.startswith('MATH(') or k.startswith('MP(') for k, t in seq):
        if issues:
            flagged += 1
            print(f'p#{i} FLAG {issues} :: {compact[:170]}')
        else:
            # print first few for eyeball
            pass

# Dump a sample of 12 answer lines with shading markup for eyeball review
print('\n=== sample answer lines with shading markup ===')
n = 0
for i, p in enumerate(paras):
    def alltext(el):
        out = []
        for c in el.iter():
            if c.tag == f'{{{W}}}t' and c.text is not None:
                out.append(c.text)
            elif c.tag == f'{{{M}}}t' and c.text is not None:
                out.append(c.text)
        return ''.join(out)
    ft = alltext(p)
    if '【答案】' not in ft:
        continue
    seq = []
    for child in p:
        tag = child.tag.split('}')[1]
        if tag == 'r':
            t = ''.join(c.text or '' for c in child.findall(f'{{{W}}}t'))
            seq.append(('S' if run_shaded(child) else 'r', t))
        elif tag == 'oMath':
            n_shd = len(child.findall(f'.//{{{W}}}shd'))
            seq.append(('M' + ('s' if n_shd else '-'), alltext(child)))
    compact = ''.join((f'⟨{k}:{t}⟩' if k in ('S', 'Ms', 'M-') else t) for k, t in seq)
    n += 1
    print(f'  p#{i}: {compact[:150]}')
    if n >= 30:
        break
