# -*- coding: utf-8 -*-
"""Definitive per-segment coverage sampler + width/dash/glyph metrics."""
import numpy as np
from PIL import Image

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image3.png"
a = np.array(Image.open(SRC).convert("L")).astype(float)
dark = a < 128

V = {
 'A': (56, 453), 'B': (356.5, 453.5), 'C': (462, 349), 'D': (161.5, 348.5),
 'A1': (56, 152.5), 'B1': (356, 152.5), 'C1': (462.5, 46.5), 'D1': (162.5, 47),
}

def sample(p, q, trim=7.0):
    p = np.array(p, float); q = np.array(q, float)
    d = q - p; L = float(np.hypot(*d)); u = d / L
    n = np.array([-u[1], u[0]])
    ts = np.arange(trim, L - trim, 0.5)
    hits = []
    for t in ts:
        pt = p + u * t
        best = False
        for o in np.arange(-1.0, 1.01, 0.5):
            x, y = pt + n * o
            xi, yi = int(round(x)), int(round(y))
            # bilinear-ish check: dark if within 1px
            if 0 <= yi < a.shape[0] and 0 <= xi < a.shape[1] and dark[yi, xi]:
                best = True; break
        hits.append(best)
    hits = np.array(hits)
    ratio = hits.mean() if len(hits) else 0
    # runs
    runs = []
    if len(hits):
        cur, ln = hits[0], 0
        for h in hits:
            if h == cur: ln += 1
            else: runs.append((cur, ln)); cur = h; ln = 1
        runs.append((cur, ln))
    return L, ratio, runs

names = list(V)
print("=== all vertex-pair segments (trim 7px) ===")
for i in range(len(names)):
    for j in range(i+1, len(names)):
        p, q = V[names[i]], V[names[j]]
        L, r, runs = sample(p, q)
        rr = ''.join(('-' if not c else '#') for c, l in runs)
        if r > 0.08:
            print(f"{names[i]:>2}-{names[j]:<2} L={L:6.1f} ratio={r:.2f}  {rr[:70]}")
        else:
            print(f"{names[i]:>2}-{names[j]:<2} L={L:6.1f} ratio={r:.2f}  (blank)")

print("\n=== over/undershoot check: extend each notable segment by 20px both ends ===")
for (n1, n2) in [('A1','C1'),('D1','B'),('B1','D'),('B1','C'),('A','C'),('A','D'),('D1','C'),('D1','A'),('D','C'),('D1','D')]:
    p = np.array(V[n1], float); q = np.array(V[n2], float)
    d = q - p; L = float(np.hypot(*d)); u = d / L
    p0 = p - u * 20; q0 = q + u * 20
    _, r, runs = sample(p0, q0, trim=0)
    rr = ''.join(('-' if not c else '#') for c, l in runs)
    print(f"{n1}-{n2} ext ratio={r:.2f}  {rr[:90]}")

print("\n=== subpixel stroke width (ink integral across profiles) ===")
def width_at(x, y, nx, ny):
    # integrate darkness along normal direction over +-6 px
    tot = 0.0
    for o in np.arange(-6, 6.01, 0.25):
        xx = x + nx * o; yy = y + ny * o
        xi, yi = int(np.floor(xx)), int(np.floor(yy))
        if 0 <= yi < a.shape[0] - 1 and 0 <= xi < a.shape[1] - 1:
            # bilinear
            fx, fy = xx - xi, yy - yi
            v = (a[yi, xi] * (1-fx) * (1-fy) + a[yi, xi+1] * fx * (1-fy) +
                 a[yi+1, xi] * (1-fx) * fy + a[yi+1, xi+1] * fx * fy)
            tot += (255 - v) / 255
    return tot * 0.25

print("left  edge  A1A  :", round(np.mean([width_at(56, y, 1, 0) for y in (200, 250, 300, 350)]), 2))
print("right edge  B1B  :", round(np.mean([width_at(356, y, 1, 0) for y in (200, 250, 300, 350)]), 2))
print("back  edge  C1C  :", round(np.mean([width_at(462, y, 1, 0) for y in (100, 150, 200, 250)]), 2))
print("bottom A-B       :", round(np.mean([width_at(x, 453, 0, 1) for x in (120, 200, 280)]), 2))
print("top  A1-B1       :", round(np.mean([width_at(x, 153, 0, 1) for x in (120, 200, 280)]), 2))
print("top  D1-C1       :", round(np.mean([width_at(x, 47, 0, 1) for x in (200, 300, 400)]), 2))
n45 = np.array([-np.sin(np.pi/4), np.cos(np.pi/4)])
print("A1D1 45 solid    :", round(np.mean([width_at(108, 100, *n45), width_at(133, 75, *n45)]), 2))
print("B1C1 45 solid    :", round(np.mean([width_at(396, 112, *n45), width_at(430, 78, *n45)]), 2))
print("D1D dash (x162)  :", round(np.mean([width_at(162, 52, 1, 0), width_at(162, 72, 1, 0), width_at(162, 150, 1, 0)]), 2))
print("DC dash  (y347)  :", round(np.mean([width_at(186, 347, 0, 1), width_at(226, 347, 0, 1), width_at(305, 347, 0, 1)]), 2))
# dashed diagonals: D1A at y=180 -> (127.5,180); D1C at y=260 -> (374,260); A-C at y=400 -> (263,400)
uD1A = np.array(V['A']) - np.array(V['D1'], float); uD1A /= np.hypot(*uD1A)
uD1C = np.array(V['C'], float) - np.array(V['D1'], float); uD1C /= np.hypot(*uD1C)
uAC = np.array(V['C'], float) - np.array(V['A'], float); uAC /= np.hypot(*uAC)
nD1A = np.array([-uD1A[1], uD1A[0]]); nD1C = np.array([-uD1C[1], uD1C[0]]); nAC = np.array([-uAC[1], uAC[0]])
print("D1A dash         :", round(width_at(127.5, 180, *nD1A), 2))
print("D1C dash         :", round(width_at(374.2, 260, *nD1C), 2))
print("AC  dash         :", round(width_at(263.4, 400, *nAC), 2))

print("\n=== dash pattern from column x=162 (D1D) ===")
runs = []
cur = None
for y in range(46, 350):
    v = dark[y, 162]
    if v and cur is None: cur = y
    elif not v and cur is not None: runs.append((cur, y-1)); cur = None
dash = [b-a+1 for a,b in runs]; gaps = [runs[i+1][0]-runs[i][1]-1 for i in range(len(runs)-1)]
print("dash lengths:", dash)
print("gaps:", gaps)
print("mean dash", round(np.mean(dash[1:-1]),2), "mean gap", round(np.mean(gaps),2))

print("\n=== glyph metrics ===")
def bbox(x0,y0,w,h):
    sub = dark[y0:y0+h, x0:x0+w]
    ys, xs = np.where(sub)
    return (x0+xs.min(), y0+ys.min(), xs.max()-xs.min()+1, ys.max()-ys.min()+1, sub.sum())
for name,(x0,y0,w,h) in {
  'A':(31,457,28,26),'B':(349,461,29,25),'C':(467,340,29,26),'D':(124,331,31,25),
  'A1':(8,127,28,26),'A1sub':(39,142,10,16),'B1':(318,116,29,25),'B1sub':(349,130,10,16),
  'C1':(467,21,29,26),'C1sub':(496,35,10,16),'D1':(130,8,31,25),'D1sub':(164,22,10,16)}.items():
    print(name, bbox(x0,y0,w,h))
