# -*- coding: utf-8 -*-
"""取证B组·全品墨隙实测：p04/p05 目标 = 与 ∥ 两侧墨隙。
口径：裁片→灰度→阈160二值→行投影找目标行带→列段分析→符号段左右白隙 px→mm（横 14.176 px/mm）。"""
import os, json
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = r"C:\提示词\工作区\全品结构提取\数学选必一\导学案页图"
PXMM = 2977 / 210.0   # 14.176 px/mm 横口径
THR = 160

# (页, 标签, 裁片x0,y0,x1,y1, 符号类型, 符号在带内的大致x序号提示)
TARGETS = [
    ("p04", "表格·记作 a=b",      930, 3140, 1320, 3330, "=", "表内"),
    ("p04", "表格·记作 a∥b",      930, 3550, 1320, 3740, "∥", "表内"),
    ("p04", "正文·判断(3) a∥b",  1420, 1690, 2340, 1890, "∥", "若 后"),
    ("p04", "正文·判断(3) b∥c",  1420, 1690, 2340, 1890, "∥", "且 后"),
    ("p04", "正文·判断(3) a∥c",  1420, 1690, 2340, 1890, "∥", "则 后"),
    ("p05", "正文·条目2 b∥a",    1480, 300, 1800, 540, "∥", "末尾"),
    ("p05", "正文·判断(2) b∥a",  1480, 1440, 2200, 1650, "∥", "中"),
    ("p05", "正文·判断(2) b=λa",  1480, 1440, 2200, 1650, "=", "行末"),
    ("p05", "正文·例1A |a|=|b|", 1480, 2220, 2390, 2430, "=", "中"),
    ("p05", "正文·判断(3) 和式=",  210, 1820, 1290, 2030, "=", "中"),
]

def band_rows(img):
    a = np.asarray(img.convert("L"))
    ink = a < THR
    return a, ink

results = []
for pg, label, x0, y0, x1, y1, sym, hint in TARGETS:
    im = Image.open(os.path.join(D, pg + ".png")).crop((x0, y0, x1, y1))
    a, ink = band_rows(im)
    H, W = ink.shape
    rowink = ink.sum(axis=1)
    # 找含墨行带（连续 rowink>0 的最大带）
    bands = []
    s = None
    for r in range(H):
        if rowink[r] > 0 and s is None: s = r
        if rowink[r] == 0 and s is not None:
            bands.append((s, r - 1)); s = None
    if s is not None: bands.append((s, H - 1))
    # 多行时取墨量最大的带（目标行）；如需全部行后续手工改
    bands.sort(key=lambda b: -(rowink[b[0]:b[1]+1].sum()))
    rb0, rb1 = bands[0]
    sub = ink[rb0:rb1 + 1, :]
    colink = sub.sum(axis=0) > 0
    segs = []
    c = 0
    while c < W:
        if colink[c]:
            t = c
            while c < W and colink[c]: c += 1
            segs.append((t, c - 1))
        else: c += 1
    print(f"\n[{pg} {label} {sym}·{hint}] 行带 y={rb0+y0}..{rb1+y0} 高{rb1-rb0+1}px 段数{len(segs)}")
    for i, (s, e) in enumerate(segs):
        print(f"  seg{i:02d} x={s+x0:5d}..{e+x0:5d} w={e-s+1:4d}px={(e-s+1)/PXMM:.2f}mm")
