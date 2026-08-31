# -*- coding: utf-8 -*-
"""W-G P0717元素序检查：＿＿后紧跟的OMML公式是否为挖空答案"""
import zipfile
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)
def m(t): return '{%s}%s' % (M, t)

CPY = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68\G工作副本.docx"
doc = etree.fromstring(zipfile.ZipFile(CPY).read('word/document.xml'))
body = doc.find(w('body'))
paras = [el for el in body if isinstance(el.tag, str) and el.tag == w('p')]
p = paras[717]
# 直接子级run与oMath的文档序
seq = []
for child in p:
    if not isinstance(child.tag, str): continue
    if child.tag == w('r'):
        t = ''.join(tt.text or '' for tt in child.iter() if tt.tag == w('t'))
        rpr = child.find(w('rPr'))
        shd = rpr.find(w('shd')).get(w('fill')) if (rpr is not None and rpr.find(w('shd')) is not None) else None
        seq.append(('r', t, shd))
    elif child.tag == m('oMath'):
        lin = ''.join(tt.text or '' for tt in child.iter() if tt.tag == m('t'))
        # oMath内是否有shd
        nshd = sum(1 for e in child.iter() if e.tag in (w('shd'),) )
        seq.append(('oMath', lin, 'shd#=%d' % nshd))
for i, (k, t, s) in enumerate(seq):
    print(i, k, repr(t[:50]), s)
