# -*- coding: utf-8 -*-
# pass2：页眉区（CONTENTS/目录/方块）、章方块、点线灰、页码数字、正文页版心标定
from PIL import Image
import numpy as np

BASE = r"C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/"
PXMM = 2977 / 210.0
pt = lambda px: px * 25.4 / (PXMM * 25.4) * 7227 / 2540 / 10  # dummy
PT = lambda px: px / PXMM * 72 / 25.4 * 25.4 / 25.4  # noqa
def mmpx(v): return v / PXMM

def grayband(a, thr, y0, y1, x0, x1, minink=4, label=""):
    reg = a[y0:y1, x0:x1] < thr
    rc = reg.sum(axis=1)
    out = []
    y = 0
    H = y1 - y0
    while y < H:
        if rc[y] > minink:
            s = y
            while y < H and rc[y] > minink:
                y += 1
            xs = np.where(reg[s:y, :].any(axis=0))[0]
            vals = a[y0+s:y0+y, x0+xs.min():x0+xs.max()+1]
            ink = vals[vals < thr]
            out.append((y0+s, y0+y, x0+int(xs.min()), x0+int(xs.max()),
                        int(ink.mean()) if ink.size else -1))
        else:
            y += 1
    for (b0, b1, xa, xb, g) in out:
        print(f"  {label} y{b0}-{b1} h={b1-b0}px x{xa}-{xb} meanGray={g}  yTop={b0/PXMM:.2f}mm inkH={(b1-b0)/PXMM:.2f}mm")
    return out

im2 = np.array(Image.open(BASE + "p02.png").convert("L"))
print("== p02 页眉区（thr 215, y300-800）==")
grayband(im2, 215, 300, 800, 200, 2800, 3, "hdr")
print("== p02 页眉区（thr 120 深字，y450-700）==")
grayband(im2, 120, 450, 700, 1800, 2300, 3, "目录字")
print("== 章方块区（y860-1000, x400-600, thr200）==")
grayband(im2, 200, 860, 1000, 400, 620, 3, "sq01")
print("== PART ONE 行（y975-1030, thr215）==")
grayband(im2, 215, 975, 1030, 400, 2800, 3, "part")
print("== 首节行 1.1（y1030-1090）分段：标题侧 x460-1500 / 点线 x1500-2500 / 页码 x2560-2700 ==")
grayband(im2, 120, 1030, 1090, 460, 1500, 3, "title")
grayband(im2, 215, 1030, 1090, 1500, 2500, 3, "dots")
grayband(im2, 120, 1030, 1090, 2500, 2750, 3, "pageno")
print("== 小节行 1.1.1（y1150-1200）==")
grayband(im2, 120, 1145, 1205, 460, 1500, 3, "title")
grayband(im2, 120, 1145, 1205, 2500, 2750, 3, "pageno")
print("== 课时行（y1265-1315）==")
grayband(im2, 120, 1260, 1320, 460, 1500, 3, "title")
print("== 本章总结行（y2655-2705）==")
grayband(im2, 120, 2650, 2710, 460, 1500, 3, "zongjie")
print("== 采样灰值 ==")
for (lbl, y, x) in [("CONTENTS左C", 560, 350), ("CONTENTS中", 560, 900), ("CONTENTS右S", 560, 1500),
                    ("点线mid", 1055, 2000), ("PART ONE", 1000, 500), ("章方块", 930, 480),
                    ("页码数字", 1055, 2620)]:
    print(f"  {lbl} ({x},{y}) = {im2[y, x]}")
print("== 正文页 p05 版心标定（thr120 全页行带 x 极值，取前 3 带）==")
im5 = np.array(Image.open(BASE + "p05.png").convert("L"))
bs = grayband(im5, 120, 500, 900, 100, 2900, 10, "body")
