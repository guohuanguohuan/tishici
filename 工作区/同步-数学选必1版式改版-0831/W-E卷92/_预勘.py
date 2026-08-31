# -*- coding: utf-8 -*-
"""W-E卷92 预勘：①4处＿＿段run结构（N15双标记判定）②全件正文w:ind残留清单③jc分布④节头清单"""
import zipfile, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)
def m(t): return '{%s}%s' % (M, t)

path = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-E卷92\E卷92-工作副本.docx"
with zipfile.ZipFile(path) as z:
    doc = etree.fromstring(z.read('word/document.xml'))
body = doc.find(w('body'))

def in_table(p):
    par = p.getparent()
    while par is not None:
        if par.tag == w('tbl'): return True
        par = par.getparent()
    return False

def rtext(r):
    return ''.join(t.text or '' for t in r.iter() if isinstance(t.tag, str) and t.tag in (w('t'), m('t')))

print('==== ① ＿＿段run结构 ====')
for i, el in enumerate(body):
    if not isinstance(el.tag, str) or el.tag != w('p'): continue
    lt = ''.join(rtext(r) for r in el.findall('.//' + w('r')))
    if '＿' not in lt: continue
    print('--- P%d ---' % i)
    for r in el.findall('.//' + w('r')):
        rPr = r.find(w('rPr'))
        shd = rPr.find(w('shd')) if rPr is not None else None
        col = rPr.find(w('color')) if rPr is not None else None
        sz = rPr.find(w('sz')) if rPr is not None else None
        t = rtext(r)
        if not t: continue
        print('  run[%r] shd=%s color=%s sz=%s' % (t[:30], shd.get(w('fill')) if shd is not None else None, col.get(w('val')) if col is not None else None, sz.get(w('val')) if sz is not None else None))

print('==== ② w:ind 残留（正文body直接子级段＋表内段）====')
n_body_ind = 0; n_tbl_ind = 0
for p in body.iter(w('p')):
    pPr = p.find(w('pPr'))
    if pPr is None: continue
    ind = pPr.find(w('ind'))
    if ind is None: continue
    if in_table(p):
        n_tbl_ind += 1
    else:
        n_body_ind += 1
        attrs = {etree.QName(k).localname: v for k, v in ind.attrib.items()}
        print('  P段ind: %s | %s' % (attrs, rtext(p)[:50] if hasattr(p, 'find') else ''))
print('body直接段ind数=%d 表内段ind数=%d' % (n_body_ind, n_tbl_ind))

print('==== ③ jc 分布（正文段，非表内）====')
from collections import Counter
c = Counter()
for p in body.iter(w('p')):
    if in_table(p): continue
    pPr = p.find(w('pPr'))
    jc = pPr.find(w('jc')) if pPr is not None else None
    c[jc.get(w('val')) if jc is not None else None] += 1
print(c)

print('==== ④ 节头清单（N.N式）====')
for i, el in enumerate(body):
    if not isinstance(el.tag, str) or el.tag != w('p'): continue
    t = ''.join(rtext(r) for r in el.findall('.//' + w('r')))
    if re.match(r'^\d+(\.\d+)+\s', t) or re.match(r'^\d+(\.\d+)+', t):
        pPr = el.find(w('pPr'))
        pstyle = pPr.find(w('pStyle')) if pPr is not None else None
        print('  P%d %s | style=%s' % (i, t[:44], pstyle.get(w('val')) if pstyle is not None else None))

print('==== ⑤ 页眉页脚部件 jc/ind 速览 ====')
with zipfile.ZipFile(path) as z:
    names = [n for n in z.namelist() if n.startswith('word/header') or n.startswith('word/footer')]
    for n in names:
        d = etree.fromstring(z.read(n))
        jcs = [pp.find(w('jc')).get(w('val')) for pp in d.iter(w('p')) if pp.find(w('pPr')) is not None and pp.find(w('pPr')).find(w('jc')) is not None]
        print(' ', n, 'jc=', jcs)
