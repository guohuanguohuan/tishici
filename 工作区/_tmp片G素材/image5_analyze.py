# -*- coding: utf-8 -*-
"""image5.png (矩形沿AC折起图) pixel analysis -> TikZ redraw parameters.
NOTE: source PNG is RGBA with RGB=0 everywhere; ink is carried in ALPHA."""
import numpy as np
from PIL import Image

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image5.png"
OUT = r"C:\提示词\工作区\_tmp片G素材"

im = Image.open(SRC)
alpha = np.array(im)[:, :, 3]
H, W = alpha.shape
ink = alpha > 128
print("size:", W, "x", H)
ys, xs = np.where(ink)
print("ink bbox: x", xs.min(), "-", xs.max(), " y", ys.min(), "-", ys.max())
print("ink px:", ink.sum())

from scipy import ndimage
lab, n = ndimage.label(ink, structure=np.ones((3, 3)))
print("components(8-conn):", n)
objs = ndimage.find_objects(lab)
info = []
for i, sl in enumerate(objs):
    h = sl[0].stop - sl[0].start
    w = sl[1].stop - sl[1].start
    cnt = int((lab[sl] == i + 1).sum())
    info.append((cnt, sl[1].start, sl[1].stop, sl[0].start, sl[0].stop, w, h))
info.sort(reverse=True)
for cnt, x0, x1, y0, y1, w, h in info:
    print(f"  px={cnt:6d} x[{x0},{x1}) y[{y0},{y1}) w={w} h={h}")
