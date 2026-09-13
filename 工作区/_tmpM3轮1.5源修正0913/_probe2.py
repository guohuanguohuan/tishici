# -*- coding: utf-8 -*-
"""列出指定 body 元素的直接子节点（run/oMath/bookmark…）与其拼接文本"""
import sys
sys.path.insert(0, '工具')
from dxml import Document, qn
from lxml import etree

def text_of(node):
    out = []
    for t in node.iter():
        if t.tag in (qn('w:t'), qn('m:t')) and t.text:
            out.append(t.text)
    return ''.join(out)

path, idxs = sys.argv[1], [int(x) for x in sys.argv[2].split(',')]
doc = Document(path)
els = list(doc.element.body)
for i in idxs:
    ch = els[i]
    kids = list(ch)
    print('==== el%d <%s> 直接子节点 %d' % (i, etree.QName(ch).localname, len(kids)))
    full = ''
    for k, n in enumerate(kids):
        ln = etree.QName(n).localname
        t = text_of(n)
        full += t
        print('  [%d] %-12s %r' % (k, ln, t))
    print('  段落全文=%r' % full)
    print('  挂点: w:shd=%d pBdr=%s drawing=%d oMath=%d' % (
        len(ch.findall('.//' + qn('w:shd'))),
        (ch.find('.//' + qn('w:pBdr')) is not None),
        len(ch.findall('.//' + qn('w:drawing'))),
        len(ch.findall('.//' + qn('m:oMath')))))
