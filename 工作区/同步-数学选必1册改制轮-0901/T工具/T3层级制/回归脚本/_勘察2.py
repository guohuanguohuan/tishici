# -*- coding: utf-8 -*-
"""勘察2：题号/条目/节标题的run级结构（拆run形态、底纹/加粗挂点、区间括注位置）"""
import sys, re, zipfile, os
sys.path.insert(0, r'C:\提示词\工具')
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

def rinfo(r):
    rpr = r.find(q('rPr'))
    b = shd = sz = None
    if rpr is not None:
        b = 'b' if rpr.find(q('b')) is not None else '-'
        s = rpr.find(q('shd'))
        shd = s.get(q('fill')) if s is not None else '-'
        z = rpr.find(q('sz'))
        sz = z.get(q('val')) if z is not None else '-'
    return 'b=%s shd=%s sz=%s' % (b, shd, sz)

def dump_runs(path, want_idx):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    print('=' * 24, os.path.basename(path))
    for i, c in enumerate(body):
        if i not in want_idx:
            continue
        if c.tag != q('p'):
            continue
        print('--- [%d] ---' % i)
        for k, r in enumerate(c.findall(q('r'))[:8]):
            ts = ''.join(t.text or '' for t in r.findall(q('t')))
            if ts or k < 3:
                print('   run%d %s |%s|' % (k, rinfo(r), ts[:40]))

# B: 3=1.1节标题 4=1.1.1带区间 7=题1 386=讲部1.2.2.5；讲部条目位置待找
dump_runs(r'测试副本/B讲练上（61题）.docx', {3, 4, 7, 386})
dump_runs(r'测试副本/I1知识清单.docx', {8, 9, 10, 16, 49})
