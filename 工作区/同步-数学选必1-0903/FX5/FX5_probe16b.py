# -*- coding: utf-8 -*-
"""FX5-G probe 16b: layer-sensitive space hygiene scan (item 7) — FIXED traversal"""
import re
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

tree = etree.parse(DOC)
body = tree.getroot().find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

def ptext_events(p):
    """document-order events; w:t within same w:r kept; math atomic."""
    out = []
    for node in p.iter():
        if node.tag == f'{{{W}}}t' and node.text is not None:
            out.append(('T', node.text))
        elif node.tag == f'{{{M}}}t' and node.text is not None:
            out.append(('M', node.text))
        elif node.tag == f'{{{W}}}drawing':
            out.append(('I', ''))
        elif node.tag == f'{{{W}}}tab' and node.getparent().tag == f'{{{W}}}r':
            out.append(('T', '\t'))
    return out

def T_grouped(p):
    """merge consecutive T events into chunks (broken by M/I)"""
    chunks = []
    buf = ''
    for k, t in ptext_events(p):
        if k == 'T':
            buf += t
        else:
            if buf:
                chunks.append(buf)
            buf = ''
            chunks.append(None)  # layer break marker
    if buf:
        chunks.append(buf)
    return chunks

print('=== 1. double half-space in w:t (chunk-internal) ===')
n = 0
for i, p in enumerate(paras):
    for c in T_grouped(p):
        if c and '  ' in c:
            n += 1
            print(f'  p#{i}: {c[:90]!r}')
print('count:', n)

print('\n=== 2. full-width punct preceded by space/nbsp (within w:t chunks) ===')
n = 0
for i, p in enumerate(paras):
    for c in T_grouped(p):
        if not c:
            continue
        for m in re.finditer(r'[ \xa0]([，。；：？！、）])', c):
            n += 1
            ctx = c[max(0, m.start()-15):m.end()+10]
            print(f'  p#{i}: ...{ctx!r}')
print('count:', n)

print('\n=== 3. trailing spaces at true para end ===')
n = 0
for i, p in enumerate(paras):
    ev = ptext_events(p)
    last = None
    for e in ev:
        if (e[0] in ('T', 'M')) and e[1]:
            last = e
        elif e[0] == 'I':
            last = ('I', '')
    if last and last[0] == 'T' and re.search(r'[ \xa0]+$', last[1]):
        n += 1
        print(f'  p#{i}: {last[1][-40:]!r}')
print('count:', n)

print('\n=== 4. nbsp sequences (whitelist=答题位（3-5×nbsp）) ===')
n = 0
for i, p in enumerate(paras):
    full = ''.join(t for k, t in ptext_events(p) if k == 'T')
    for m in re.finditer(r'\xa0{2,}', full):
        s = m.group()
        before = full[max(0, m.start()-1):m.start()]
        after = full[m.end():m.end()+1]
        if len(s) in (3, 4, 5) and before == '（' and after == '）':
            continue
        n += 1
        ctx = full[max(0, m.start()-10):m.end()+10]
        print(f'  p#{i}: len={len(s)} ctx={ctx!r}')
print('count(non-whitelist):', n)
