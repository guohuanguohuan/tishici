# -*- coding: utf-8 -*-
"""按文本定位 body 元素序号，并列出其直接子节点与文本"""
import sys
sys.path.insert(0, '工具')
from dxml import Document, qn
from lxml import etree
W, M = qn('w:t'), qn('m:t')

def txt(n):
    return ''.join((t.text or '') for t in n.iter() if t.tag in (W, M))

path = sys.argv[1]
doc = Document(path)
els = list(doc.element.body)
for kw in sys.argv[2:]:
    hits = [(i, txt(ch)) for i, ch in enumerate(els) if kw in txt(ch)]
    print('#### 关键词 %r 命中 %d 处' % (kw, len(hits)))
    for i, t in hits:
        print('  el%d 全文=%r' % (i, t))
        kids = list(els[i])
        acc = ''
        for k, n in enumerate(kids):
            s = txt(n)
            acc += s
            print('     [%2d] %-10s %r' % (k, etree.QName(n).localname, s))
        print('     挂点 w:shd=%d pBdr=%s drawing=%d oMath=%d 子节点=%d' % (
            len(els[i].findall('.//' + qn('w:shd'))),
            els[i].find('.//' + qn('w:pBdr')) is not None,
            len(els[i].findall('.//' + qn('w:drawing'))),
            len(els[i].findall('.//' + qn('m:oMath'))), len(kids)))
