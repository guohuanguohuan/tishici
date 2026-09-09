# -*- coding: utf-8 -*-
"""取证B组·全品补裁：修正 t04(条目2 b∥a)、t06(例1A |a|=|b|)、t08(判断2 b=λa)、t07核对。"""
import os
from PIL import Image, ImageDraw
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = r"C:\提示词\工作区\全品结构提取\数学选必一\导学案页图"
PXMM = 2977 / 210.0
THR = 160

TARGETS = [
    ("p05", "t04b_条目2b∥a", 1500, 360, 1720, 450, None),
    ("p05", "t06b_例1A",    1480, 2255, 2500, 2360, None),
    ("p05", "t08_判断2b=λa", 1480, 1550, 2500, 1640, None),
    ("p05", "t07b_判断3和式", 210, 1880, 1290, 2010, None),
]

for pg, name, x0, y0, x1, y1, _ in TARGETS:
    im0 = Image.open(os.path.join(D, pg + ".png")).crop((x0, y0, x1, y1))
    a = np.asarray(im0.convert("L")); ink = a < THR
    H, W = ink.shape
    rowink = ink.sum(axis=1)
    bands = []; s = None
    for r in range(H):
        if rowink[r] > 2 and s is None: s = r
        if rowink[r] <= 2 and s is not None: bands.append((s, r - 1)); s = None
    if s is not None: bands.append((s, H - 1))
    print(f"\n{name}: 行带 {[(b[0]+y0, b[1]+y0) for b in bands]}")
    # 取墨量最大带
    if bands:
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
        strip = im0.crop((0, max(0, rb0 - 5), W, min(H, rb1 + 6))).convert("RGB")
        Z = 3
        strip = strip.resize((strip.width * Z, strip.height * Z), Image.LANCZOS)
        dr = ImageDraw.Draw(strip)
        for i, (t, e) in enumerate(segs):
            dr.line([t * Z, 0, t * Z, strip.height], fill=(255, 0, 0), width=1)
            dr.line([(e + 1) * Z, 0, (e + 1) * Z, strip.height], fill=(0, 160, 0), width=1)
            dr.text((t * Z + 2, 2), str(i), fill=(0, 0, 255))
        strip.save(os.path.join(HERE, f"seg_{name}.png"))
        print("  ", " | ".join(f"{i}:{t+x0}..{e+x0}({(e-t+1)/PXMM:.2f}mm)" for i, (t, e) in enumerate(segs)))
