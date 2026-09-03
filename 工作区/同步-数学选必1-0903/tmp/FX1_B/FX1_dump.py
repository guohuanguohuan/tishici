# -*- coding: utf-8 -*-
"""精确dump 13条答案段：run文本/灰底 + oMath线性化(m:t)/是否整块灰"""
import zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
PATH = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
with zipfile.ZipFile(PATH) as z:
    root = etree.fromstring(z.read('word/document.xml'))
paras = root.find(f'{{{W}}}body').findall(f'{{{W}}}p')

def om_lin(om):
    return ''.join(e.text or '' for e in om.iter() if etree.QName(e).localname == 't')

def om_gray(om):
    return any(shd.get(f'{{{W}}}fill') == 'C9C9C9' for shd in om.iter(f'{{{W}}}shd'))

# 目标段号清单（来自前面检出含纯标点灰run的段）
targets = [151,180,212,225,307,617,632,678,835,918,1041,1061,1063]
for idx in targets:
    p = paras[idx]
    print(f'===== p#{idx} =====')
    for c in p:
        ln = etree.QName(c).localname
        if ln == 'pPr':
            continue
        if ln == 'r':
            t = c.find(f'{{{W}}}t')
            shd = c.find(f'{{{W}}}rPr/{{{W}}}shd')
            fill = shd.get(f'{{{W}}}fill') if shd is not None else ''
            mark = 'W' if fill == 'C9C9C9' else ' '
            print(f'  r[{mark}] {t.text!r}')
        elif ln == 'oMath':
            grayd = om_gray(c)
            print(f'  m[{"G" if grayd else " "}] {om_lin(c)!r}')
    print()
