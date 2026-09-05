# -*- coding: utf-8 -*-
"""H 件纠错轮视觉回归：两处修复点所在页 + 下一页，993px PNG。"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '回归')
NAME = '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）'
JOBS = [
    ('【性质证明】', 'H_性质证明分数线'),   # 修复点A
    ('重根技巧', 'H_切线例题分数线'),       # 修复点B（PDF文本流中"切线为例"被公式换行截断，改用同段唯一锚）
]
d = pymupdf.open(os.path.join(OUT, NAME + '.pdf'))
print('PDF 页数:', len(d))
for anchor, out in JOBS:
    hits = [p for p in range(len(d)) if d[p].search_for(anchor)]
    if not hits:
        print('!! 锚未命中:', anchor)
        continue
    p0 = hits[0]
    for p in sorted({p0, min(p0 + 1, len(d) - 1)}):
        pg = d[p]
        z = 993.0 / pg.rect.width
        fp = os.path.join(OUT, '%s_p%03d.png' % (out, p + 1))
        pg.get_pixmap(matrix=pymupdf.Matrix(z, z)).save(fp)
        print('渲染', os.path.basename(fp), '（锚@页%d）' % (p0 + 1))
# 缺陷残留全文检索
for bad in ('/x²', 'a²+y²', 'x²a²'):
    tot = sum(len(d[p].search_for(bad)) for p in range(len(d)))
    print('残留检索 %r -> %d 命中' % (bad, tot))
d.close()
print('RENDER H DONE')
