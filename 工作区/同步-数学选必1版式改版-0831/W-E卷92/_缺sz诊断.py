# -*- coding: utf-8 -*-
"""诊断：找出3个非豁免run缺显式sz（复刻 字号双档改版.py 的复核断言口径）"""
import zipfile, re, sys
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def local(e): return etree.QName(e).localname
PUA_RE = re.compile(r'[\uE000-\uF8FF]')

def run_kind(r):
    has_t = any(t.text for t in r.findall(q('t')))
    if r.find(q('drawing')) is not None or r.find(q('pict')) is not None or r.find(q('object')) is not None:
        return 'img' if has_t else 'skip'
    for t in r.findall(q('t')):
        if t.text and PUA_RE.search(t.text):
            return 'skip'
    return 'text'

def under_drawing(r):
    a = r.getparent()
    while a is not None:
        if local(a) in ('drawing', 'pict', 'txbxContent', 'object'):
            return True
        a = a.getparent()
    return False

path = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-E卷92\E卷92-工作副本.docx"
with zipfile.ZipFile(path) as z:
    doc = etree.fromstring(z.read('word/document.xml'))
body = doc.find(q('body'))

missing = []
for p in body.iter(q('p')):
    ptxt = ''.join(t.text or '' for t in p.iter(q('t')))
    for r in p.iter(q('r')):
        if under_drawing(r) or run_kind(r) == 'skip':
            continue
        rpr = r.find(q('rPr'))
        if rpr is None or rpr.find(q('sz')) is None:
            missing.append((ptxt[:60], etree.tostring(r, encoding='unicode')[:300]))

print('missing数:', len(missing))
for ptxt, rx in missing:
    print('---')
    print('段:', ptxt)
    print('run:', rx)
