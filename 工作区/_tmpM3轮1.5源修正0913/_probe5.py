# -*- coding: utf-8 -*-
"""打印指定 el 的直接子节点＋二级子节点（带 w:/m: 前缀）"""
import sys
sys.path.insert(0, '工具')
from dxml import Document, qn
from lxml import etree

WNS = qn('w:body').rsplit('}', 1)[0] + '}'
MNS = qn('m:body').rsplit('}', 1)[0] + '}'
W, M = qn('w:t'), qn('m:t')

def pref(n):
    u = etree.QName(n)
    p = 'w:' if u.namespace + '}' == WNS else ('m:' if u.namespace + '}' == MNS else '?')
    return p + u.localname

def txt(n):
    return ''.join((t.text or '') for t in n.iter() if t.tag in (W, M))

path = sys.argv[1]
doc = Document(path)
els = list(doc.element.body)
for i in [int(x) for x in sys.argv[2].split(',')]:
    print('==== el%d' % i)
    for k, n in enumerate(els[i]):
        print(' [%2d] %-12s %r' % (k, pref(n), txt(n)))
        for j, g in enumerate(n):
            print('      (%d.%d) %-12s %r' % (k, j, pref(g), txt(g)))
