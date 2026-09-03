# -*- coding: utf-8 -*-
"""FX5-G probe 9: run-level dump of bianzhu true-positive paras 166/234/301/324/726/744"""
import re
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

tree = etree.parse(DOC)
root = tree.getroot()
body = root.find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

def dump_runs(p):
    out = []
    for c in p:
        tag = c.tag.split('}')[1]
        if tag == 'pPr':
            continue
        if tag == 'r':
            for rc in c:
                rt = rc.tag.split('}')[1]
                if rt == 't':
                    out.append(('T', rc.text or ''))
                elif rt == 'tab':
                    out.append(('TAB', ''))
                elif rt == 'drawing':
                    out.append(('IMG', ''))
        elif tag == 'oMath':
            txt = ''.join(rc.text or '' for rc in c.iter(f'{{{M}}}t'))
            out.append(('MATH', txt))
        elif tag == 'oMathPara':
            txt = ''.join(rc.text or '' for rc in c.iter(f'{{{M}}}t'))
            out.append(('MATHPARA', txt))
        else:
            out.append((tag, ''))
    return out

for idx in (166, 234, 301, 324, 726, 744):
    print(f'\n===== p#{idx} run stream =====')
    for kind, txt in dump_runs(paras[idx]):
        print(f'  {kind}: {txt!r}')
