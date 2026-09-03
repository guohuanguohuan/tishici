# -*- coding: utf-8 -*-
"""FX4-F 补充修复：选项段边界空run补「；」（B→C边界与长句选项粘连，共6段7处）"""
import re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
ns = {'w': W, 'm': M}
def q(t): return '{%s}%s' % (W, t)

tree = etree.parse('F_unzip/word/document.xml.new')
body = tree.getroot().find('w:body', ns)
paras = body.findall('w:p', ns)

pat = re.compile(r'[A-D]．')
fixed = []
for i, p in enumerate(paras):
    joined = ''.join(t.text or '' for t in p.iter() if t.tag in (q('t'), '{%s}t' % M))
    if not pat.search(joined[:60]):
        continue
    ts = [t for t in p.iter(q('t'))]
    for j, t in enumerate(ts):
        if (t.text or '') != '':
            continue
        # 下一个非空 w:t
        nxt = None
        for k in range(j+1, len(ts)):
            if (ts[k].text or '') != '':
                nxt = ts[k].text; break
        if nxt is None:
            continue
        if re.match(r'^[B-D]$', nxt) or re.match(r'^[B-D]．', nxt):
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = '；'
            fixed.append((i, nxt[:12]))

print("fixed:", fixed)
out = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
open('F_unzip/word/document.xml.new', 'wb').write(out)
print("saved, bytes:", len(out))
