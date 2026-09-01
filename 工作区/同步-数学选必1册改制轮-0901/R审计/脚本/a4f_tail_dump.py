# -*- coding: utf-8 -*-
"""R1审计——②段尾公式簇6处段落dump。"""
import sys, os, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s'%(W,t)
def mq(t): return '{%s}%s'%(M,t)
def plain_omath(om): return ''.join(t.text or '' for t in om.iter(mq('t')))
def para_dump(p):
    out = []
    def walk(el):
        for c in el:
            t = etree.QName(c).localname; ns = etree.QName(c).namespace
            if t == 't' and ns == W: out.append(c.text or '')
            elif t == 'oMath': out.append('⟦' + plain_omath(c) + '⟧')
            else: walk(c)
    walk(p)
    return ''.join(out)

TARGETS = [
 ('B','2,3','1.1.3-10'), ('B','-1,2,1','1.2.2-1'), ('B','P3,-3,4','1.2.2-2'),
 ('B','0,23','1.2.2-7'), ('C','16π9,3π','1.2.5-53'), ('C','2π3,2π','1.2.5-55'),
]
D = r'C:\提示词\高中数学\高中数学同步'
FN = {'B':'人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
      'C':'人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'}
for code, sig, qno in TARGETS:
    z = zipfile.ZipFile(os.path.join(D, FN[code]))
    doc = etree.fromstring(z.read('word/document.xml'))
    paras = list(doc.find(q('body')).iter(q('p')))
    # 先定位该题号段index，再向后找含签名的段
    start = None
    for i, p in enumerate(paras):
        t = ''.join(x.text or '' for x in p.iter(q('t')))
        if t.strip().startswith(qno + '．'):
            start = i; break
    printed = 0
    for i in range(start or 0, min(start + 40 if start else 9999, len(paras))):
        lin = para_dump(paras[i])
        if sig in lin.replace('⟦','').replace('⟧',''):
            print('[%s %s p#%d]' % (code, qno, i+1))
            for j in range(max(0, i-2), min(i+2, len(paras))):
                mark = '>>' if j == i else '  '
                print('  %s %s' % (mark, para_dump(paras[j])[:300]))
            printed += 1
            if printed >= 2: break
print('DONE')
