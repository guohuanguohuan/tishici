# -*- coding: utf-8 -*-
"""FX5-G probe 2: tab census (run-level vs pPr defs), sz21 runs, bianzhu linear math (w:t layer)"""
import re
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

tree = etree.parse(DOC)
root = tree.getroot()
body = root.find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

def ptext(p):
    out = []
    for node in p.iter():
        t = node.tag.split('}')[1] if '}' in node.tag else node.tag
        if node.tag == f'{{{W}}}t' and node.text:
            out.append(node.text)
        elif node.tag == f'{{{M}}}t' and node.text:
            out.append('⟦M:' + node.text + '⟧')
        elif node.tag == f'{{{W}}}tab':
            out.append('⟦TAB⟧')
    return ''.join(out)

# --- 1. run-level w:tab census ---
print('=== RUN-LEVEL w:tab census ===')
run_tabs = 0
tab_paras = []
for i, p in enumerate(paras):
    # w:tab as direct child of w:r (run-level tab char). Exclude w:tabs (pPr) definitions.
    tabs = [t for t in p.iter(f'{{{W}}}tab')]
    if tabs:
        run_tabs += len(tabs)
        tab_paras.append((i, len(tabs), ptext(p)))
print('run-level w:tab total:', run_tabs, 'in', len(tab_paras), 'paras')
for i, n, t in tab_paras:
    print(f'  p#{i} ({n} tabs): {t[:150]!r}')

# --- 2. pPr w:tabs definitions ---
print('\n=== pPr w:tabs (docking definitions) ===')
ppr_tabs = 0
ppr_tab_paras = 0
for i, p in enumerate(paras):
    pPr = p.find(f'{{{W}}}pPr')
    if pPr is not None:
        tw = pPr.find(f'{{{W}}}tabs')
        if tw is not None:
            cnt = len(tw.findall(f'{{{W}}}tab'))
            ppr_tabs += cnt
            ppr_tab_paras += 1
print('pPr w:tabs/w:tab total:', ppr_tabs, 'in', ppr_tab_paras, 'paras')

# --- 3. sz=21 runs ---
print('\n=== sz/szCs=21 runs ===')
sz21 = []
for i, p in enumerate(paras):
    for r in p.findall(f'{{{W}}}r'):
        rPr = r.find(f'{{{W}}}rPr')
        if rPr is None: continue
        sz = rPr.find(f'{{{W}}}sz')
        szCs = rPr.find(f'{{{W}}}szCs')
        hit = False
        for el in (sz, szCs):
            if el is not None and el.get(f'{{{W}}}val') == '21':
                hit = True
        if hit:
            # what does the run contain?
            contents = [c.tag.split('}')[1] for c in r]
            txt = ''.join(r.itertext())
            sz21.append((i, contents, txt[:30]))
print('sz21 runs:', len(sz21))
from collections import Counter
cc = Counter(tuple(sorted(set(c for c in contents))) for _, contents, _ in sz21)
for k, v in cc.items():
    print('  content pattern', k, ':', v)

# --- 4. 【编注】 paragraphs with linear math in w:t layer ---
print('\n=== 【编注】 paras, w:t-layer linear math ===')
lin_chars = re.compile(r'[√²³⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉∠⊥∈∩∪≈≤≥≠±·×]|(?:\^)')
for i, p in enumerate(paras):
    full = ptext(p)
    if '【编注】' not in full: continue
    # w:t only
    wt = ''.join(t.text or '' for t in p.iter(f'{{{W}}}t'))
    if lin_chars.search(wt):
        print(f'  p#{i}: WT-LAYER HIT: {wt[:200]!r}')
