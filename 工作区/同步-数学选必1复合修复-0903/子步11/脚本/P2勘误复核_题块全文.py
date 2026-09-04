# -*- coding: utf-8 -*-
"""只读：题1.2.1.3-2（前轮号1.2.1.2-2）题块全文提取＋全件签名扫描"""
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

print('===== 题块全文 p#469..p#477（不截断） =====')
for i in range(469, 478):
    full, wt = streams(paras[i])
    if not full.strip():
        print(f'p#{i}: <空段>')
        continue
    print(f'p#{i}\n  WT  : {wt!r}\n  FULL: {full!r}')

print('\n===== 「解得」处逐字（p#475 FULL 原始，含空白） =====')
full, _ = streams(paras[475])
j = full.find('解得')
print(repr(full[max(0, j - 40):j + 60]))

print('\n===== 全件签名扫描（去空白归一，逐段） =====')
SIGS = {
    '旧错值 x=1z=-2': 'x=1z=-2',
    '改正值 x=-1z=2': 'x=-1z=2',
    '方程组 x-1+z=0-2x-z=0': 'x-1+z=0-2x-z=0',
    '题干特征 若PA⊥平面ABC': '若PA⊥平面ABC',
    '结论 P(－1,0,2)': 'P(－1,0,2)',
}
hits = {k: [] for k in SIGS}
for i, p in enumerate(paras):
    nf = norm(streams(p)[0])
    for k, s in SIGS.items():
        if norm(s) in nf:
            hits[k].append(i)
for k, v in hits.items():
    print(f'{k}: 命中段={v}')

print('\n===== 题干选项核对（p#471 FULL 尾部） =====')
f471, _ = streams(paras[471])
print(repr(f471))
