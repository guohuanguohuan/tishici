# -*- coding: utf-8 -*-
# 一次性勘察脚本（E1衔接）：输出docx body段落流（序号/样式/字号标记/底纹/前60字），供人工过目
import sys, io, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)

path = sys.argv[1]
lim = int(sys.argv[2]) if len(sys.argv) > 2 else 200
off = int(sys.argv[3]) if len(sys.argv) > 3 else 0
with zipfile.ZipFile(path) as z:
    root = etree.fromstring(z.read('word/document.xml'))
body = root.find(q('body'))
for i, el in enumerate(body):
    tag = etree.QName(el).localname
    if tag != 'p':
        print(f'[{i}] <{tag}>')
        continue
    if i < off or i >= off + lim:
        continue
    pPr = el.find(q('pPr'))
    style = ''
    shd = ''
    if pPr is not None:
        ps = pPr.find(q('pStyle'))
        if ps is not None: style = ps.get(q('val'))
        sh = pPr.find(q('shd'))
        if sh is not None: shd = sh.get(q('fill'), '')
    txt = ''.join(t.text or '' for t in el.iter(q('t')))
    mt = ''.join(t.text or '' for t in el.iter(qm('t')))
    nmath = len(el.findall('.//' + qm('oMath')))
    ndraw = len(el.findall('.//' + q('drawing')))
    flag = ''
    if nmath: flag += f' M{nmath}'
    if ndraw: flag += f' D{ndraw}'
    if shd: flag += f' [{shd}]'
    if style: flag += f' <{style}>'
    print(f'[{i}] {txt}{mt}{flag}'[:150])
