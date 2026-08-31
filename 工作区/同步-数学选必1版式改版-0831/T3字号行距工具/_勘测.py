# -*- coding: utf-8 -*-
"""T3勘测脚本：dump段落形态（一次性，工作区子文件夹内）"""
import sys, io, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t):
    return '{%s}%s' % (W, t)

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

f = sys.argv[1]
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
z = zipfile.ZipFile(f)
doc = etree.fromstring(z.read('word/document.xml'))
body = doc.find(q('body'))
els = list(body)
print('file:', f, ' body子元素数:', len(els))
for i, el in enumerate(els):
    if not (lo <= i < hi):
        continue
    ln = etree.QName(el).localname
    if ln == 'tbl':
        rows = el.findall(q('tr'))
        first = ''
        if rows:
            first = para_text(rows[0])
        print(i, 'TBL rows=%d' % len(rows), repr(first[:50]))
    elif ln == 'sectPr':
        print(i, 'sectPr')
    else:
        txt = para_text(el)
        ps = el.find(q('pPr'))
        sid = ''
        outline = ''
        if ps is not None:
            pst = ps.find(q('pStyle'))
            sid = pst.get(q('val')) if pst is not None else ''
            ol = ps.find(q('outlineLvl'))
            outline = ol.get(q('val')) if ol is not None else ''
        # run字号分布
        szs = set()
        for r in el.findall(q('r')):
            rpr = r.find(q('rPr'))
            if rpr is None:
                szs.add('-')
                continue
            szel = rpr.find(q('sz'))
            szs.add(szel.get(q('val')) if szel is not None else '-')
        print(i, repr(txt[:66]), 'style=%s%s' % (sid, ('/ol' + outline) if outline else ''), 'sz:', sorted(szs))
