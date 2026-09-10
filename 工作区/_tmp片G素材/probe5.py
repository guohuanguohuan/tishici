# -*- coding: utf-8 -*-
"""Correct-normal stroke widths + grayscale profiles."""
import numpy as np
from PIL import Image

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image3.png"
a = np.array(Image.open(SRC).convert("L")).astype(float)

def width_at(x, y, nx, ny):
    tot = 0.0
    for o in np.arange(-6, 6.001, 0.125):
        xx = x + nx * o; yy = y + ny * o
        xi, yi = int(np.floor(xx)), int(np.floor(yy))
        fx, fy = xx - xi, yy - yi
        v = (a[yi, xi]*(1-fx)*(1-fy) + a[yi, xi+1]*fx*(1-fy) +
             a[yi+1, xi]*(1-fx)*fy + a[yi+1, xi+1]*fx*fy)
        tot += (255 - v) / 255
    return tot * 0.125

def report(name, pts, nx, ny):
    vals = [round(width_at(x, y, nx, ny), 2) for x, y in pts]
    print(f"{name:14s} {vals}  mean={np.mean(vals):.2f}")

# axis parallel
report("A1A vert", [(56,200),(56,250),(56,300),(56,350),(56,400)], 1, 0)
report("B1B vert", [(356,200),(356,250),(356,300),(356,400)], 1, 0)
report("C1C vert", [(462,100),(462,150),(462,200),(462,300)], 1, 0)
report("AB horiz", [(120,453),(200,453),(280,453)], 0, 1)
report("A1B1 horiz", [(120,153),(200,153),(280,153)], 0, 1)
report("D1C1 horiz", [(200,47),(300,47),(400,47)], 0, 1)
# diagonals, correct normals
report("A1D1 solid", [(81,127),(108,100),(133,75),(156,52)], 0.710,0.704)
report("B1C1 solid", [(378,133),(410,98),(440,68)], -0.7071,-0.7071)
report("B-C1 solid", [(375,381),(410,247),(440,132)], 0.968,0.252)
report("C-B solid", [(390,420),(410,400),(440,370)], 0.710,0.704)
# dashed interiors
report("D1D dash", [(162,50),(162,72),(162,91),(162,111),(162,150),(162,300)], 1, 0)
report("DC dash", [(186,347),(226,347),(305,347),(430,347)], 0, 1)
report("D1A dash", [(158,60),(139,130),(121,200),(102,270),(84,340)], -0.9668,-0.2536)
report("D1C dash", [(174,58),(238,123),(303,188),(368,253),(432,318)], 0.703,0.711)
report("AC dash", [(130,434),(181,421),(233,408),(284,395),(384,369)], -0.248,0.969)
report("AD dash", [(64,445),(92,417),(120,389),(148,361)], 0.704,0.710)

print("\n-- grayscale profile across left edge x=54..60 @y=300 --")
print([int(v) for v in a[300, 53:61]])
print("-- across D1D dash @y=52, x=158..166 --")
print([int(v) for v in a[52, 157:167]])
print("-- across DC dash @x=207, y=343..352 --")
print([int(v) for v in a[343:352, 207]])
print("-- across D1A dash: row y=200, x=118..126 --")
print([int(v) for v in a[200, 117:127]])
print("-- across A1D1 solid: row y=100, x=105..116 --")
print([int(v) for v in a[100, 104:117]])
print("-- across C-B solid: row y=400, x=404..415 --")
print([int(v) for v in a[400, 403:416]])
print("-- across B-C1 solid: row y=300, x=392..400 --")
print([int(v) for v in a[300, 391:401]])
