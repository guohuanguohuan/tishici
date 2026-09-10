# -*- coding: utf-8 -*-
"""探针：用旧脚本（终版实测.py）原函数复算 g3 素材旧线框，找 71.29×72.09 的真实来源。"""
import sys, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
import pymupdf
def load(alias, path):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
old = load('oldm', '终版实测.py')
PT = old.PT
SRC = 'C:/提示词/工作区/_tmp片G素材/'
sp = pymupdf.open(SRC + 'tikz_tan6.pdf')[0]
r = sp.rect
clip = pymupdf.Rect(r.x0+0.2, r.y0+0.2, r.x1-0.2, r.y1-0.2)
print('页 %.2f×%.2f mm' % (r.width/PT, r.height/PT))
cs = old.merge_rows(old.cluster(old.diag_items(sp.get_drawings()), 8/25.4*PT))
for rr, nl in cs:
    print(' 旧簇 w%.2f h%.2f x[%.2f,%.2f] y[%.2f,%.2f] nlong=%d' % (rr.width/PT, rr.height/PT, rr.x0/PT, rr.x1/PT, rr.y0/PT, rr.y1/PT, nl))
rr = cs[0][0]
for k in [c[0] for c in cs[1:]]:
    rr |= k
seed = pymupdf.Rect(rr.x0-1, rr.y0-1, rr.x1+1, rr.y1+1)
W = old.fig_bbox(sp, clip, seed, wire_only=True)
B = old.fig_bbox(sp, clip, seed)
print('旧素材线框 mm %.2f×%.2f  旧素材全墨 mm %.2f×%.2f' % (W.width/PT, W.height/PT, B.width/PT, B.height/PT))
ib = old.ink_bbox(sp, clip)
print('旧素材整页墨bbox mm %.2f×%.2f' % ((ib[2]-ib[0])/PT, (ib[3]-ib[1])/PT))
