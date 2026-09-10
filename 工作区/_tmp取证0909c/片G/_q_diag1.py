# -*- coding: utf-8 -*-
r"""临时探针：比对件内 vs 素材的线框连通域清单，找 Δ 来源。"""
import sys
sys.path.insert(0, r'C:/提示词/工作区/_tmp取证0909c/片G')
import pymupdf
from 片G实测 import (PT, MARGIN, COLW, COLSEP, MID, BOT, SRC, MAIN, MAP,
                    diag_items, cluster, merge_rows, ink_components, bboxes, col_lines)

TARGET = sys.argv[1] if len(sys.argv) > 1 else 'g3'

doc = pymupdf.open(MAIN)
# 件内：找出全部簇并打印
rows = []
for pno, page in enumerate(doc, 1):
    for r, nlong in merge_rows(cluster(diag_items(page.get_drawings()), 8 / 25.4 * PT)):
        if r.width / PT < 15 or r.height / PT < 10 or nlong < 3:
            continue
        rows.append((pno, r, nlong))
rows.sort(key=lambda z: (z[0], z[1].y0))
print('件内簇数', len(rows))
for i, (pno, r, nlong) in enumerate(rows):
    print(' [%d] p%d 簇rect(mm) x[%.2f,%.2f] y[%.2f,%.2f]  %.2f×%.2f 斜长笔%d'
          % (i, pno, r.x0 / PT, r.x1 / PT, r.y0 / PT, r.y1 / PT, r.width / PT, r.height / PT, nlong))

idx = {'g6': 0, 'g1': 1, 'g2': 2, 'g3': 3, 'g4': 4, 'g5': 5}[TARGET]
pno, r, nlong = rows[idx]
tag, sn, wbox, frag = MAP[idx]
col = 1 if r.x0 < MID else 2
cl = MARGIN if col == 1 else MARGIN + COLW + COLSEP
page = doc[pno - 1]
band = pymupdf.Rect(cl + 0.4, max(MARGIN - 2, r.y0 - 14 * PT),
                    cl + COLW - 0.4, min(page.rect.height - BOT + 2, r.y1 + 14 * PT))
seed = pymupdf.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1)
comps = ink_components(page, band)
wire = [c for c in comps if c.intersects(seed)]
full = bboxes(comps, seed)
print('\n=== 件内 %s (p%d c%d) band y[%.2f,%.2f] seed %.2f×%.2f  连通域%d 其中交种子%d'
      % (tag, pno, col, band.y0 / PT, band.y1 / PT, seed.width / PT, seed.height / PT, len(comps), len(wire)))
w0 = wire[0]
for c in wire[1:]:
    w0 |= c
print('  线框并 %.2f×%.2f  x[%.2f,%.2f] y[%.2f,%.2f]' % (w0.width / PT, w0.height / PT, w0.x0 / PT, w0.x1 / PT, w0.y0 / PT, w0.y1 / PT))
print(' 交种子域清单(mm) x0 y0 x1 y1 w h npx:')
for c in sorted(wire, key=lambda z: (z.y0, z.x0)):
    print('   %7.2f %7.2f %7.2f %7.2f  %6.2f %6.2f' % (c.x0 / PT, c.y0 / PT, c.x1 / PT, c.y1 / PT, c.width / PT, c.height / PT))
print(' 不交种子域(潜在标签/污染):')
for c in sorted([c for c in comps if not c.intersects(seed)], key=lambda z: (z.y0, z.x0)):
    inside = w0.contains(c) if False else None
    print('   %7.2f %7.2f %7.2f %7.2f  %6.2f %6.2f  在线框并内=%s' % (
        c.x0 / PT, c.y0 / PT, c.x1 / PT, c.y1 / PT, c.width / PT, c.height / PT,
        (c.x0 >= w0.x0 - .1 and c.x1 <= w0.x1 + .1 and c.y0 >= w0.y0 - .1 and c.y1 <= w0.y1 + .1)))

# 素材
d2 = pymupdf.open(SRC + sn)
p2 = d2[0]
rr = p2.rect
clip = pymupdf.Rect(rr.x0 + 0.2, rr.y0 + 0.2, rr.x1 - 0.2, rr.y1 - 0.2)
comps2 = ink_components(p2, clip)
cs2 = merge_rows(cluster(diag_items(p2.get_drawings()), 8 / 25.4 * PT))
cs2 = [c for c in cs2 if c[0].width / PT >= 15 and c[0].height / PT >= 10 and c[1] >= 3]
seed2 = pymupdf.Rect(cs2[0][0])
for extra, _n in cs2[1:]:
    seed2 |= extra
seed2 = pymupdf.Rect(seed2.x0 - 1, seed2.y0 - 1, seed2.x1 + 1, seed2.y1 + 1)
wire2 = [c for c in comps2 if c.intersects(seed2)]
k = wbox / (rr.width / PT)
print('\n=== 素材 %s  页 %.2f×%.2f  k=%.4f  簇数%d 种子 %.2f×%.2f  连通域%d 交种子%d'
      % (sn, rr.width / PT, rr.height / PT, k, len(cs2), seed2.width / PT, seed2.height / PT, len(comps2), len(wire2)))
u2 = wire2[0]
for c in wire2[1:]:
    u2 |= c
print('  素材线框并 %.2f×%.2f  ×k=%.2f×%.2f  x[%.2f,%.2f] y[%.2f,%.2f]' % (
    u2.width / PT, u2.height / PT, u2.width * k / PT, u2.height * k / PT, u2.x0 / PT, u2.x1 / PT, u2.y0 / PT, u2.y1 / PT))
print(' 素材交种子域(mm, 已×k 折件内尺寸) 按宽降序:')
for c in sorted(wire2, key=lambda z: -(z.width * z.height)):
    print('   %7.2f %7.2f  w%6.2f h%6.2f  →折 w%6.2f h%6.2f' % (
        c.x0 / PT, c.y0 / PT, c.width / PT, c.height / PT, c.width * k / PT, c.height * k / PT))
print('\n 素材不交种子域:')
for c in sorted([c for c in comps2 if not c.intersects(seed2)], key=lambda z: -(z.width * z.height)):
    print('   %7.2f %7.2f %7.2f %7.2f  w%6.2f h%6.2f →折 w%6.2f h%6.2f' % (
        c.x0 / PT, c.y0 / PT, c.x1 / PT, c.y1 / PT, c.width / PT, c.height / PT, c.width * k / PT, c.height * k / PT))
