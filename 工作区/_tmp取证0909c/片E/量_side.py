# -*- coding: utf-8 -*-
"""片E 量测：main.pdf 中 5 组 side 图——墨级几何＋图带内/图底以下文字行（右缘/通栏判定）。
用法：python 量_side.py [pdf]  （默认 variantF/main.pdf）"""
import os, sys, re
import pymupdf
import numpy as np
from PIL import Image as PILImage

PT = 72 / 25.4
MARGIN = 17.575 * PT
COLSEP = 9.25 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = (MARGIN, MARGIN + COLW + COLSEP)

pdf = sys.argv[1] if len(sys.argv) > 1 else r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
doc = pymupdf.open(pdf)
print(f'# {pdf} pages={len(doc)}')
print('img | p  x0 y0 x1 y1 | ink_top topdiff ink_bot | seam right | 带内行 图底以下行(右缘/栏右−右缘/通栏?)')

rows = []
for pno, page in enumerate(doc, 1):
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
        # 墨 bbox（600dpi 同 ⑱-2 口径）
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
        near = [(bb, tt) for bb, tt in tlines
                if bb.x0 >= cl2 - 2 and bb.x0 >= rct.x0 - COLW and bb.x1 <= rct.x0 + 5
                and bb.y1 < rct.y1 and bb.y0 > rct.y0 and (bb.x1 - bb.x0) > 20
                and not tt.lstrip().startswith('◆')]
        below = [(bb, tt) for bb, tt in tlines
                 if bb.x0 >= cl2 - 2 and bb.x1 <= cl2 + COLW + 2 and bb.y0 >= ink[3] - 1.0
                 and (bb.x1 - bb.x0) > 20]
        # 图带内文墨右缘（seam 用）
        best = None
        x_stop = int((rct.x0 - clip.x0) * sc) - 1
        x_start = int((cl2 - clip.x0) * sc)
        for yy in range(max(0, int((ink[1] - clip.y0) * sc)), min(a.shape[0], int((ink[3] - clip.y0) * sc))):
            nz = np.nonzero(a[yy, x_start:x_stop])[0]
            if len(nz):
                xr = clip.x0 + (x_start + nz.max()) / sc
                if best is None or xr > best:
                    best = xr
        topdiff = (ink[1] - min(bb.y0 for bb, _ in near)) / PT if near else float('nan')
        seam = (ink[0] - best) / PT if best else float('nan')
        right = (cl2 + COLW - ink[2]) / PT
        name = info.get('digest') and 'img'
        rows.append((pno, rct, ink, topdiff, seam, right, near, below))
        print(f'p{pno} x[{rct.x0:.1f},{rct.x1:.1f}] y[{rct.y0:.1f},{rct.y1:.1f}] | ink_top {ink[1]:.1f} topdiff {topdiff:+.2f} ink_bot {ink[3]:.1f} | '
              f'seam {seam:.2f} right {right:.2f} | 带内 {len(near)} 行')
        for bb, tt in sorted(near + below, key=lambda z: z[0].y0):
            tag = '带内' if bb.y0 < ink[3] else '图底以下'
            full = '通栏' if bb.x1 >= cl2 + COLW - 5 * PT else ''
            print(f'    {tag} y[{bb.y0:.1f},{bb.y1:.1f}] x[{bb.x0:.1f},{bb.x1:.1f}] '
                  f'右缘距栏右 {(cl2 + COLW - bb.x1) / PT:.2f}mm {full}  {tt[:44]}')
