# -*- coding: utf-8 -*-
"""复算 ⑱-3 对 image5（1798px）的 below 行选取。"""
import numpy as np
import pymupdf
from PIL import Image

doc = pymupdf.open(r'C:/提示词/工作区/_tmp取证0909c/片H2/档_FINAL.pdf')
PT = 72 / 25.4
MARGIN = 17.2 * PT
COLSEP = 7.6 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = (MARGIN, MARGIN + COLW + COLSEP)
for pno in range(doc.page_count):
    page = doc[pno]
    infos = page.get_image_info(xrefs=True)
    if not infos:
        continue
    tlines = [(pymupdf.Rect(l['bbox']), ''.join(sp['text'] for sp in l['spans']))
              for b in page.get_text('dict')['blocks'] if b['type'] == 0 for l in b.get('lines', [])]
    for info in infos:
        if info['width'] != 1798:
            continue
        rct = pymupdf.Rect(info['bbox'])
        print('p', pno + 1, 'rect', [round(v, 1) for v in rct])
        cl2 = COLL[0] if rct.x0 < MID else COLL[1]
        clip = pymupdf.Rect(cl2 - 2, rct.y0 - 8, cl2 + COLW + 2, rct.y1 + 8)
        pix = page.get_pixmap(dpi=600, clip=clip)
        a = np.array(Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')) < 128
        sc = pix.width / clip.width
        ix0, iy0 = (rct.x0 + 0.6 - clip.x0) * sc, (rct.y0 + 0.6 - clip.y0) * sc
        ix1, iy1 = (rct.x1 - 0.6 - clip.x0) * sc, (rct.y1 - 0.6 - clip.y0) * sc
        sub = a[int(iy0):int(iy1), int(ix0):int(ix1)]
        ys, xs = np.nonzero(sub)
        ink_bot = clip.y0 + (int(iy0) + ys.max()) / sc
        ink_l = clip.x0 + (int(ix0) + xs.min()) / sc
        print('  ink_bot', round(ink_bot, 1), 'ink_l', round(ink_l, 1))
        below = sorted([bb for bb, _ in tlines if bb.x0 >= cl2 - 2 and bb.x1 <= cl2 + COLW + 2 and bb.y0 >= ink_bot - 1],
                       key=lambda bb: bb.y0)
        for bb in below[:6]:
            txt = next(t for b2, t in tlines if b2 == bb)
            print('   below', [round(v, 1) for v in bb], repr(txt[:40]))
        if below:
            y0f = below[0].y0
            grp = [bb for bb in below if bb.y0 - y0f < 3.0]
            xr = max(bb.x1 for bb in grp)
            print('   redge mm =', round((cl2 + COLW - xr) / PT, 2))
