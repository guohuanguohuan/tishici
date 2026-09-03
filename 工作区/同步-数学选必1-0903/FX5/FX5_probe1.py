# -*- coding: utf-8 -*-
"""FX5-G probe 1: structure — sectPr, para[0], tabs, sz21, shading overview"""
import re
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}

tree = etree.parse(DOC)
root = tree.getroot()
body = root.find(f'{{{W}}}body')

# All sectPr locations
sectprs = root.findall(f'.//{{{W}}}sectPr')
print('=== sectPr count:', len(sectprs))
for i, sp in enumerate(sectprs):
    # where is it? inside pPr of a paragraph or body child
    par = sp.getparent()
    gp = par.getparent()
    tag_chain = par.tag.split('}')[1] + '<-' + gp.tag.split('}')[1]
    print(f'--- sectPr[{i}] in {tag_chain}')
    for child in sp:
        t = child.tag.split('}')[1]
        attrs = {k.split("}")[1]: v for k, v in child.attrib.items()}
        print('    ', t, attrs)

paras = body.findall(f'{{{W}}}p')
print('\n=== total paragraphs:', len(paras))

# para[0] content
p0 = paras[0]
print('\n=== para[0] XML (first 2500 chars):')
x = etree.tostring(p0, encoding='unicode')
print(x[:2500])
print('\npara[0] text:', repr(''.join(p0.itertext())[:120]))

# para[1], para[2] text
for i in (1, 2, 3):
    t = ''.join(paras[i].itertext())
    st = paras[i].find(f'{{{W}}}pPr/{{{W}}}pStyle')
    print(f'para[{i}] style={st.get(f"{{{W}}}val") if st is not None else None} text={t[:60]!r}')
