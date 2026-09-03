# -*- coding: utf-8 -*-
"""定位：dump 若干答案段的原始子元素+oMath灰底检查，确认oMath是否真无灰"""
import zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
PATH = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
with zipfile.ZipFile(PATH) as z:
    root = etree.fromstring(z.read('word/document.xml'))
paras = root.find(f'{{{W}}}body').findall(f'{{{W}}}p')

def om_gray_detail(om):
    """列出oMath内所有shd及所在元素路径"""
    out = []
    for el in om.iter():
        ln = etree.QName(el).localname
        if ln == 'shd':
            par = el.getparent()
            out.append((etree.QName(par).localname, el.get(f'{{{W}}}fill')))
    return out

for idx in (180, 212, 1061):
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
            print(f'  r.{"灰" if fill=="C9C9C9" else "-"} {t.text!r}')
        elif ln == 'oMath':
            grays = om_gray_detail(c)
            lin = ''.join(e.text or '' for e in c.iter(f'{{{W}}}t'))
            print(f'  oMath.灰点={grays} lin={lin!r}')
    print()
