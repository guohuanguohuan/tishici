# -*- coding: utf-8 -*-
import sys, io, copy, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
BASE = r'C:\提示词\高中数学\高中数学同步'
z = zipfile.ZipFile(BASE + r'\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx')
root = etree.fromstring(z.read('word/document.xml'))
body = root.find(q('body'))
ENT_RE = re.compile(r'^(\d+(?:\.\d+)*)-(\d+)．')
target = None
for el in body:
    if tag(el) == 'p' and ENT_RE.match(ptext(el)):
        target = el
        break
ne = copy.deepcopy(target)

def canon(e, rmask, idmask, valmask):
    if not isinstance(e.tag, str):
        return ''
    qn = etree.QName(e).namespace or ''
    out = ['<%s[%s]' % (etree.QName(e).localname, qn.rsplit('/', 2)[-1])]
    for k in sorted(e.attrib):
        v = e.attrib[k]
        kl = etree.QName(k).localname
        if k.startswith('{%s}' % R): v = '@@RID@@'
        if kl == 'id' and v in idmask: v = '@@DOCPr@@'
        if kl == 'val' and v in valmask: v = '@@NUM@@'
        out.append(' %s="%s"' % (kl, v))
    out.append('>')
    if e.text: out.append(e.text)
    for c in e:
        out.append(canon(c, rmask, idmask, valmask))
        if c.tail: out.append(c.tail)
    out.append('</>')
    return ''.join(out)

a = canon(target, set(), set(), set())
b = canon(ne, set(), set(), set())
print('无映射恒等:', a == b, len(a), len(b))
if a != b:
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            print('@', i)
            print('SRC:', a[max(0, i - 60):i + 160])
            print('NEW:', b[max(0, i - 60):i + 160])
            break
