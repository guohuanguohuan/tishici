# -*- coding: utf-8 -*-
"""读 _tabcal.pdf：按变体标签定位表格，输出表头/首行(2行格)/末行 行高与净空（600dpi ink）。"""
import re
import numpy as np
import pymupdf

PT = 72 / 25.4
DPI = 600
PXMM = 25.4 / DPI
THR = 128

doc = pymupdf.open('_tabcal.pdf')
labels = {}
for pno, page in enumerate(doc, 1):
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            m = re.match(r'^(W\d+) E=(\S+) G=(\S+) Gh=(\S+) top=(\S+) bot=(\S+)$', t)
            if m:
                labels.setdefault(pno, []).append((ln['bbox'][3], m.groups()))


def rules(page):
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
    return hrs, vrs


def cell_pads(page, x0, x1, y0, y1, wt, wb):
    clip = pymupdf.Rect(x0, y0, x1, y1)
    pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY, clip=clip)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    dark = a < THR
    if dark.sum() < 30:
        return None
    ys, xs = np.where(dark)
    inked = dark.any(axis=1)
    idx = np.flatnonzero(inked)
    nl, prev = 1, idx[0]
    for v in idx[1:]:
        if (v - prev) * PXMM > 0.6:
            nl += 1
        prev = v
    offT = (1.6 - wt / 2) * 25.4 / 72
    offB = (1.6 - wb / 2) * 25.4 / 72
    return (ys.min() * PXMM + offT, (pix.height - 1 - ys.max()) * PXMM + offB, nl)


for pno, page in enumerate(doc, 1):
    if pno not in labels:
        continue
    hrs, vrs = rules(page)
    for y_lab, (name, E, G, Gh, top, bot) in sorted(labels[pno]):
        cand = []
        for h, w in sorted(hrs, key=lambda x: x[0].y0):
            r = h
            if r.y0 <= y_lab + 2:
                continue
            n = sum(1 for v in vrs if v.y0 - 1 <= r.y0 <= v.y1 + 1 and r.x0 - 1.5 <= v.x0 <= r.x1 + 1.5)
            if n >= 2:
                cand.append((h, w))
        rs = []
        for h in cand:
            if not rs or h[0].y0 - rs[-1][0].y0 < 60:
                rs.append(h)
            else:
                break
        if len(rs) < 4:
            print(f'== {name} E={E} G={G} Gh={Gh} top={top} bot={bot}: 横线不足 ({len(rs)})')
            continue
        print(f'== {name} E={E} G={G} Gh={Gh} top={top} bot={bot}')
        for ri, tag in ((0, '表头'), (1, '零向量'), (len(rs) - 2, '末行')):
            (rt, wt), (rb, wb) = rs[ri], rs[ri + 1]
            h_mm = (rb.y0 - rt.y0) / PT
            xs = sorted(set(round(v.x0, 2) for v in vrs
                            if v.y0 - 1 <= rt.y0 <= v.y1 + 1 or v.y0 - 1 <= rb.y0 <= v.y1 + 1))
            cells = []
            for ci in range(len(xs) - 1):
                xx0, xx1 = xs[ci] + 2.0, xs[ci + 1] - 2.0
                if xx1 - xx0 < 6:
                    continue
                p = cell_pads(page, xx0, xx1, rt.y0 + 1.6, rb.y0 - 1.6, wt, wb)
                if p:
                    cells.append(f'c{ci}({p[2]}行) T{p[0]:5.2f} B{p[1]:5.2f}')
            print(f'   {tag} 行高{h_mm:5.2f}mm  ' + ' | '.join(cells))
