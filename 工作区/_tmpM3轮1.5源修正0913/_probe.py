# -*- coding: utf-8 -*-
"""定点探针：列出指定 docx 指定 body 元素内的 m:t / w:t 序列与 OMML 结构上下文"""
import sys
sys.path.insert(0, '工具')
from dxml import Document, qn
from lxml import etree

path, idxs = sys.argv[1], [int(x) for x in sys.argv[2].split(',')]
doc = Document(path)
els = list(doc.element.body)
for i in idxs:
    ch = els[i]
    print('==== el%d  <%s>' % (i, etree.QName(ch).localname))
    seq = []
    for k, node in enumerate(ch.iter()):
        ln = etree.QName(node).localname
        chain = []
        p = node
        while p is not None and etree.QName(p).localname != 'body':
            chain.append(etree.QName(p).localname)
            p = p.getparent()
        if ln == 't' and node.tag in (qn('w:t'), qn('m:t')):
            pre = 'w:t' if node.tag == qn('w:t') else 'm:t'
            print('  [%d] %s %r   path=%s' % (k, pre, node.text, '/'.join(reversed(chain))))
