# -*- coding: utf-8 -*-
"""FX5-G probe 11: raw XML of bianzhu paras 166/234/301/324/726 + inline-oMath-aware stream"""
import re
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

tree = etree.parse(DOC)
root = tree.getroot()
body = root.find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

def stream(p):
    out = []
    for r in p.findall(f'{{{W}}}r'):
        for c in r:
            t = c.tag.split('}')[1]
            if t == 't':
                out.append(('T', c.text or ''))
            elif t == 'oMath':
                txt = ''.join(x.text or '' for x in c.iter(f'{{{M}}}t'))
                out.append(('M', txt))
            elif t == 'tab':
                out.append(('TAB', ''))
            elif t == 'drawing':
                out.append(('I', ''))
    for om in p.findall(f'{{{M}}}oMath'):
        txt = ''.join(x.text or '' for x in om.iter(f'{{{M}}}t'))
        out.append(('M-para', txt))
    return out

for idx in (166, 234, 301, 324, 726, 744):
    print(f'\n===== p#{idx} inline-aware stream =====')
    for kind, txt in stream(paras[idx]):
        print(f'  {kind}: {txt!r}')
