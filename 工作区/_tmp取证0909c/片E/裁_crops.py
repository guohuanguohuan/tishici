# -*- coding: utf-8 -*-
"""片E 裁片：改前/改后对照＋「图下方通栏」实锤标注。
用法：python 裁_crops.py before|after
  before：对当前 main.pdf 按改前口径出 5 组裁片（重建基线 PDF 后调用）
  after ：出 5 组裁片＋标注（图墨底横线／图底以下首行右缘实锤）"""
import sys, os
import pymupdf
import numpy as np
from PIL import Image as PILImage, ImageDraw

OUT = r'C:\提示词\工作区\_tmp取证0909c\片E'
PT = 72 / 25.4
MARGIN = 17.575 * PT
COLSEP = 9.25 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = (MARGIN, MARGIN + COLW + COLSEP)
# 组：名 → (页, 裁片 PDF 矩形)  探九改后位置上移，矩形放宽覆盖前后
CROPS = {
    '探二': (3, (300, 440, 565, 640)),
    '探三': (4, (40, 205, 300, 350)),
    '探六': (5, (40, 360, 300, 500)),
    '探八': (6, (40, 270, 300, 400)),
    '探九': (6, (300, 185, 565, 360)),
}
mode = sys.argv[1] if len(sys.argv) > 1 else 'after'
doc = pymupdf.open(r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf')
print('pages', len(doc))
for g, (pno, rect) in CROPS.items():
    page = doc[pno - 1]
    clip = pymupdf.Rect(*rect)
    pix = page.get_pixmap(dpi=300, clip=clip)
    im = PILImage.frombytes('RGB', (pix.width, pix.height), pix.samples)
    if mode == 'after':
        # 找该栏 side 图的墨 bbox（600dpi 同断言口径），画图底横线＋通栏标注
        infos = page.get_image_info(xrefs=True)
        sc300 = 300 / 72.0
        for info in infos:
            rct = pymupdf.Rect(info['bbox'])
            cl2 = COLL[0] if rct.x0 < MID else COLL[1]
            if not (rct.x0 >= rect[0] - 10 and rct.x1 <= rect[2] + 10):
                continue
            if not (rct.y0 > rect[1] - 60 and rct.y1 < rect[3] + 60):
                continue
            if abs((rct.x0 + rct.x1) / 2 - cl2 - COLW / 2) / PT <= 3:
                continue
            clip2 = pymupdf.Rect(cl2 - 2, rct.y0 - 8, cl2 + COLW + 2, rct.y1 + 8)
            p2 = page.get_pixmap(dpi=600, clip=clip2)
            a = np.array(PILImage.frombytes('RGB', (p2.width, p2.height), p2.samples).convert('L')) < 128
            sc = p2.width / clip2.width
            iy0 = (rct.y0 + 0.6 - clip2.y0) * sc
            iy1 = (rct.y1 - 0.6 - clip2.y0) * sc
            ix0 = (rct.x0 + 0.6 - clip2.x0) * sc
            ix1 = (rct.x1 - 0.6 - clip2.x0) * sc
            sub = a[int(iy0):int(iy1), int(ix0):int(ix1)]
            ys, xs = np.nonzero(sub)
            ink_bot = clip2.y0 + (int(iy0) + ys.max()) / sc
            ink_l = clip2.x0 + (int(ix0) + xs.min()) / sc
            ink_r = clip2.x0 + (int(ix0) + xs.max()) / sc
            # 图底以下首行（同视觉行合并）
            tl = [(pymupdf.Rect(l['bbox']), ''.join(sp['text'] for sp in l['spans']))
                  for b in page.get_text('dict')['blocks'] if b['type'] == 0 for l in b.get('lines', [])]
            below = sorted([bb for bb, _ in tl if bb.x0 >= cl2 - 2 and bb.x1 <= cl2 + COLW + 2
                            and bb.y0 >= ink_bot - 1], key=lambda bb: bb.y0)
            d = ImageDraw.Draw(im)
            yb = (ink_bot - clip.y0) * sc300
            d.line([(0, yb), (im.width, yb)], fill=(255, 0, 0), width=2)
            if below:
                y0f = below[0].y0
                grp = [bb for bb in below if bb.y0 - y0f < 3.0]
                xr = max(bb.x1 for bb in grp)
                yb2 = (y0f - clip.y0) * sc300
                d.line([(0, yb2), ((xr - clip.x0) * sc300, yb2)], fill=(0, 140, 0), width=2)
                d.line([((cl2 + COLW - clip.x0) * sc300, yb2 - 14), ((cl2 + COLW - clip.x0) * sc300, yb2 + 14)],
                       fill=(0, 0, 255), width=2)
                d.text(((xr - clip.x0) * sc300 + 4, yb2 - 20),
                       f'图底以下首行右缘距栏右 {(cl2 + COLW - xr) / PT:.2f}mm', fill=(0, 120, 0))
            d.text((4, yb - 18), f'图墨底 y={ink_bot:.1f}pt', fill=(200, 0, 0))
            break
    p = os.path.join(OUT, f'{mode}_p{pno}_{g}.png')
    im.save(p)
    print(p, im.size)
