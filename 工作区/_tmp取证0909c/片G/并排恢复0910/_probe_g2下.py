# -*- coding: utf-8 -*-
"""g2 并排行下方 [分析] 行：bbox 顶 vs 600dpi 真墨顶，对图盒外扩 0.5mm 下缘。"""
import os
import pymupdf
import numpy as _np
from PIL import Image as _PILImage

BASE = r'C:\提示词\工作区\字替对照-0909\variantF'
PT = 72 / 25.4
doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
pg = doc[2]
for info in pg.get_image_info(xrefs=True):
    if info['width'] != 764:
        continue
    r = pymupdf.Rect(info['bbox'])
    infl = pymupdf.Rect(r.x0 - 0.5 * PT, r.y0 - 0.5 * PT, r.x1 + 0.5 * PT, r.y1 + 0.5 * PT)
    print('图盒 y[%.1f,%.1f] 外扩下缘 %.2f' % (r.y0, r.y1, infl.y1))
    # 图真墨底（原生 bbox 同比映射）
    im = _PILImage.open(os.path.join(BASE, 'media', 'media', 'image2.png')).convert('L')
    a = _np.asarray(im) < 128
    ys, xs = _np.nonzero(a)
    fx0, fy0 = xs.min() / a.shape[1], ys.min() / a.shape[0]
    fx1, fy1 = (xs.max() + 1) / a.shape[1], (ys.max() + 1) / a.shape[0]
    ir = pymupdf.Rect(r.x0 + fx0 * r.width, r.y0 + fy0 * r.height,
                      r.x0 + fx1 * r.width, r.y0 + fy1 * r.height)
    print('图真墨 y[%.2f,%.2f] 底%.2f' % (ir.y0, ir.y1, ir.y1))
    for b in pg.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for L in b.get('lines', []):
            bb = pymupdf.Rect(L['bbox'])
            t = ''.join(sp['text'] for sp in L['spans'])
            if '结合空间向量' not in t:
                continue
            pm = pg.get_pixmap(dpi=600, colorspace=pymupdf.csGRAY, clip=bb)
            g = _np.frombuffer(pm.samples, dtype=_np.uint8).reshape(pm.height, pm.width) < 128
            gy, gx = _np.nonzero(g)
            sc = 72.0 / 600
            ink = pymupdf.Rect(bb.x0 + gx.min() * sc, bb.y0 + gy.min() * sc,
                               bb.x0 + (gx.max() + 1) * sc, bb.y0 + (gy.max() + 1) * sc)
            print('[分析]行 bbox y[%.2f,%.2f] 真墨 y[%.2f,%.2f] x[%.2f,%.2f]' %
                  (bb.y0, bb.y1, ink.y0, ink.y1, ink.x0, ink.x1))
            print('  bbox∩外扩盒?', bb.intersects(infl), ' 真墨∩外扩盒?', ink.intersects(infl),
                  ' 墨顶-外扩底=%.2fpt' % (ink.y0 - infl.y1))
