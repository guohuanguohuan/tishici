# -*- coding: utf-8 -*-
"""检查待删节点集合内是否含特殊构件（批注/修订/书签/图/域/脚注）"""
import sys
sys.path.insert(0, '工具')
from dxml import Document, qn
from lxml import etree

path = sys.argv[1]
doc = Document(path)
els = list(doc.element.body)
plan = {'el91': (91, 24, 45), 'el98': (98, 24, 44), 'el87': (87, 4, 5)}
for tag, (i, a, b) in plan.items():
    p = els[i]
    kids = list(p)
    seg = kids[a:b]
    names = sorted({etree.QName(n).localname for n in seg} |
                   {etree.QName(d).localname for n in seg for d in n.iter()})
    print('%s 待删节点 %d..%d 共%d个; 内部标签全集=%s' % (tag, a, b-1, len(seg), names))
    txt = ''.join(t.text for n in seg for t in n.iter() if t.tag in (qn('w:t'), qn('m:t')) and t.text)
    print('   拼接文本=%r 长度=%d' % (txt, len(txt)))
print('--- el87 保留部分 xml ---')
print(etree.tostring(els[87][4], encoding='unicode')[:1200])
