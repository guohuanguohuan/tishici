# -*- coding: utf-8 -*-
"""FX5-G probe 5: context around anomalous option paras"""
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
    def walk(el):
        for c in el:
            if c.tag == f'{{{W}}}t' and c.text is not None:
                out.append(c.text)
            elif c.tag == f'{{{M}}}t' and c.text is not None:
                out.append(c.text)
            elif c.tag == f'{{{W}}}tab' and c.getparent().tag == f'{{{W}}}r':
                out.append('⟦T⟧')
            elif c.tag == f'{{{W}}}drawing':
                out.append('[IMG]')
            else:
                walk(c)
    walk(p)
    return ''.join(out)

for center in (471, 490, 533, 672, 728, 743, 754):
    print(f'\n===== context p#{center} =====')
    for i in range(center - 2, center + 5):
        if 0 <= i < len(paras):
            st = paras[i].find(f'{{{W}}}pPr/{{{W}}}pStyle')
            sty = st.get(f'{{{W}}}val') if st is not None else ''
            shd = paras[i].find(f'{{{W}}}pPr/{{{W}}}shd')
            sh = shd.get(f'{{{W}}}fill') if shd is not None else ''
            t = ptext(paras[i]).replace('\xa0', '␣')
            print(f'  p#{i} [{sty}|{sh}] {t[:130]!r}')
