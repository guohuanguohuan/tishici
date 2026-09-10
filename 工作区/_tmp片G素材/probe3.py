# -*- coding: utf-8 -*-
"""Subtract known lines; cluster the remainder (glyphs + any unknown lines)."""
import numpy as np
from PIL import Image
import cv2

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image3.png"
a = np.array(Image.open(SRC).convert("L"))
H, W = a.shape
dark = a < 128

# --- known line inventory (px, y down) ---
SOLID = [((56,152),(56,454)), ((356,152),(356,454)), ((462,47),(462,349)),
         ((56,453),(356,453)), ((56,153),(356,153)), ((162,47),(462,47)),
         ((56,152),(163,46)), ((356,152),(462,46)), ((462,47),(356,454)),
         ((462,349),(356,454))]
DASH = [((162,46),(162,349)), ((162,347),(462,347)), ((163,46),(56,454)),
        ((163,46),(462,349)), ((56,453),(462,349)), ((56,453),(162,349)),
        ((56,453),(462,46))]
LINES = SOLID + DASH

mask = np.zeros((H, W), bool)
for (p, q) in LINES:
    x1, y1 = p; x2, y2 = q
    L = int(np.hypot(x2-x1, y2-y1)) + 1
    for t in np.linspace(0, 1, L*2):
        x = x1 + (x2-x1)*t; y = y1 + (y2-y1)*t
        xi, yi = int(round(x)), int(round(y))
        x0, x3 = max(0, xi-2), min(W, xi+3)
        y0, y3 = max(0, yi-2), min(H, yi+3)
        mask[y0:y3, x0:x3] = True

rem = dark & ~mask
print("dark px:", dark.sum(), " remaining:", rem.sum())

n, lab, stats, cent = cv2.connectedComponentsWithStats(rem.astype(np.uint8), 8)
print("components:", n-1)
comps = []
for i in range(1, n):
    x, y, w, h, area = stats[i]
    comps.append((area, x, y, w, h, cent[i]))
comps.sort(reverse=True)
print("\n== components (area, bbox, centroid) ==")
for area, x, y, w, h, c in comps:
    if area >= 6:
        print(f"area={area:5d} bbox=({x:3d},{y:3d},{w:3d}x{h:3d}) cent=({c[0]:6.1f},{c[1]:6.1f})")

# --- probe columns for unknown dashes in mid-figure ---
def runs_along(fixed, lo, hi, axis):
    out = []; cur = None
    for i in range(lo, hi):
        v = dark[fixed, i] if axis == 'row' else dark[i, fixed]
        if v and cur is None: cur = i
        elif not v and cur is not None: out.append((cur, i-1)); cur = None
    if cur is not None: out.append((cur, hi-1))
    return out

print("\n== columns probe (y 40..460) ==")
for x in (220, 265, 300, 330, 375, 410, 440):
    print(f"x={x}: {runs_along(x, 40, 460, 'col')}")
print("\n== rows probe (x 45..470) ==")
for y in (100, 180, 260):
    print(f"y={y}: {runs_along(y, 45, 470, 'row')}")
print("\n== dash stroke width samples ==")
for (x, y) in ((207, 340), (207, 345)):  # across DC dashes
    print(f"col x={x} y340-352: {runs_along(x, 338, 356, 'col')}")
print("col2:", runs_along(210, 336, 356, 'col'))
