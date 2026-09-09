# -*- coding: utf-8 -*-
"""取证B组·全品段界标注条带：每目标行带 ×2 放大，红竖线标墨段边界＋段号，供目检定段。"""
import os
from PIL import Image, ImageDraw
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = r"C:\提示词\工作区\全品结构提取\数学选必一\导学案页图"
PXMM = 2977 / 210.0
THR = 160

TARGETS = [
    ("p04", "t01_表a=b",   930, 3140, 1320, 3330, (980, 1230)),
    ("p04", "t02_表a∥b",   930, 3550, 1320, 3740, (980, 1230)),
    ("p04", "t03_判断3∥",  1420, 1690, 2340, 1890, (1620, 2210)),
    ("p05", "t04_条目2∥",  1480, 300, 1800, 540, (1530, 1800)),
    ("p05", "t05_判断2∥λ", 1480, 1440, 2200, 1650, (1540, 2210)),
    ("p05", "t06_例1A=",   1480, 2220, 2390, 2430, (1540, 2395)),
    ("p05", "t07_判断3和式", 210, 1820, 1290, 2030, (250, 1140)),
]

for pg, name, x0, y0, x1, y1, (wx0, wx1) in TARGETS:
    im = Image.open(os.path.join(D, pg + ".png")).crop((x0, y0, x1, y1))
    a = np.asarray(im.convert("L")); ink = a < THR
    H, W = ink.shape
    rowink = ink.sum(axis=1)
    bands = []; s = None
    for r in range(H):
        if rowink[r] > 0 and s is None: s = r
        if rowink[r] == 0 and s is not None: bands.append((s, r - 1)); s = None
    if s is not None: bands.append((s, H - 1))
    bands.sort(key=lambda b: -(rowink[b[0]:b[1]+1].sum()))
    rb0, rb1 = bands[0]
    sub = ink[rb0:rb1 + 1, :]
    colink = sub.sum(axis=0) > 0
    segs = []; c = 0
    while c < W:
        if colink[c]:
            t = c
            while c < W and colink[c]: c += 1
            segs.append((t, c - 1))
        else: c += 1
    # 输出条带：x 从 wx0..wx1（页坐标），行带全高
    strip = im.crop((wx0 - x0, max(0, rb0 - 6), wx1 - x0, min(H, rb1 + 7))).convert("RGB")
    Z = 3
    strip = strip.resize((strip.width * Z, strip.height * Z), Image.LANCZOS)
    dr = ImageDraw.Draw(strip)
    for i, (s, e) in enumerate(segs):
        if e < wx0 - x0 or s > wx1 - x0: continue
        X0 = (s - (wx0 - x0)) * Z; X1 = (e + 1 - (wx0 - x0)) * Z
        dr.line([X0, 0, X0, strip.height], fill=(255, 0, 0), width=1)
        dr.line([X1, 0, X1, strip.height], fill=(0, 160, 0), width=1)
        dr.text((X0 + 2, 2), str(i), fill=(0, 0, 255))
    strip.save(os.path.join(HERE, f"seg_{name}.png"))
    segs_in = [(i, s + x0, e + x0, (e - s + 1) / PXMM) for i, (s, e) in enumerate(segs) if s + x0 >= wx0 - 5 and e + x0 <= wx1 + 5]
    print(name, "行带y=", rb0 + y0, "..", rb1 + y0)
    print("  ", " | ".join(f"{i}:{s}..{e}({w:.2f}mm)" for i, s, e, w in segs_in))
