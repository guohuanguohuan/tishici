# -*- coding: utf-8 -*-
"""E1内容抽检：拉取指定段落全文＋前后段（只读）。"""
import os, sys, zipfile
from lxml import etree

NSW = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (NSW, t)
BASE = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'

def paras(fn):
    z = zipfile.ZipFile(os.path.join(BASE, fn))
    doc = etree.fromstring(z.read('word/document.xml'))
    out = []
    for p in doc.iter(q('p')):
        wt = ''.join(t.text or '' for t in p.iter(q('t')))
        ms = []
        for om in p.iter('{%s}oMath' % M):
            # 带根号/分数标记的线性化：√ 用 RAD() 包裹、分数用 A/B
            lin = lin_omath(om)
            if lin.strip(): ms.append(lin)
        out.append((wt, ' ‖ '.join(ms)))
    return out

def lin_omath(el):
    """保留分数与根号结构的线性化。"""
    MNS = '{%s}' % M
    def walk(e):
        if e.tag == MNS + 'f':  # fraction
            num = e.find(MNS + 'num'); den = e.find(MNS + 'den')
            return '(%s)/(%s)' % (''.join(walk(c) for c in num), ''.join(walk(c) for c in den))
        if e.tag == MNS + 'rad':  # radical
            e2 = e.find(MNS + 'e')
            return '√(%s)' % ''.join(walk(c) for c in e2)
        if e.tag == MNS + 'sSup':
            base = e.find(MNS + 'e'); sup = e.find(MNS + 'sup')
            return '%s^{%s}' % (''.join(walk(c) for c in base), ''.join(walk(c) for c in sup))
        if e.tag == MNS + 'sSub':
            base = e.find(MNS + 'e'); sub = e.find(MNS + 'sub')
            return '%s_{%s}' % (''.join(walk(c) for c in base), ''.join(walk(c) for c in sub))
        if e.tag == MNS + 't':
            return e.text or ''
        r = ''
        for c in e:
            r += walk(c)
        return r
    return walk(el)

TARGETS = [
    ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', [206, 207, 208, 209, 210]),
    ('B', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', [622, 623, 624, 625, 838, 839, 840, 841]),
    ('C', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', [4, 5, 6, 299, 300, 301, 302, 303]),
    ('X2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', [20, 21, 22, 23, 24]),
    ('F', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', [264, 265, 266, 267, 531, 532, 533, 534]),
    ('H', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', [384, 385, 386, 387, 714, 715, 716, 717, 718]),
    ('E', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', [518, 519, 520, 521]),
]
for code, fn, idxs in TARGETS:
    ps = paras(fn)
    print('#' * 12, code)
    for i in idxs:
        if i < len(ps):
            wt, m = ps[i]
            print('[%d] %s' % (i, wt[:150]))
            if m: print('     M: %s' % m[:400])
