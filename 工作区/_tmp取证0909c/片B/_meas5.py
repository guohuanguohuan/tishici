# -*- coding: utf-8 -*-
"""测 _tabcal5.pdf 两张表（A1 auto / A2 fixed）逐行行高与逐格净空。"""
import sys
import numpy as np
import pymupdf

PDF = sys.argv[1] if len(sys.argv) > 1 else '_tabcal5.pdf'
PT = 72 / 25.4
DPI = 600
PXMM = 25.4 / DPI
THR = 128

doc = pymupdf.open(PDF)
for pno, page in enumerate(doc, 1):
    hrs, vrs = [], []
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c:
            continue
        if tuple(round(x * 255) for x in c) not in ((122, 122, 122), (0, 0, 0)):
            continue
        if r.width > 15 * PT and r.height < 3:
            hrs.append((r, (d.get('width') or 0) / PT))
        elif r.height > 5 * PT and r.width < 3:
            vrs.append(r)
    cand = [(h, w) for h, w in sorted(hrs, key=lambda x: x[0].y0)
            if sum(1 for v in vrs if v.y0 - 1 <= h.y0 <= v.y1 + 1 and h.x0 - 1.5 <= v.x0 <= h.x1 + 1.5) >= 2]
    groups = []
    cur = []
    for h in cand:
        if not cur or h[0].y0 - cur[-1][0].y0 < 60:
            cur.append(h)
        else:
            if len(cur) >= 3:
                groups.append(cur)
            cur = [h]
    if len(cur) >= 3:
        groups.append(cur)
    for gi, rs in enumerate(groups):
        print(f'== p{pno} 表{gi + 1} ==')
        for ri in range(len(rs) - 1):
            (rt, wt), (rb, wb) = rs[ri], rs[ri + 1]
            xs = sorted(set(round(v.x0, 2) for v in vrs
                            if v.y0 - 1 <= rt.y0 <= v.y1 + 1 or v.y0 - 1 <= rb.y0 <= v.y1 + 1))
            cells = []
            for ci in range(len(xs) - 1):
                xx0, xx1 = xs[ci] + 2.0, xs[ci + 1] - 2.0
                if xx1 - xx0 < 6:
                    continue
                clip = pymupdf.Rect(xx0, rt.y0 + 1.6, xx1, rb.y0 - 1.6)
                pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY, clip=clip)
                a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
                dark = a < THR
                if dark.sum() < 30:
                    continue
                ys, x2 = np.where(dark)
                offT = (1.6 - wt / 2) * 25.4 / 72
                offB = (1.6 - wb / 2) * 25.4 / 72
                cells.append(f'c{ci} T{ys.min() * PXMM + offT:5.2f} B{(pix.height - 1 - ys.max()) * PXMM + offB:5.2f}')
            print(f'   r{ri} 行高{(rb.y0 - rt.y0) / PT:5.2f}mm  ' + ' | '.join(cells))
