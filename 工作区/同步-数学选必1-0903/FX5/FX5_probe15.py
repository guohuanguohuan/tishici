# -*- coding: utf-8 -*-
"""FX5-G probe 15: full inventory of shaded runs in all 【答案】 paras + question stems for context"""
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

def alltext(el):
    out = []
    for c in el.iter():
        if c.tag == f'{{{W}}}t' and c.text is not None:
            out.append(c.text)
        elif c.tag == f'{{{M}}}t' and c.text is not None:
            out.append(c.text)
    return ''.join(out)

print('=== ALL answer-line shaded runs with markup ===')
ans_idx = []
for i, p in enumerate(paras):
    ft = alltext(p)
    if '【答案】' not in ft:
        continue
    ans_idx.append(i)
    seq = []
    for child in p:
        tag = child.tag.split('}')[1]
        if tag == 'r':
            t = ''.join(c.text or '' for c in child.findall(f'{{{W}}}t'))
            seq.append((('S' if run_shaded(child) else 'r'), t))
        elif tag == 'oMath':
            n_shd = len(child.findall(f'.//{{{W}}}shd'))
            seq.append(('M' + ('s' if n_shd else '-'), alltext(child)))
    # compact: mark shaded spans
    parts = []
    for k, t in seq:
        if k == 'S':
            parts.append('⟨' + t + '⟩')
        elif k == 'Ms':
            parts.append('⟪' + t + '⟫')
        else:
            parts.append(t)
    compact = ''.join(parts)
    # only print if any ⟨⟩ span contains CJK narrative or trailing punct
    spans = re.findall(r'⟨([^⟨]*)⟩', compact)
    interesting = any(re.search(r'[，。；、]|[\u4e00-\u9fff]|\.$|．$|．|，', s) for s in spans)
    if interesting:
        print(f'p#{i}: {compact[:200]}')

print('\n=== question stems for p#9,140,182,392,447 ===')
for target in (9, 140, 182, 392, 447):
    # walk back to find the question number para (starts with 2.x pattern)
    for j in range(target, max(0, target - 15), -1):
        t = alltext(paras[j])
        if re.match(r'^\s*2\.\d[\d.]*-\d+．', t):
            print(f'  p#{target} question (p#{j}): {t[:130]!r}')
            break
