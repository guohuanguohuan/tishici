# -*- coding: utf-8 -*-
"""FX5-G probe 16: layer-sensitive space hygiene scan (item 7)"""
import re
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

tree = etree.parse(DOC)
body = tree.getroot().find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

def ptext(p):
    out = []
    def walk(el):
        for c in el:
            if c.tag == f'{{{W}}}t' and c.text is not None:
                out.append(('T', c.text))
            elif c.tag == f'{{{M}}}t' and c.text is not None:
                out.append(('M', c.text))
            elif c.tag == f'{{{W}}}drawing':
                out.append(('I', ''))
            elif c.tag == f'{{{W}}}tab' and c.getparent().tag == f'{{{W}}}r':
                out.append(('T', '\t'))
    walk(p)
    return out

FW = '，。；：？！、）》」』'

print('=== 1. double half-space in single w:t ===')
n = 0
for i, p in enumerate(paras):
    for kind, t in ptext(p):
        if kind == 'T' and '  ' in t:
            n += 1
            print(f'  p#{i}: {t[:80]!r}')
print('count:', n)

print('\n=== 2. full-width punct preceded by space (layer-sensitive, w:t only, same-run or prev-T-run boundary) ===')
n = 0
for i, p in enumerate(paras):
    seq = [e for e in ptext(p) if e[0] == 'T']
    # merge adjacent T runs? No — layer boundary between separate w:t runs is a run boundary;
    # space at end of one w:t + FW punct at start of NEXT w:t is still visually adjacent (same para text flow).
    # But math between = separator. So concatenate consecutive T entries (they're adjacent in doc order only if no M/I between).
    j = 0
    events = ptext(p)
    k = 0
    while k < len(events):
        if events[k][0] == 'T':
            buf = ''
            start_k = k
            while k < len(events) and events[k][0] == 'T':
                buf += events[k][1]
                k += 1
            for m in re.finditer(r'[ \xa0\u3000]([，。；：？！、）])', buf):
                n += 1
                ctx = buf[max(0, m.start()-20):m.end()+15]
                print(f'  p#{i}: ...{ctx!r}')
        else:
            k += 1
print('count:', n)

print('\n=== 3. trailing spaces at true para end (last content text) ===')
n = 0
for i, p in enumerate(paras):
    events = ptext(p)
    # find last event with content
    last = None
    for e in events:
        if e[0] == 'T' and e[1]:
            last = ('T', e[1])
        elif e[0] == 'M' and e[1]:
            last = ('M', e[1])
        elif e[0] == 'I':
            last = ('I', '')
    if last and last[0] == 'T' and re.search(r'[ \xa0]+$', last[1]):
        n += 1
        print(f'  p#{i}: {last[1][-40:]!r}')
print('count:', n)

print('\n=== 4. nbsp runs inventory (excluding 答题位 （4×nbsp） patterns) ===')
n = 0
for i, p in enumerate(paras):
    seq = ''.join(t for k, t in ptext(p) if k == 'T')
    for m in re.finditer(r'\xa0{2,}', seq):
        s = m.group()
        ctx = seq[max(0, m.start()-8):m.end()+8]
        # whitelist: answer slot parens
        if re.match(r'^\xa0{3,5}$', s) and seq[max(0,m.start()-1):m.start()] == '（' and seq[m.end():m.end()+1] == '）':
            continue
        n += 1
        print(f'  p#{i}: len={len(s)} ctx={ctx!r}')
print('count(non-whitelist):', n)
