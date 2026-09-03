# -*- coding: utf-8 -*-
"""FX5-G probe 10: raw XML of p#744 (suspect) vs p#730 (intact bianzhu with math)"""
import re
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

tree = etree.parse(DOC)
root = tree.getroot()
body = root.find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

def clean(s):
    return re.sub(r'\s+xmlns:[a-zA-Z0-9]+="[^"]*"', '', s)

print('=== p#730 RAW (intact?) ===')
print(clean(etree.tostring(paras[730], encoding='unicode'))[:4000])
print('\n\n=== p#744 RAW (suspect) ===')
print(clean(etree.tostring(paras[744], encoding='unicode'))[:4000])
