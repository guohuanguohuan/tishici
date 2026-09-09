# -*- coding: utf-8 -*-
"""全品 p04/p05 参照区裁片＋行带检测（A4 扫描口径 14.176/14.057 px/mm，承项目 测量脚本.py）。"""
import numpy as np, sys
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding="utf-8")

PXMM_Y = 4176 / 297.0   # 14.057
PXMM_X = 2977 / 210.0   # 14.176
QP = r"C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/"

def bands_of(arr, thr=170, min_gap=6, min_h=6):
    has = (arr < thr).any(axis=1)
    idx = np.flatnonzero(has)
    out, s, p = [], None, None
    for i in idx:
        i = int(i)
        if s is None:
            s = p = i; continue
        if i - p > min_gap:
            if p - s + 1 >= min_h: out.append((s, p))
            s = i
        p = i
    if s is not None and p - s + 1 >= min_h:
        out.append((s, p))
    return out

jobs = [
    ("p04.png", (1420, 1380, 2700, 2210), "qp_p04_R_zt.png", "quanpin p04 R: zhenduan(1)-(5)"),
    ("p05.png", (150, 1540, 1430, 2060), "qp_p05_L_zt.png", "quanpin p05 L: zhenduan(1)-(3)"),
    ("p05.png", (150, 3060, 1430, 3760), "qp_p05_L_shu.png", "quanpin p05 L: zhishidian5 shucheng(1)(1)(2)(3)"),
]
for page, (x0, y0, x1, y1), fname, title in jobs:
    im = Image.open(QP + page).convert("L")
    crop = im.crop((x0, y0, x1, y1))
    arr = np.asarray(crop)
    bs = bands_of(arr)
    print(f"==== {title}  region x[{x0},{x1}] y[{y0},{y1}]  {len(bs)} bands")
    prev = None
    for k, (s, e) in enumerate(bs):
        top, bot = y0 + s, y0 + e
        d = "" if prev is None else f"  pitch={top-prev:4d}px={ (top-prev)/PXMM_Y:5.2f}mm"
        print(f"  band{k:02d} y[{top},{bot}] h={e-s+1:3d}px={ (e-s+1)/PXMM_Y:5.2f}mm{d}")
        prev = top
    rgb = crop.convert("RGB")
    dr = ImageDraw.Draw(rgb)
    for k, (s, e) in enumerate(bs):
        dr.line([(0, s), (40, s)], fill=(255, 0, 0), width=2)
        dr.text((44, s - 4), str(k), fill=(255, 0, 0))
    rgb.save(fname)
    print("  saved", fname)
