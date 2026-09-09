# -*- coding: utf-8 -*-
"""片C #29 抽点：600dpi ink 两侧墨隙实测。用法：_spot_ink.py <pdf> <标签> <page> <y> <x0> <x1> <name>"""
import sys
import numpy as np
import pymupdf
from PIL import Image

PTMM = 72 / 25.4
DPI = 600


def ink_gap(doc, pno, y, x0, x1, name):
    page = doc[pno - 1]
    clip = pymupdf.Rect(x0 - 60, y - 7, x1 + 60, y + 17)
    pix = page.get_pixmap(dpi=DPI, clip=clip)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')
    a = np.array(im) < 128
    cols = a.any(axis=0)
    # 中心字符墨列范围（x0..x1 映射到像素）
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
    # 墨盒
    rows = np.where(a[:, c0:c1 + 1].any(axis=1))[0]
    print(f'{name}: 墨盒 {(c1 - c0 + 1) / DPI * 25.4:.2f}×{(rows.max() - rows.min() + 1) / DPI * 25.4:.2f}mm  '
          f'左墨隙 {gl and round(gl, 2)}mm  右墨隙 {gr and round(gr, 2)}mm')
    return (gl, gr)


if __name__ == '__main__':
    pdf, label = sys.argv[1], sys.argv[2]
    doc = pymupdf.open(pdf)
    print(f'== {label} ==')
    args = sys.argv[3:]
    for i in range(0, len(args), 5):
        pno, y, x0, x1, name = int(args[i]), float(args[i + 1]), float(args[i + 2]), float(args[i + 3]), args[i + 4]
        ink_gap(doc, pno, y, x0, x1, name)
