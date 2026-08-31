# -*- coding: utf-8 -*-
"""W-G N15预检：3处挖空run级形态（双标记 vs 悬空）"""
import zipfile, re
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)
def m(t): return '{%s}%s' % (M, t)

CPY = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68\G工作副本.docx"
doc = etree.fromstring(zipfile.ZipFile(CPY).read('word/document.xml'))
body = doc.find(w('body'))
paras = [el for el in body if isinstance(el.tag, str) and el.tag == w('p')]

def runinfo(p):
    out = []
    for r in p.findall('.//' + w('r')):
        t = ''.join(tt.text or '' for tt in r.iter() if tt.tag == w('t'))
        rpr = r.find(w('rPr'))
        shd = color = sz = None
        if rpr is not None:
            s = rpr.find(w('shd'))
            if s is not None: shd = s.get(w('fill'))
            c = rpr.find(w('color'))
            if c is not None: color = c.get(w('val'))
            z = rpr.find(w('sz'))
            if z is not None: sz = z.get(w('val'))
        out.append((t, shd, color, sz))
    # OMML runs
    for mr in p.findall('.//' + m('r')):
        t = ''.join(tt.text or '' for tt in mr.iter() if tt.tag == m('t'))
        rpr = mr.find(m('rPr'))
        shd = color = None
        if rpr is not None:
            s = rpr.find(w('shd'))
            if s is not None: shd = s.get(w('fill'))
            c = rpr.find(w('color'))
            if c is not None: color = c.get(w('val'))
        if t or shd or color:
            out.append(('[M]' + t, shd, color, 'M'))
    return out

for idx in (713, 717):
    p = paras[idx]
    print('=== P%04d' % idx)
    for t, shd, color, sz in runinfo(p):
        print('  run=%r shd=%s color=%s sz=%s' % (t[:44], shd, color, sz))
