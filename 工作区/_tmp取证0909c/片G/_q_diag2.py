# -*- coding: utf-8 -*-
r"""临时探针2：件内簇 vs 素材簇 的矢量条目几何对照。"""
import sys
sys.path.insert(0, r'C:/提示词/工作区/_tmp取证0909c/片G')
import pymupdf
from 片G实测 import PT, SRC, MAIN, MAP, diag_items, cluster, merge_rows

which = sys.argv[1]
idx = {'g6': 0, 'g1': 1, 'g2': 2, 'g3': 3, 'g4': 4, 'g5': 5}[which]
tag, sn, wbox, frag = MAP[idx]


def items_dump(page, label, seedrect=None):
    dr = page.get_drawings()
    n = 0
    boxes = []
    for o in dr:
        for it in o['items']:
            kind = it[0]
            if kind == 'l':
                p1, p2 = it[1], it[2]
                r = pymupdf.Rect(p1.x, p1.y, p2.x, p2.y)
                r.normalize()
                typ = 'L'
            elif kind == 'c':
                ps = it[1:5]
                xs = [q.x for q in ps]
                ys = [q.y for q in ps]
                r = pymupdf.Rect(min(xs), min(ys), max(xs), max(ys))
                typ = 'C'
            elif kind == 're':
                r = pymupdf.Rect(it[1])
                typ = 'R'
            elif kind == 'qu':
                r = pymupdf.Rect(it[1])
                typ = 'Q'
            else:
                typ = kind
                r = pymupdf.Rect(o['rect'])
            n += 1
            if seedrect is not None and not r.intersects(seedrect):
                continue
            boxes.append((typ, r, o.get('color'), o.get('fill'), o.get('width')))
    print('  %s 页 %.2f×%.2f  drawings对象总bbox条目%d  入选%d' % (label, page.rect.width / PT, page.rect.height / PT, n, len(boxes)))
    U = None
    for t, r, c, f, wd in boxes:
        U = pymupdf.Rect(r) if U is None else (U | r)
    if U:
        print('   全部条目并: x[%.2f,%.2f] y[%.2f,%.2f] %.2f×%.2f' % (U.x0 / PT, U.x1 / PT, U.y0 / PT, U.y1 / PT, U.width / PT, U.height / PT))
    # 分类统计
    longdiag = [b for b in boxes if b[0] in 'LC' and max(b[1].width, b[1].height) / PT >= 5]
    print('   跨度≥5mm 的 L/C 条目 %d；其中斜向(dx>1,dy>1) %d' % (
        len(longdiag),
        sum(1 for t, r, *_ in longdiag if r.width > 1.0 and r.height > 1.0)))
    ax = [b for b in boxes if b[0] in 'LC' and (b[1].width <= 1.0 or b[1].height <= 1.0)]
    print('   轴对齐 L/C 条目 %d  其他(re/qu/fill) %d' % (len(ax), len(boxes) - len(longdiag) - len(ax)))
    # 打印超出某矩形的条目
    return boxes


doc = pymupdf.open(MAIN)
allc = []
for pno, page in enumerate(doc, 1):
    for r, nl in merge_rows(cluster(diag_items(page.get_drawings()), 8 / 25.4 * PT)):
        if r.width / PT >= 15 and r.height / PT >= 10 and nl >= 3:
            allc.append((pno, r, nl))
allc.sort(key=lambda z: (z[0], z[1].y0))
pno, rc, nl = allc[idx]
print('=== 件内 %s  p%d  簇rect x[%.2f,%.2f] y[%.2f,%.2f] %.2f×%.2f 斜长笔%d' % (
    tag, pno, rc.x0 / PT, rc.x1 / PT, rc.y0 / PT, rc.y1 / PT, rc.width / PT, rc.height / PT, nl))
b1 = items_dump(doc[pno - 1], '件内页', pymupdf.Rect(rc.x0 - 3, rc.y0 - 3, rc.x1 + 3, rc.y1 + 3))

d2 = pymupdf.open(SRC + sn)
p2 = d2[0]
cs2 = [c for c in merge_rows(cluster(diag_items(p2.get_drawings()), 8 / 25.4 * PT))
       if c[0].width / PT >= 15 and c[0].height / PT >= 10 and c[1] >= 3]
print('\n=== 素材 %s  簇数%d' % (sn, len(cs2)))
for r, m in cs2:
    print('   素材簇 x[%.2f,%.2f] y[%.2f,%.2f] %.2f×%.2f 斜长笔%d' % (
        r.x0 / PT, r.x1 / PT, r.y0 / PT, r.y1 / PT, r.width / PT, r.height / PT, m))
seed2 = pymupdf.Rect(cs2[0][0])
for e, _ in cs2[1:]:
    seed2 |= e
b2 = items_dump(p2, '素材页', seed2)
k = wbox / (p2.rect.width / PT)
print('\n  素材条目折算件内（×%.4f）后与件内对照：件内线框簇 %.2f×%.2f 素材 %.2f×%.2f→%.2f×%.2f' % (
    k, rc.width / PT, rc.height / PT, seed2.width / PT, seed2.height / PT, seed2.width * k / PT, seed2.height * k / PT))
# 素材中超出种子（=线网）的条目 = 可能是标签？矢量？
print('\n  素材全部 L/C 条目中最靠边者（x0 最小 5 个 / y1 最大 5 个）：')
lc = [b for b in b2 if b[0] in 'LC']
for t, r, c, f, wd in sorted(lc, key=lambda z: z[1].x0)[:5]:
    print('    x0=%6.2f y[%.2f,%.2f] %6.2f×%6.2f %s color=%s fill=%s w=%s' % (r.x0 / PT, r.y0 / PT, r.y1 / PT, r.width / PT, r.height / PT, t, c, f, wd))
for t, r, c, f, wd in sorted(lc, key=lambda z: -z[1].y1)[:5]:
    print('    y1=%6.2f x[%.2f,%.2f] %6.2f×%6.2f %s color=%s fill=%s w=%s' % (r.y1 / PT, r.x0 / PT, r.x1 / PT, r.width / PT, r.height / PT, t, c, f, wd))
