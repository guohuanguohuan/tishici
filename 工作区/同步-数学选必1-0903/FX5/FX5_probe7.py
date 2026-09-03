# -*- coding: utf-8 -*-
"""FX5-G probe 7: extract the source question text from 大招7平均性质 around '的两个交点为'"""
import zipfile, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
SRC = r'C:\提示词\高中数学\参考\组卷网\高中数学解题大招（二级结论）荟萃\04_原始资料\模块8解析几何\模块8大招7平均性质.docx'

with zipfile.ZipFile(SRC) as z:
    xml = z.read('word/document.xml')
root = etree.fromstring(xml)
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

texts = [ptext(p) for p in paras]
for i, t in enumerate(texts):
    if '的两个交点为' in t or 'x2=2y' in t.replace(' ', '') or '在平面直角坐标系xOy中' in t:
        print(f'\n>>> found at p#{i}:')
        for j in range(max(0, i-2), min(len(texts), i+18)):
            print(f'  src p#{j}: {texts[j][:180]!r}')
        break
