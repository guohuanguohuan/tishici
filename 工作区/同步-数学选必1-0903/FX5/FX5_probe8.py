# -*- coding: utf-8 -*-
"""FX5-G probe 8: dump source option paras XML (大招7 p#60-63) + G p#754 XML"""
import zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
SRC = r'C:\提示词\高中数学\参考\组卷网\高中数学解题大招（二级结论）荟萃\04_原始资料\模块8解析几何\模块8大招7平均性质.docx'
G = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'

with zipfile.ZipFile(SRC) as z:
    sxml = z.read('word/document.xml')
sroot = etree.fromstring(sxml)
sbody = sroot.find(f'{{{W}}}body')
sparas = sbody.findall(f'{{{W}}}p')

def strip_ns(el):
    s = etree.tostring(el, encoding='unicode')
    return s

import re
def clean(s):
    # remove xmlns declarations for readability
    return re.sub(r'\s+xmlns:[a-zA-Z0-9]+="[^"]*"', '', s)

print('=== SOURCE p#60 (option A) ===')
print(clean(strip_ns(sparas[60]))[:3000])
print('\n=== SOURCE p#61 (option B) ===')
print(clean(strip_ns(sparas[61]))[:4000])
print('\n=== SOURCE p#62 (option C) ===')
print(clean(strip_ns(sparas[62]))[:4000])
print('\n=== SOURCE p#63 (option D) ===')
print(clean(strip_ns(sparas[63]))[:4000])

gtree = etree.parse(G)
groot = gtree.getroot()
gbody = groot.find(f'{{{W}}}body')
gparas = gbody.findall(f'{{{W}}}p')
print('\n\n=== G p#754 (full XML) ===')
print(clean(strip_ns(gparas[754]))[:8000])
