# -*- coding: utf-8 -*-
"""绕图回流0910 探针：g1（image1 691px）/g2（image2 764px）并排带——
逐行列出「文行 bbox／600dpi 真墨右缘」＋图真墨底，判有无「图底以下余段」（同段文字行落在图墨底之下）。
口径：同栏正文行；行归属＝与图带垂直重叠（旁行）或墨顶 ≥ 图墨底−1pt（下延行）。"""
import os
import pymupdf
import numpy as _np
from PIL import Image as _PILImage

BASE = r'C:\提示词\工作区\字替对照-0909\variantF'
PT = 72 / 25.4
COLL = [17.2 * PT, 17.2 * PT + 84.0 * PT + 7.6 * PT]
COLW = 84.0 * PT
NAT = {}


def ink_nat(name):
    if name in NAT:
        return NAT[name]
    im = _PILImage.open(os.path.join(BASE, 'media', 'media', name))
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = _PILImage.new('RGBA', im.size, (255, 255, 255, 255))
        im = _PILImage.alpha_composite(bg, im.convert('RGBA'))
    a = _np.asarray(im.convert('L')) < 128
    ys, xs = _np.nonzero(a)
    NAT[name] = (xs.min() / a.shape[1], ys.min() / a.shape[0],
                 (xs.max() + 1) / a.shape[1], (ys.max() + 1) / a.shape[0])
    return NAT[name]


def line_ink600(page, r):
    pm = page.get_pixmap(dpi=600, colorspace=pymupdf.csGRAY, clip=r)
    a = _np.frombuffer(pm.samples, dtype=_np.uint8).reshape(pm.height, pm.width)
    m = a < 128
    if not m.any():
        return None
    ys, xs = _np.nonzero(m)
    sc = 72.0 / 600
    return pymupdf.Rect(r.x0 + xs.min() * sc, r.y0 + ys.min() * sc,
                        r.x0 + (xs.max() + 1) * sc, r.y0 + (ys.max() + 1) * sc)


doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
print('pages', doc.page_count)
for pno in range(1, doc.page_count + 1):
    pg = doc[pno - 1]
    for info in pg.get_image_info(xrefs=True):
        if info['width'] not in (691, 764):
            continue
        tag, nm = ('g1', 'image1.png') if info['width'] == 691 else ('g2', 'image2.png')
        r = pymupdf.Rect(info['bbox'])
        cl = COLL[0] if (r.x0 + r.x1) / 2 < (COLL[0] + COLL[1]) / 2 else COLL[1]
        fx0, fy0, fx1, fy1 = ink_nat(nm)
        ir = pymupdf.Rect(r.x0 + fx0 * r.width, r.y0 + fy0 * r.height,
                          r.x0 + fx1 * r.width, r.y0 + fy1 * r.height)
        print(f'\n=== {tag} {nm} p{pno} 栏左{cl / PT:.1f} 栏右{(cl + COLW) / PT:.1f}'
              f' 盒 x[{r.x0 / PT:.2f},{r.x1 / PT:.2f}] y[{r.y0 / PT:.2f},{r.y1 / PT:.2f}]'
              f' 真墨 x[{ir.x0 / PT:.2f},{ir.x1 / PT:.2f}] y[{ir.y0 / PT:.2f},{ir.y1 / PT:.2f}]'
              f' 墨高{ir.height / PT:.2f}mm 右缘{((cl + COLW) - ir.x1) / PT:.2f}mm')
        rows = []
        for b in pg.get_text('dict')['blocks']:
            if b['type'] != 0:
                continue
            for L in b.get('lines', []):
                bb = pymupdf.Rect(L['bbox'])
                if not (cl - 2 <= (bb.x0 + bb.x1) / 2 <= cl + COLW + 2):
                    continue
                t = ''.join(sp['text'] for sp in L['spans'])
                sp0 = max(L['spans'], key=lambda z: z['size'])['size']
                if sp0 < 8.6:      # 非正文（8pt 解析/9pt 等）粗筛
                    pass
                rows.append((bb, t, sp0))
        rows.sort(key=lambda z: z[0].y0)
        for bb, t, sp0 in rows:
            ov = min(bb.y1, ir.y1) - max(bb.y0, ir.y0)
            kind = '旁行' if ov > 1 else ('下延' if bb.y0 >= ir.y0 else '上邻')
            if kind == '上邻' and bb.y1 < ir.y0 - 2:
                continue
            ik = line_ink600(pg, bb)
            x1i = ik.x1 if ik else bb.x1
            print(f'  {kind} y[{bb.y0 / PT:7.2f},{bb.y1 / PT:7.2f}] 墨[{(ik.y0 if ik else bb.y0) / PT:7.2f},{(ik.y1 if ik else bb.y1) / PT:7.2f}]'
                  f' 墨右缘{x1i / PT:7.2f} 距栏右{((cl + COLW) - x1i) / PT:6.2f}mm sz{sp0:.1f} | {t[:56]}')
