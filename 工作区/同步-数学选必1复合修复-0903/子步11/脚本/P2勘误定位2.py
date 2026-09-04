# -*- coding: utf-8 -*-
"""只读定位：用题干/详解特征签名找题1.2.1.2-2所在段"""
import zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
DOCX = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'

with zipfile.ZipFile(DOCX) as z:
    root = etree.fromstring(z.read('word/document.xml'))
paras = root.findall(f'.//{{{W}}}body//{{{W}}}p')

def streams(p):
    full, wt = [], []
    for el in p.iter():
        ln = etree.QName(el).localname
        if ln == 't' and el.text:
            full.append(el.text)
            if etree.QName(el).namespace == W:
                wt.append(el.text)
    return ''.join(full), ''.join(wt)

def norm(s):
    return ''.join(s.split())

SIGS = ['若PA⊥平面ABC', '已知点A(0,1,0)', 'x-1+z=0-2x-z=0', 'x=1z=-2', 'x=-1z=2', '1.2.1.2', 'P(－1,0,2)', 'P(-1,0,2)']
for i, p in enumerate(paras):
    full, wt = streams(p)
    nf, nw = norm(full), norm(wt)
    hits = [s for s in SIGS if norm(s) in nf or norm(s) in nw]
    if hits:
        print(f'p#{i} hits={hits}')
        print(f'   WT: {wt[:120]!r}')
        print(f'   FULL: {full[:200]!r}')

# 另：列出全部题号块文本，看1.2.1.2节题号长什么样
print('\n===== 全部含"1.2.1"的题号段（wt前40字） =====')
for i, p in enumerate(paras):
    _, wt = streams(p)
    w = norm(wt)
    if '1.2.1' in w and ('-' in w or '－' in w or '.' in w):
        print(f'p#{i}: {wt[:50]!r}')
