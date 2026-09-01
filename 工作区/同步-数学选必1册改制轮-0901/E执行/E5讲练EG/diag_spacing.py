# -*- coding: utf-8 -*-
import zipfile
from lxml import etree
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def q(t): return '{%s}%s' % (W, t)
z = zipfile.ZipFile('E_工作.docx')
root = etree.fromstring(z.read('word/document.xml'))
body = root.find(q('body'))
assert body is not None, 'body None!'
st = etree.fromstring(z.read('word/styles.xml'))
anchor_ids = set()
for s in st.iter(q('style')):
    nm = s.find(q('name'))
    val = nm.get(q('val')) if nm is not None else ''
    if val == '节名锚':
        anchor_ids.add(s.get(q('styleId')))
print('anchor_ids=', anchor_ids)
n28 = 0; nan = 0
for i, p in enumerate(body):
    if p.tag != q('p'):
        continue
    ps = p.find(q('pPr'))
    pst = ps.find(q('pStyle')) if ps is not None else None
    pstyle = pst.get(q('val')) if pst is not None else ''
    if pstyle in anchor_ids:
        nan += 1
        continue
    spc = ps.find(q('spacing')) if ps is not None else None
    ok = spc is not None and spc.get(q('before')) == '0' and spc.get(q('after')) == '0' \
        and spc.get(q('line')) == '410' and spc.get(q('lineRule')) == 'atLeast'
    if not ok:
        txt = ''.join(t.text or '' for t in p.iter(q('t')))
        attrs = {etree.QName(k).localname: v for k, v in spc.attrib.items()} if spc is not None else None
        print('SPACING dev body[%d] pstyle=%r attrs=%s text=%r' % (i, pstyle, attrs, txt[:40]))
print('anchor paras =', nan)
for r in root.iter(q('r')):
    rpr = r.find(q('rPr'))
    if rpr is None:
        continue
    sz = rpr.find(q('sz'))
    if sz is not None and sz.get(q('val')) == '28':
        n28 += 1
print('sz=28 run total =', n28)
