# -*- coding: utf-8 -*-
"""选项修0910：扫描页行带＋墨段（run）投影测量。
用法：python runs.py <png> <x0mm> <x1mm> <y0mm> <y1mm> [mingapmm=3]
输出：窗口内每个墨行的 y 范围＋墨段起止（mm，页面坐标），段隙<mingapmm 的相邻段并合。"""
import sys
import numpy as np
from PIL import Image

SRC = sys.argv[1]
X0, X1, Y0, Y1 = [float(v) for v in sys.argv[2:6]]
MINGAP = float(sys.argv[6]) if len(sys.argv) > 6 else 3.0
PXMM = 14.062
img = np.asarray(Image.open(SRC).convert("L"))
xa, xb = int(X0 * PXMM), int(X1 * PXMM)
ya, yb = int(Y0 * PXMM), int(Y1 * PXMM)
sub = img[ya:yb, xa:xb] < 200
rows = np.flatnonzero(sub.any(axis=1))
if rows.size == 0:
    print("(no ink)")
    sys.exit()
cuts = np.flatnonzero(np.diff(rows) > 2)
bounds = list(zip(
    np.r_[rows[0], rows[cuts + 1]],
    np.r_[rows[cuts], rows[-1]]))
for b0, b1 in bounds:
    band = sub[b0:b1 + 1]
    cols = np.flatnonzero(band.any(axis=0))
    ccuts = np.flatnonzero(np.diff(cols) > MINGAP * PXMM)
    cruns = list(zip(
        np.r_[cols[0], cols[ccuts + 1]],
        np.r_[cols[ccuts], cols[-1]]))
    segs = ["%.2f–%.2f" % (X0 + s0 / PXMM, X0 + (e0 + 1) / PXMM) for s0, e0 in cruns]
    print("y %6.2f–%6.2f | %s" % (Y0 + b0 / PXMM, Y0 + (b1 + 1) / PXMM, "  ".join(segs)))
