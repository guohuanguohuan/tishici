# -*- coding: utf-8 -*-
# pass3：精测各零件数值。一次性测量脚本。
from PIL import Image
import numpy as np

BASE = r"C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/"
PXMM = 2977 / 210.0
MM = lambda px: px / PXMM

def bbox(a, y0, y1, x0, x1, thr, label="", mode="dark"):
    reg = a[y0:y1, x0:x1]
    m = reg < thr if mode == "dark" else reg > thr
    ys, xs = np.where(m)
    if len(ys) == 0:
        print(f"  {label}: EMPTY"); return None
    b = (y0 + ys.min(), y0 + ys.max(), x0 + xs.min(), x0 + xs.max())
    core = reg[m]
    print(f"  {label}: y{b[0]}-{b[1]} x{b[2]}-{b[3]}  h={b[1]-b[0]+1}px={MM(b[1]-b[0]+1):.2f}mm w={b[3]-b[2]+1}px={MM(b[3]-b[2]+1):.2f}mm  L={b[2]/PXMM:.2f}mm R={b[3]/PXMM:.2f}mm T={b[0]/PXMM:.2f}mm gray mean={core.mean():.0f} min={core.min()} mode={np.bincount(core.flatten()).argmax()}")
    return b

def dotpitch(a, y0, y1, x0, x1, thr):
    reg = a[y0:y1, x0:x1] < thr
    col = reg.any(axis=0)
    runs, s = [], None
    for i, v in enumerate(col):
        if v and s is None: s = i
        if not v and s is not None: runs.append((s, i - 1)); s = None
    if s is not None: runs.append((s, len(col) - 1))
    if len(runs) > 2:
        c = np.array([r[0] for r in runs[1:]]) - np.array([r[0] for r in runs[:-1]])
        w = [b - a_ + 1 for (a_, b) in runs]
        print(f"    dots n={len(runs)} pitch med={np.median(c):.0f}px={MM(np.median(c)):.2f}mm width med={np.median(w):.0f}px")
    else:
        print(f"    dots n={len(runs)}")

im2 = np.array(Image.open(BASE + "p02.png").convert("L"))
print("== p02 ==")
print("-- 章方块01（含白字）--")
b = bbox(im2, 860, 1080, 250, 470, 220, "sq01")
bbox(im2, 860, 1080, 250, 470, 235, "sq01内白字", "light")
print("-- 章名 --")
bbox(im2, 880, 975, 470, 1300, 120, "章名")
print("-- PART ONE --")
bbox(im2, 965, 1020, 440, 800, 215, "PARTONE")
print("-- 章点线 --")
bbox(im2, 965, 1020, 820, 2700, 225, "章rule")
dotpitch(im2, 995, 1012, 900, 2000, 235)
print("-- 首节行 --")
bbox(im2, 1030, 1090, 460, 1500, 120, "1.1标题")
bbox(im2, 1030, 1090, 2600, 2680, 150, "页码139")
dotpitch(im2, 1048, 1064, 1000, 2400, 230)
print("-- 课时行 --")
bbox(im2, 1260, 1320, 660, 1500, 120, "课时标题")
print("-- 本章总结行 --")
bbox(im2, 2650, 2715, 460, 540, 150, "圆图标")
bbox(im2, 2650, 2715, 540, 760, 120, "本章总结字")
bbox(im2, 2650, 2715, 460, 540, 235, "圆内白", "light")
print("-- 页眉：CONTENTS --")
bbox(im2, 360, 680, 300, 1660, 235, "CONTENTS")
for x0 in range(320, 1600, 160):
    seg = im2[380:660, x0:x0+160]
    m = seg < 240
    if m.sum() > 50:
        print(f"    CONTENTS x{x0}-{x0+160}: core gray={seg[m].min()} p10={np.percentile(seg[m],10):.0f}")
print("-- 页眉方块组 --")
bbox(im2, 350, 470, 1650, 1900, 200, "方块深(上右)")
bbox(im2, 460, 580, 1650, 1790, 235, "方块浅(左)")
bbox(im2, 575, 640, 1690, 1780, 235, "小块(下)")
print("-- 目录字 --")
bbox(im2, 480, 660, 1840, 2160, 150, "目录")
print("-- 竖线+导学案 --")
bbox(im2, 480, 660, 2160, 2200, 235, "竖线")
bbox(im2, 480, 660, 2200, 2360, 235, "导学案")

im3 = np.array(Image.open(BASE + "p03.png").convert("L"))
print("== p03 全行带 ==")
rc = (im3 < 120)[:, 300:2800].sum(axis=1)
y = 0; prev = None
while y < im3.shape[0]:
    if rc[y] > 4:
        s = y
        while y < im3.shape[0] and rc[y] > 4: y += 1
        xs = np.where((im3[s:y, :] < 120).any(axis=0))[0]
        pk = f" pitch={s-prev}px={MM(s-prev):.2f}mm" if prev else ""
        prev = s
        print(f"  y{s}-{y} h={y-s}px x{xs.min()}-{xs.max()}{pk}")
    else:
        y += 1
print("-- p03 参考答案行 --")
bbox(im3, 3170, 3260, 400, 1300, 150, "◆+参考答案")
