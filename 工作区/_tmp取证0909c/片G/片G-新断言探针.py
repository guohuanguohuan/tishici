# -*- coding: utf-8 -*-
r"""片G 0910 图下置·新断言口径探针（为 _测v4断言.py ⑱族/⑮/N6 适配取实测值）。

图认定＝「非轴对齐矢量墨」簇（同 断言顶格.py (e) 新口径：簇内跨度 ≥5mm 的斜长笔 ≥3；
        同 y 带 x 隙 ≤20mm 并簇 → 三联三子图成一簇）。
逐簇打印：阅读序（页,栏,y）／簇墨 rect／声明盒（置宽 W＋栏心）／盒内余量（左右）／
        上邻正文行底→簇顶（前距）／簇底→下邻正文行顶（下距）／上邻行文本前 18 字。
正文行判据：同栏、行宽 ≥15mm、且不与簇 rect（外扩 0.5mm）相交——图内标签系窄块，天然排除。
"""
import re
import pymupdf

PT = 72 / 25.4
MARGIN = 17.2 * PT
COLSEP = 7.6 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = (MARGIN, MARGIN + COLW + COLSEP)
BOT = 20 * PT
MINLONG = 3
BODYW = 15.0 * PT
MAIN = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
# 阅读序＝body.tex 中 \input{figs/…} 行序；W＝\resizebox 声明宽（\linewidth＝84.0mm）
SPEC = [('g6-triple', 84.0), ('g1-prism', 41.1), ('g2-cubeE', 42.0),
        ('g3-cube6', 84.0), ('g4-dihedral', 66.3), ('g5-fold', 54.7)]


def diag_items(dr):
    out = []
    for o in dr:
        for it in o['items']:
            if it[0] == 'l':
                p1, p2 = it[1], it[2]
                dx, dy = abs(p2.x - p1.x), abs(p2.y - p1.y)
                if dx > 1.0 and dy > 1.0 and max(dx, dy) / PT > 2.0:
                    out.append((pymupdf.Rect(min(p1.x, p2.x) - .3, min(p1.y, p2.y) - .3,
                                             max(p1.x, p2.x) + .3, max(p1.y, p2.y) + .3),
                                max(dx, dy) / PT >= 5.0))
            elif it[0] == 'c':
                ps = it[1:5]
                xs = [q.x for q in ps]
                ys = [q.y for q in ps]
                w, h = max(xs) - min(xs), max(ys) - min(ys)
                if max(w, h) / PT > 2.0 and w > 1.0 and h > 1.0:
                    out.append((pymupdf.Rect(min(xs) - .3, min(ys) - .3, max(xs) + .3, max(ys) + .3),
                                max(w, h) / PT >= 5.0))
    return out


def vec_clusters(page):
    pairs = diag_items(page.get_drawings())
    rs = [pymupdf.Rect(a) for a, _ in pairs]
    lg = [1 if b else 0 for _, b in pairs]
    gap = 8 / 25.4 * PT
    par = list(range(len(rs)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    for i in range(len(rs)):
        for j in range(i + 1, len(rs)):
            a = pymupdf.Rect(rs[i])
            a.x0 -= gap; a.y0 -= gap; a.x1 += gap; a.y1 += gap
            if a.intersects(rs[j]):
                x, y = find(i), find(j)
                if x != y:
                    par[x] = y
    grp = {}
    for i in range(len(rs)):
        grp.setdefault(find(i), []).append(i)
    cs = []
    for g in grp.values():
        r = pymupdf.Rect(rs[g[0]])
        for k in g[1:]:
            r |= rs[k]
        cs.append([r, sum(lg[k] for k in g)])
    changed = True
    while changed:
        changed = False
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                a, b = cs[i][0], cs[j][0]
                if (min(a.y1, b.y1) - max(a.y0, b.y0) > -3 * PT
                        and max(a.x0, b.x0) - min(a.x1, b.x1) <= 20 * PT):
                    cs[i] = [a | b, cs[i][1] + cs[j][1]]
                    del cs[j]
                    changed = True
                    break
            if changed:
                break
    return [c for c in cs if c[1] >= MINLONG and c[0].width / PT >= 15 and c[0].height / PT >= 10]


def col_lines(page, cl):
    ls = []
    for b in page.get_text('dict')['blocks']:
        for ln in b.get('lines', []):
            r = pymupdf.Rect(ln['bbox'])
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t and r.width >= BODYW and cl - 2 <= (r.x0 + r.x1) / 2 <= cl + COLW + 2:
                ls.append((t, r))
    return ls


doc = pymupdf.open(MAIN)
rows = []
for pno, page in enumerate(doc, 1):
    for r, nlong in vec_clusters(page):
        col = 1 if r.x0 < MID else 2
        rows.append((pno, col, r.y0, r, nlong))
rows.sort(key=lambda x: (x[0], x[1], x[2]))
print('矢量图簇  命中', len(rows))
assert len(rows) == len(SPEC), '簇数≠6，须复核'
for (pno, col, _, r, nlong), (nm, W) in zip(rows, SPEC):
    cl = COLL[col - 1]
    cc = cl + COLW / 2
    bx0, bx1 = cc - W * PT / 2, cc + W * PT / 2
    ls = col_lines(doc[pno - 1], cl)
    g = pymupdf.Rect(r.x0 - 0.5, r.y0 - 0.5, r.x1 + 0.5, r.y1 + 0.5)
    out = [(t, lr) for t, lr in ls if not lr.intersects(g)]
    up = [(t, lr) for t, lr in out if lr.y1 <= r.y0]
    dn = [(t, lr) for t, lr in out if lr.y0 >= r.y1]
    upt = max(up, key=lambda z: z[1].y1) if up else ('—', None)
    dnt = min(dn, key=lambda z: z[1].y0) if dn else ('—', None)
    print(f'{nm:<11s} p{pno} c{col} 斜长笔{nlong:3d} 置宽{W:5.1f} '
          f'盒[{bx0:6.2f},{bx1:6.2f}] 墨[{r.x0:6.2f},{r.x1:6.2f}] '
          f'左余{r.x0 - bx0:+5.2f} 右余{bx1 - r.x1:+5.2f} 墨宽{r.width / PT:6.2f} 墨高{r.height / PT:6.2f} '
          f'盒心偏{((r.x0 + r.x1) / 2 - cc) / PT:+5.2f}mm '.replace('pt', '') +
          f'| 前距{(r.y0 - upt[1].y1) / PT:5.2f} 下距{((dnt[1].y0 - r.y1) / PT if dnt[1] else 99):5.2f} '
          f'| 上邻「{upt[0][:22]}」 下邻「{dnt[0][:22]}」')
