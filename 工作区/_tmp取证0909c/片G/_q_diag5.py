# -*- coding: utf-8 -*-
"""探针：为何 run4【五】复算的素材旧线框＝纯线网（未吞标签），与历史 71.29×72.09 不符。"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pymupdf
import importlib.util
spec = importlib.util.spec_from_file_location('aw', '权威实测.py')
aw = importlib.util.module_from_spec(spec); spec.loader.exec_module(aw)
PT = aw.PT
SRC = aw.SRC

sd = pymupdf.open(SRC + 'tikz_tan6.pdf'); sp = sd[0]
stk = aw.strokes(sp)
cs = aw.clusters(stk)
srect = pymupdf.Rect(cs[0][0])
for c in cs[1:]:
    srect |= c[0]
seed = [i for c in cs for i in c[2]]
print('簇数', len(cs), '簇rect(mm)', [ ('%.2f×%.2f @ [%.2f,%.2f]x[%.2f,%.2f]' % (c[0].width/PT, c[0].height/PT, c[0].x0/PT, c[0].x1/PT, c[0].y0/PT, c[0].y1/PT)) for c in cs ])
print('srect mm  x[%.2f,%.2f] y[%.2f,%.2f]  w=%.2f h=%.2f' % (srect.x0/PT, srect.x1/PT, srect.y0/PT, srect.y1/PT, srect.width/PT, srect.height/PT))
clip = pymupdf.Rect(sp.rect.x0+0.1, sp.rect.y0+0.1, sp.rect.x1-0.1, sp.rect.y1-0.1)
A = aw.ink_mask(sp, clip)
comp = aw.comps_rect(A, clip.x0, clip.y0, minpix=1, dilate=2)
S = pymupdf.Rect(srect.x0-1, srect.y0-1, srect.x1+1, srect.y1+1)
print('seed(旧,±1pt) mm x[%.2f,%.2f] y[%.2f,%.2f]' % (S.x0/PT, S.x1/PT, S.y0/PT, S.y1/PT))
print('连通域数', len(comp))
big = sorted(comp, key=lambda r: -r.width*r.height)
for r in big[:14]:
    print('  comp mm x[%7.2f,%7.2f] y[%7.2f,%7.2f] w%6.2f h%6.2f  intersect_seed=%s' % (
        r.x0/PT, r.x1/PT, r.y0/PT, r.y1/PT, r.width/PT, r.height/PT, r.intersects(S)))
U = None
for r in comp:
    if r.intersects(S):
        U = pymupdf.Rect(r) if U is None else (U | r)
print('旧法并集 mm w=%.2f h=%.2f' % (U.width/PT, U.height/PT))
