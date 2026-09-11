# -*- coding: utf-8 -*-
# 量取全品导学案目录页（p02/p03）版式参数：行带/缩进/行距/灰度。一次性测量脚本，不属交付物。
from PIL import Image
import numpy as np

BASE = r"C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/"
PXMM = 2977 / 210.0  # 14.176 px/mm；360dpi 下 1px=0.2pt

def bands_of(a, thr, x0, x1, minink=4):
    dark = a < thr
    rc = dark[:, x0:x1].sum(axis=1)
    H = a.shape[0]
    out = []
    y = 0
    while y < H:
        if rc[y] > minink:
            y0 = y
            while y < H and rc[y] > minink:
                y += 1
            out.append((y0, y))
        else:
            y += 1
    return out

def xext(a, thr, y0, y1):
    seg = a[y0:y1, :] < thr
    xs = np.where(seg.any(axis=0))[0]
    return (int(xs.min()), int(xs.max())) if len(xs) else None

def gray_at(a, y, x):
    return int(a[y, x])

def report(name, y0, y1, full=False):
    im = Image.open(BASE + name).convert("L")
    a = np.array(im)
    W = a.shape[1]
    print(f"==== {name} {a.shape[1]}x{a.shape[0]} px/mm={W/210.0:.3f} 1px={25.4*72/ (W/210.0*25.4):.3f}pt")
    bs = bands_of(a, 120, int(W*0.05), int(W*0.98))
    prev = None
    for (b0, b1) in bs:
        xe = xext(a, 120, b0, b1)
        pitch = f" pitch={b0-prev}px({(b0-prev)/PXMM:.2f}mm)" if prev is not None else ""
        prev = b0
        print(f"y {b0:>4}-{b1:>4} h={b1-b0:>3}px={(b1-b0)*0.2:.1f}pt inkH={(b1-b0)/PXMM:.2f}mm yTop={b0/PXMM:.2f}mm x{xe}{pitch}")

report("p02.png", 0, 4175)
