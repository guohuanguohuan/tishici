# -*- coding: utf-8 -*-
"""片E 几何反解：5 图 ink/盒/胶/N 估算（同 postproc side_row 公式）。"""
import math
from PIL import Image as I

BASE = r'C:\提示词\工作区\字替对照-0909\variantF'

def ink(name):
    im = I.open(BASE + '\\media\\media\\' + name).convert('RGBA')
    w, h = im.size
    bg = I.new('RGB', (w, h), (255, 255, 255)); bg.paste(im, (0, 0), im)
    bb = bg.convert('L').point(lambda v: 255 if v < 245 else 0).getbbox()
    return w, h, bb

SIDE_BOX_W_MM = 33.12
COLW = 82.8
SIDE_DEF = {
    'image1.png': dict(ink_w=27.200, r_edge=1.70, text_w=49.000, c0=3.04),
    'image2.png': dict(ink_w=None, r_edge=2.0, text_w=46.368),
    'image3.png': dict(ink_w=None, r_edge=1.70, text_w=46.368),
    'image4.png': dict(ink_w=None, r_edge=2.6, text_w=44.000),
    'image5.png': dict(ink_w=30.000, r_edge=2.6, text_w=46.368),
}
BS = 18.25 * 25.4 / 72
print('BS=%.4fmm' % BS)
for name, cfg in SIDE_DEF.items():
    w, h, (l, t, r, b) = ink(name)
    ink_px_w = r - l
    ink_w = cfg['ink_w'] or SIDE_BOX_W_MM * ink_px_w / w
    sc = ink_w / ink_px_w
    pw = w * sc; pad_l = l * sc; pad_r = (w - r) * sc; pad_t = t * sc; pad_b = (h - b) * sc
    text_w = cfg['text_w']; glue = COLW - cfg['r_edge'] + pad_r - text_w - pw
    H = cfg.get('c0', 2.96) + pad_t + 0.25
    ink_h = (b - t) * sc
    N = math.floor((ink_h - 0.25) / BS) + 1
    print('%-11s px %dx%d ink_px_w=%d ink_w=%.3f sc=%.5f pw=%.3f pad_l=%.3f pad_r=%.3f pad_t=%.3f pad_b=%.3f ink_h=%.3f H=%.3f glue=%.3f img_x=T+G=%.3f 盒高=%.3f 盒底rel_L1=%+.3f N=%d' % (
        name, w, h, ink_px_w, ink_w, sc, pw, pad_l, pad_r, pad_t, pad_b, ink_h, H, glue, text_w + glue, h * sc, -H + h * sc, N))
    print('    justified seam=G+pad_l=%.3f   ink底rel_L1=%+.3f(=盒底−pad_b)  墨右缘距栏右=%.3f' % (
        glue + pad_l, -H + b * sc, COLW - (text_w + glue + l * sc)))
