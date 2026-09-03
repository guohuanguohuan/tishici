# -*- coding: utf-8 -*-
"""FX5-G probe 4: full inventory of option paragraphs — run-level event stream for separator surgery"""
import re
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

tree = etree.parse(DOC)
root = tree.getroot()
body = root.find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

MARK = re.compile(r'^([A-D])．')

def events(p):
    """linear event stream: ('wt', node, text) / ('tab', node) / ('omath', node) / ('other', tag)"""
    ev = []
    for r in p.findall(f'{{{W}}}r'):
        for c in r:
            tag = c.tag.split('}')[1]
            if tag == 't':
                ev.append(('wt', c, c.text or ''))
            elif tag == 'tab':
                ev.append(('tab', c, None))
            elif tag == 'drawing':
                ev.append(('drawing', c, None))
            elif tag in ('rPr', 'lastRenderedPageBreak', 'bookmarkStart', 'bookmarkEnd'):
                pass
            else:
                ev.append(('other-' + tag, c, None))
    for om in p.findall(f'.//{{{M}}}oMath'):
        pass  # handled positionally below
    return ev

def full_stream(p):
    """document-order stream of children events across runs and oMath (oMath as atomic)"""
    ev = []
    def walk(el, depth=0):
        for c in el:
            t = c.tag.split('}')[1] if '}' in c.tag else c.tag
            if c.tag == f'{{{W}}}p':
                continue
            if c.tag == f'{{{W}}}r':
                walk(c, depth)
            elif c.tag == f'{{{M}}}oMath' or c.tag == f'{{{M}}}oMathPara':
                txt = ''.join(c.itertext())
                ev.append(('MATH', c, txt))
            elif c.tag == f'{{{W}}}t':
                ev.append(('wt', c, c.text or ''))
            elif c.tag == f'{{{W}}}tab':
                ev.append(('tab', c, None))
            elif c.tag == f'{{{W}}}drawing':
                ev.append(('drawing', c, '[IMG]'))
            elif c.tag == f'{{{W}}}pPr' or c.tag == f'{{{W}}}rPr':
                continue
            elif c.tag == f'{{{W}}}bookmarkStart' or c.tag == f'{{{W}}}bookmarkEnd':
                continue
            else:
                walk(c, depth)
    walk(p)
    return ev

# inventory: all paras whose w:t layer contains option marker A．
opt_paras = []
for i, p in enumerate(paras):
    wt = ''.join(t.text or '' for t in p.iter(f'{{{W}}}t'))
    if re.search(r'A．', wt) or re.search(r'A\.[^\d]', wt):
        opt_paras.append(i)
print('option paras:', len(opt_paras), opt_paras)

for i in opt_paras:
    p = paras[i]
    st = full_stream(p)
    s = []
    for kind, node, txt in st:
        if kind == 'wt': s.append(txt)
        elif kind == 'MATH': s.append('«' + txt + '»')
        elif kind == 'tab': s.append('⟦T⟧')
        elif kind == 'drawing': s.append('[IMG]')
    line = ''.join(s)
    # compress answer-slot nbsp
    line = line.replace('\xa0', '␣')
    print(f'\n--- p#{i}: {line[:220]}')
