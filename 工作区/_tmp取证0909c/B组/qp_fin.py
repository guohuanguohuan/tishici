# -*- coding: utf-8 -*-
"""取证B组·全品补充：①判断(2)行2 b=λa；②t03 ∥b 粘连段 6x 放大＋子带分解；③t06b = 区 6x 放大。"""
import os
from PIL import Image, ImageDraw
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = r"C:\提示词\工作区\全品结构提取\数学选必一\导学案页图"
PXMM = 2977 / 210.0
THR = 160
p05 = Image.open(os.path.join(D, "p05.png"))
p04 = Image.open(os.path.join(D, "p04.png"))

# ① b=λa 行2：y1545..1595
crop = p05.crop((1480, 1545, 2560, 1600))
a = np.asarray(crop.convert("L")); ink = a < THR
rowink = ink.sum(axis=1)
ys = [r for r in range(ink.shape[0]) if rowink[r] > 0]
print("行2 墨行 y:", 1545 + min(ys), "..", 1545 + max(ys))
colink = ink.sum(axis=0) > 0
segs = []; c = 0
W = ink.shape[1]
while c < W:
    if colink[c]:
        t = c
        while c < W and colink[c]: c += 1
        segs.append((t, c - 1))
    else: c += 1
Z = 3
strip = crop.convert("RGB").resize((crop.width * Z, crop.height * Z), Image.LANCZOS)
dr = ImageDraw.Draw(strip)
for i, (t, e) in enumerate(segs):
    dr.line([t * Z, 0, t * Z, strip.height], fill=(255, 0, 0), width=1)
    dr.line([(e + 1) * Z, 0, (e + 1) * Z, strip.height], fill=(0, 160, 0), width=1)
    dr.text((t * Z + 2, 2), str(i), fill=(0, 0, 255))
strip.save(os.path.join(HERE, "seg_t08b_b=λa.png"))
print("段:", " | ".join(f"{i}:{t+1480}..{e+1480}({(e-t+1)/PXMM:.2f}mm)" for i, (t, e) in enumerate(segs)))

# ② t03 ∥b：x1731..1795 y1775..1840 放大6x＋上下半带分解
crop2 = p04.crop((1720, 1770, 1815, 1845))
crop2.resize((crop2.width * 6, crop2.height * 6), Image.LANCZOS).save(os.path.join(HERE, "zoom_t03_∥b.png"))
a2 = np.asarray(crop2.convert("L")); ink2 = a2 < THR
for tag, r0, r1 in [("上半", 0, ink2.shape[0] // 2), ("下半", ink2.shape[0] // 2, ink2.shape[0])]:
    sub = ink2[r0:r1, :]
    colink2 = sub.sum(axis=0) > 0
    segs2 = []; c = 0
    while c < len(colink2):
        if colink2[c]:
            t = c
            while c < len(colink2) and colink2[c]: c += 1
            segs2.append((t + 1720, c - 1 + 1720))
        else: c += 1
    print(f"t03 ∥b {tag}带段:", " | ".join(f"{s}..{e}({(e-s+1)/PXMM:.2f}mm)" for s, e in segs2))

# ③ t06b = 区：x2250..2460 y2270..2340 放大6x
crop3 = p05.crop((2250, 2270, 2460, 2340))
crop3.resize((crop3.width * 6, crop3.height * 6), Image.LANCZOS).save(os.path.join(HERE, "zoom_t06b_=区.png"))
