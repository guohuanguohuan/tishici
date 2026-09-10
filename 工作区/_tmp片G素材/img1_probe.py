# -*- coding: utf-8 -*-
"""Pixel analysis of variantF image1.png — ink lives in the ALPHA channel."""
import numpy as np
from PIL import Image
import cv2

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image1.png"
im = Image.open(SRC)
al = np.array(im)[..., 3]
ink = (al > 128).astype(np.uint8)
H, W = ink.shape
print("size:", W, "x", H, "ink px:", int(ink.sum()))
ys, xs = np.where(ink > 0)
print("content bbox: x %d-%d  y %d-%d" % (xs.min(), xs.max(), ys.min(), ys.max()))

# stroke width sample: horizontal runs at several rows
for r in (60, 300, 600, 900, 1140):
    row = ink[r, :]
    runs = []
    x = 0
    while x < W:
        if row[x]:
            x0 = x
            while x < W and row[x]:
                x += 1
            runs.append((x0, x - x0))
        else:
            x += 1
    print("row %4d runs:" % r, runs[:14])

# dots: erode 7x7
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
er = cv2.erode(ink * 255, kernel)
n, lab, stats, cent = cv2.connectedComponentsWithStats(er, 8)
print("dot candidates after 7x7 erode:", n - 1)
dots = []
for i in range(1, n):
    cx, cy = cent[i]
    area = stats[i, cv2.CC_STAT_AREA]
    w_ = stats[i, cv2.CC_STAT_WIDTH]; h_ = stats[i, cv2.CC_STAT_HEIGHT]
    print("  cand cx=%.1f cy=%.1f area=%d w=%d h=%d" % (cx, cy, area, w_, h_))
    if area >= 4:
        dots.append((cx, cy, area, w_, h_))
np.save("img1_ink.npy", ink)
print("DOTS:")
for d in sorted(dots, key=lambda t: t[1]):
    print("  dot cx=%.1f cy=%.1f area=%d w=%d h=%d" % d)
