# -*- coding: utf-8 -*-
"""片C #29 抽点 v2：600dpi ink 两侧墨隙（窄 y 带＝目标字形墨带）。
用法：_spot_ink2.py <pdf> <标签> <page> <y0> <y1> <x0> <x1> <name>"""
import sys
import numpy as np
import pymupdf
from PIL import Image

DPI = 600


def ink_gap(doc, pno, y0, y1, x0, x1, name):
    page = doc[pno - 1]
    clip = pymupdf.Rect(x0 - 40, y0 - 1, x1 + 40, y1 + 1)
    pix = page.get_pixmap(dpi=DPI, clip=clip)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')
    a = np.array(im) < 128
    cols = a.any(axis=0)
    px0 = int((x0 - clip.x0) / 72 * DPI)
    px1 = int((x1 - clip.x0) / 72 * DPI)
    core = np.where(cols[px0:px1])[0]
    if len(core) == 0:
        print(f'{name}: 中心区无墨')
        return
    c0 = px0 + core.min()
    c1 = px0 + core.max()
    left = np.where(cols[:c0])[0]
    right = np.where(cols[c1 + 1:])[0]
    gl = (c0 - left.max()) / DPI * 25.4 if len(left) else None
    gr = (right.min() + 1) / DPI * 25.4 if len(right) else None
    print(f'{name}: 左墨隙 {gl and round(gl, 2)}mm  右墨隙 {gr and round(gr, 2)}mm')


if __name__ == '__main__':
    pdf, label = sys.argv[1], sys.argv[2]
    doc = pymupdf.open(pdf)
    print(f'== {label} ==')
    args = sys.argv[3:]
    for i in range(0, len(args), 6):
        pno, y0, y1, x0, x1 = int(args[i]), float(args[i+1]), float(args[i+2]), float(args[i+3]), float(args[i+4])
        ink_gap(doc, pno, y0, y1, x0, x1, args[i+5])
