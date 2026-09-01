# -*- coding: utf-8 -*-
"""R1审计——特定粘连候选块结构探针。"""
import sys, os, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s'%(W,t)
def mq(t): return '{%s}%s'%(M,t)
def plain_omath(om): return ''.join(t.text or '' for t in om.iter(mq('t')))
def struct_sig(om, depth=0):
    """紧凑结构签名：eqArr→EQ[..];..，f→FR(a|b)，rad→RAD(..)，m→MAT，d→D(..)，其余线性。"""
    t = etree.QName(om).localname
    if t == 'eqArr':
        return 'EQ[' + ' ;; '.join(struct_sig(e) for e in om.findall(mq('e'))) + ']'
    if t == 'f':
        return 'FR(%s|%s)' % (struct_sig(om.find(mq('num')) or ''), struct_sig(om.find(mq('den')) or ''))
    if t == 'rad':
        return 'RAD(%s)' % struct_sig(om.find(mq('e')) or '')
    if t == 'm':
        return 'MAT[' + ';'.join(','.join(struct_sig(e) for e in row.findall(mq('e'))) for row in om.findall(mq('mr'))) + ']'
    if t == 'd':
        return 'D(' + ';'.join(struct_sig(e) for e in om.findall(mq('e'))) + ')'
    if t == 'r':
        return (om.find(mq('t')).text or '') if om.find(mq('t')) is not None else ''
    parts = []
    for c in om:
        ct = etree.QName(c).localname
        if ct in ('rPr',): continue
        parts.append(struct_sig(c))
    return ''.join(parts)

TARGETS = [
 ('B','ijk111020'), ('B','ijk111200'), ('B','x=11641'), ('B','x-1+z=0-2x-z=0'),
 ('B','n⋅AB=0n⋅AC=0'), ('B','n⋅AB=0'), ('B','m⋅PD=0'), ('B','n·FC=0n·FG=0'),
 ('B','n⋅AB=0n'), ('C','x2-y2=-2x2+y2=3'), ('C','n⋅PQ=0n⋅PS=0'),
 ('C','r22+n2=25r22+n'), ('C','m·EF=0m·DE=0'), ('C','n⊥AB,n⊥AN'),
 ('B','y=2,z=-1'), ('B','z=3,y=0'), ('B','cosθ='),('C','tan30°'),
]
D = r'C:\提示词\高中数学\高中数学同步'
FN = {'B':'人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
      'C':'人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'}
cache = {}
for code, sig in TARGETS:
    if code not in cache:
        z = zipfile.ZipFile(os.path.join(D, FN[code]))
        doc = etree.fromstring(z.read('word/document.xml'))
        cache[code] = list(doc.find(q('body')).iter(q('p')))
    hit = 0
    for i, p in enumerate(cache[code]):
        for om in p.iter(mq('oMath')):
            pl = plain_omath(om)
            if sig in pl:
                hit += 1
                if hit <= 2:
                    print('[%s p#%d] 朴素=%r' % (code, i+1, pl[:90]))
                    print('        结构=%s' % struct_sig(om)[:300])
    if hit == 0:
        print('[%s] 签名%r 未找到' % (code, sig))
print('DONE')
