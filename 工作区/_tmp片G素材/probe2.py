# -*- coding: utf-8 -*-
"""Precise runs analysis: scan specific rows/columns for dark runs."""
import numpy as np
from PIL import Image

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image3.png"
a = np.array(Image.open(SRC).convert("L"))
H, W = a.shape
dark = a < 128

def runs_along(fixed, lo, hi, axis):
    """axis='row' -> scan row `fixed` from x=lo..hi; axis='col' -> column."""
    out = []
    cur = None
    for i in range(lo, hi):
        v = dark[fixed, i] if axis == 'row' else dark[i, fixed]
        if v and cur is None:
            cur = i
        elif not v and cur is not None:
            out.append((cur, i - 1)); cur = None
    if cur is not None:
        out.append((cur, hi - 1))
    return out

print("== columns (vertical lines) ==")
for x in (56, 162, 356, 462):
    r = runs_along(x, 0, H, 'col')
    print(f"x={x}: {r}")

print("\n== rows (horizontal lines) ==")
for y in (47, 151, 453, 349, 347):
    r = runs_along(y, 0, W, 'row')
    print(f"y={y}: {r}")

print("\n== stroke width: perpendicular profiles ==")
# vertical line x=56 at y=300: width
for (x, y) in ((56, 300), (162, 300), (356, 300), (462, 300)):
    r = runs_along(y, x - 6, x + 7, 'row')
    print(f"vertical near x={x} @y={y}: x-runs {r}")
for (y, x) in ((453, 200), (151, 200), (47, 300), (347, 300), (349, 300)):
    r = runs_along(x, y - 6, y + 7, 'col')
    print(f"horizontal near y={y} @x={x}: y-runs {r}")

print("\n== 45-deg solid (A1D1): sample a few diagonal profiles ==")
# line A1(56,152)-D1(163,46): point at t=0.5 ~ (110,99)
for (cx, cy) in ((80, 129), (110, 99), (140, 69)):
    r = runs_along(cy, cx - 8, cx + 9, 'row')
    print(f"row y={cy} around x={cx}: {r}")

print("\n== thick solid B->C1 and C->B profiles ==")
# B(356,453)-C1(462,46): at y=300: x ~ 356+ (462-356)*(453-300)/(453-46)=356+106*153/407=395.8
for y in (300, 200, 120):
    r = runs_along(y, 380, 430, 'row')
    print(f"row y={y} x380-430: {r}")
# C(462,349)-B(356,453) at t=0.5: (409,401)
for y in (400, 420):
    r = runs_along(y, 370, 450, 'row')
    print(f"row y={y} x370-450: {r}")

print("\n== check ends of dashed lines near vertices (arrowhead?) ==")
# near A(56,453): profile perpendicular to A->D1 dir (-0.269,0.963) -> normal (0.963,0.269)
# just sample rows above A between x=40..75
for y in (425, 435, 445):
    r = runs_along(y, 30, 90, 'row')
    print(f"row y={y} x30-90: {r}")
# near D1(163,46): rows just below
for y in (55, 65, 75, 85):
    r = runs_along(y, 120, 210, 'row')
    print(f"row y={y} x120-210: {r}")
