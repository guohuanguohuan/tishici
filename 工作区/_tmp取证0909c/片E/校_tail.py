# -*- coding: utf-8 -*-
"""片E 尾胶标定：对每组 side 图找「侵入图带」的文字行（x 与图墨重叠且墨顶在图墨底之上），
算所需尾胶增量 = (图墨底+目标缝) − 侵入行墨顶。用法：python 校_tail.py [pdf]"""
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
GAP = 2.4  # pt，目标：图墨底→下块首行墨顶（沿现行布局 2.4pt 档）

pdf = sys.argv[1] if len(sys.argv) > 1 else r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
doc = pymupdf.open(pdf)
print(f'# {pdf} pages={len(doc)}')
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
        # 侵入行：同栏、墨 bbox 与图墨 x 带重叠、墨顶 < 图墨底+目标缝
        bad = [(bb, tt) for bb, tt in tlines
               if bb.x0 >= cl2 - 2 and bb.x1 > ink[0] + 1 and bb.x0 < ink[2]
               and bb.y0 < ink[3] + GAP and bb.y1 > ink[1]
               and (bb.x1 - bb.x0) > 20]
        need = 0.0
        if bad:
            need = ((ink[3] + GAP) - min(bb.y0 for bb, _ in bad)) / PT
        print(f'p{pno} 图 x[{rct.x0:.1f},{rct.x1:.1f}] 墨底 {ink[3]:.1f} | 侵入行 {len(bad)} 需尾胶增量 {need:+.2f}mm')
        for bb, tt in sorted(bad, key=lambda z: z[0].y0)[:4]:
            print(f'     y[{bb.y0:.1f},{bb.y1:.1f}] x[{bb.x0:.1f},{bb.x1:.1f}] {tt[:44]}')
