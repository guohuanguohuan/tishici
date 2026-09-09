# -*- coding: utf-8 -*-
"""通用：读 PDF（第 1 参）+ 标签前缀（第 2 参），输出各表逐行行高与逐格净空。"""
import re
import sys
import numpy as np
import pymupdf

PDF = sys.argv[1] if len(sys.argv) > 1 else '_tabcal3.pdf'
PREF = sys.argv[2] if len(sys.argv) > 2 else 'Y'
PT = 72 / 25.4
DPI = 600
PXMM = 25.4 / DPI
THR = 128

doc = pymupdf.open(PDF)
labels = {}
for pno, page in enumerate(doc, 1):
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            m = re.match(r'^(' + PREF + r'\d+) E=(\S+) G=(\S+) Gh=(\S+)(?: lG=(\S+))?$', t)
            if m:
                labels.setdefault(pno, []).append((ln['bbox'][3], m.groups()))

for pno, page in enumerate(doc, 1):
    if pno not in labels:
        continue
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
    for y_lab, grp in sorted(labels[pno]):
        name, E, G, Gh = grp[0], grp[1], grp[2], grp[3]
        lG = grp[4] if len(grp) > 4 and grp[4] else '-'
        cand = [(h, w) for h, w in sorted(hrs, key=lambda x: x[0].y0)
                if h.y0 > y_lab + 2 and
                sum(1 for v in vrs if v.y0 - 1 <= h.y0 <= v.y1 + 1 and h.x0 - 1.5 <= v.x0 <= h.x1 + 1.5) >= 2]
        rs = []
        for h in cand:
            if not rs or h[0].y0 - rs[-1][0].y0 < 60:
                rs.append(h)
            else:
                break
        if len(rs) < 3:
            print(name, '横线不足', len(rs))
            continue
        print(f'== {name} E={E} G={G} Gh={Gh} lG={lG}')
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
