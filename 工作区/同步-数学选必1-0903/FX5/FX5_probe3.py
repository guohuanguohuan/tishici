# -*- coding: utf-8 -*-
"""FX5-G probe 3: PRECISE run-level tab census (parent=w:r only), nbsp option separators,
p#516 context, tab-para run detail"""
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
        if node.tag == f'{{{W}}}t' and node.text:
            out.append(node.text)
        elif node.tag == f'{{{M}}}t' and node.text:
            out.append('⟦M:' + node.text + '⟧')
        elif node.tag == f'{{{W}}}tab' and node.getparent().tag == f'{{{W}}}r':
            out.append('⟦TAB⟧')
        elif node.tag == f'{{{W}}}br':
            out.append('⟦BR⟧')
    return ''.join(out)

# PRECISE run-level tabs
total = 0
hits = []
for i, p in enumerate(paras):
    cnt = 0
    for r in p.findall(f'{{{W}}}r'):
        cnt += len(r.findall(f'{{{W}}}tab'))
    if cnt:
        total += cnt
        hits.append((i, cnt, ptext(p)))
print('TRUE run-level tabs:', total, 'in', len(hits), 'paras')

lead = 0; sep = 0; other = []
for i, cnt, t in hits:
    # classify: leading tabs (at very start of text) vs separators
    nlead = 0
    pos = 0
    while t.startswith('⟦TAB⟧', pos):
        nlead += 1
        pos += 6
    sep += cnt - nlead
    lead += nlead
    if not (t.rstrip().endswith(('。','？','！','；','：')) or 'A．' in t or 'A.' in t):
        other.append((i, t))
print('leading-indent tabs:', lead, '| inter-option tabs:', sep)
print('non-option paras with tabs:', [(i, t[:80]) for i, t in other])

# p#516 full text
print('\n=== p#516 full ===')
print(ptext(paras[516]))

# nbsp separators in option lines: find paras with A． and nbsp between options
print('\n=== option paras with nbsp runs (nbsp NOT in （　）answer slots) ===')
for i, p in enumerate(paras):
    t = ptext(p)
    if 'A．' not in t: continue
    # nbsp sequences of >=2 in option area
    import re
    runs_txt = []
    for r in p.findall(f'{{{W}}}r'):
        for tn in r.findall(f'{{{W}}}t'):
            if tn.text:
                runs_txt.append(tn.text)
    joined = ''.join(runs_txt)
    ms = re.findall(r'[\xa0]{2,}', joined)
    if ms:
        print(f'  p#{i}: nbsp-runs {[len(x) for x in ms]}: {t[:160]!r}')
