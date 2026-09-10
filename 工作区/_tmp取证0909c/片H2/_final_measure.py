# -*- coding: utf-8 -*-
"""片H2：终版 E3 靶值复测（cap/脚本比/分式总高/减号形态）＋维持项抽点。
在同尺 360dpi 下量我方 main.pdf。"""
import numpy as np
import pymupdf
from PIL import Image
import io
from scipy import ndimage

PDF = r'C:/提示词/工作区/字替对照-0909/variantF/main.pdf'
PXMM = 14.1732  # 360dpi


def render(pno, dpi=360):
    doc = pymupdf.open(PDF)
    pix = doc[pno].get_pixmap(dpi=dpi)
    return np.asarray(Image.open(io.BytesIO(pix.tobytes('png'))).convert('L')).astype(np.uint8)


def comps(ik, x0, x1, y0, y1, thr=170, min_h=2, min_w=2):
    sub = ik[y0:y1, x0:x1] < thr
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    out = []
    for ys, xs in ndimage.find_objects(lab):
        h = ys.stop - ys.start
        w = xs.stop - xs.start
        if h < min_h or w < min_w:
            continue
        out.append((xs.start + x0, xs.stop + x0, ys.start + y0, ys.stop + y0, w, h))
    out.sort()
    return out


def report(tag, cs):
    print(f'== {tag}')
    for c in cs:
        print(f'   x{c[0]:>5}-{c[1]:<5} y{c[2]:>5}-{c[3]:<5} w{c[4]:>4} h{c[5]:>4}')


if __name__ == '__main__':
    # 1) p4（index 3）变式行：ABCD-A₁B₁C₁D₁ 串 + ½ 分式（先粗看）
    ik = render(3)
    cs = comps(ik, 250, 1100, 490, 560)
    report('p4 变式1 行（ABCD-A₁B₁C₁D₁ 串）', cs)
