# -*- coding: utf-8 -*-
"""片E：⑱-2 同口径几何量（顶差/墨缝/右缘 ×5），对任意 PDF 运行。
用法：python 量_⑱2.py <pdf>"""
import sys
import pymupdf
import numpy as np
from PIL import Image as PILImage

PT = 72 / 25.4
MARGIN = 17.575 * PT
COLSEP = 9.25 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = (MARGIN, MARGIN + COLW + COLSEP)
pdf = sys.argv[1]
doc = pymupdf.open(pdf)
rows = []
for pno in range(1, len(doc) + 1):
    page = doc[pno - 1]
    infos = page.get_image_info(xrefs=True)
    if not infos:
        continue
    tlines = [(pymupdf.Rect(l['bbox']), ''.join(sp['text'] for sp in l['spans']))
              for b in page.get_text('dict')['blocks'] if b['type'] == 0 for l in b.get('lines', [])]
    for info in infos:
        rct = pymupdf.Rect(info['bbox'])
        cl2 = COLL[0] if rct.x0 < MID else COLL[1]
        if abs((rct.x0 + rct.x1) / 2 - cl2 - COLW / 2) / PT <= 3:
            continue
        near = [bb for bb, tt in tlines
                if bb.x0 >= cl2 - 2 and bb.x0 >= rct.x0 - COLW and bb.x1 <= rct.x0 + 5
                and bb.y1 < rct.y1 and bb.y0 > rct.y0 and (bb.x1 - bb.x0) > 20
                and not tt.lstrip().startswith('◆')]
        if not near:
            continue
        clip = pymupdf.Rect(cl2 - 2, rct.y0 - 8, cl2 + COLW + 2, rct.y1 + 8)
        pix = page.get_pixmap(dpi=600, clip=clip)
        a = np.array(PILImage.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')) < 128
        sc = pix.width / clip.width
        ix0, iy0 = (rct.x0 + 0.6 - clip.x0) * sc, (rct.y0 + 0.6 - clip.y0) * sc
        ix1, iy1 = (rct.x1 - 0.6 - clip.x0) * sc, (rct.y1 - 0.6 - clip.y0) * sc
        sub = a[int(iy0):int(iy1), int(ix0):int(ix1)]
        ys, xs = np.nonzero(sub)
        ink = [clip.x0 + (int(ix0) + xs.min()) / sc, clip.y0 + (int(iy0) + ys.min()) / sc,
               clip.x0 + (int(ix0) + xs.max()) / sc, clip.y0 + (int(iy0) + ys.max()) / sc]
        first = min(near, key=lambda bb: bb.y1)
        fx0, fy0 = (first[0] - clip.x0) * sc, (first[1] - 2 - clip.y0) * sc
        fx1, fy1 = (first[2] + 1 - clip.x0) * sc, (first[3] + 1 - clip.y0) * sc
        fsub = a[int(fy0):int(fy1), int(fx0):int(fx1)]
        fys, _ = np.nonzero(fsub)
        ftop = clip.y0 + (int(fy0) + fys.min()) / sc
        y0p, y1p = int((ink[1] - clip.y0) * sc), int((ink[3] - clip.y0) * sc)
        x_stop = int((rct.x0 - clip.x0) * sc) - 1
        x_start = int((cl2 - clip.x0) * sc)
        best = None
        for yy in range(max(0, y0p), min(a.shape[0], y1p)):
            nz = np.nonzero(a[yy, x_start:x_stop])[0]
            if len(nz):
                xr = clip.x0 + (x_start + nz.max()) / sc
                if best is None or xr > best:
                    best = xr
        topdiff = (ink[1] - ftop) / PT
        seam = (ink[0] - best) / PT
        right_edge = (cl2 + COLW - ink[2]) / PT
        rows.append((info['width'], topdiff, seam, right_edge))
for w, d, s, r in rows:
    print(f'{w}px 顶{d:+.2f} 缝{s:.2f} 右{r:.2f}')
print(f'n={len(rows)}')
