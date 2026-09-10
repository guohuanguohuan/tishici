# -*- coding: utf-8 -*-
"""Two-tone map + per-segment ink color/width + arrowhead detection."""
import numpy as np
from PIL import Image

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image3.png"
img = Image.open(SRC)
print("mode:", img.mode)
a = np.array(img.convert("L")).astype(float)

vals, counts = np.unique(a.astype(int), return_counts=True)
print("histogram (top values):")
for v, c in sorted(zip(vals, counts), key=lambda t: -t[1])[:12]:
    print(f"  gray={v:3d} count={c}")

# colorized map: red = black ink (<40), blue = gray ink (40..127)
out = np.full((a.shape[0], a.shape[1], 3), 255, np.uint8)
out[a < 40] = [220, 0, 0]
out[(a >= 40) & (a < 128)] = [0, 60, 220]
Image.fromarray(out).save("twotone_map.png")
print("saved twotone_map.png")

V = {'A': (56, 453), 'B': (356.5, 453.5), 'C': (462, 349), 'D': (161.5, 348.5),
     'A1': (56, 152.5), 'B1': (356, 152.5), 'C1': (462.5, 46.5), 'D1': (162.5, 47)}
SEGS = [('AB','A','B',1),('BC','B','C',1),('CD','C','D',1),('DA','D','A',1),
        ('A1B1','A1','B1',1),('B1C1','B1','C1',1),('C1D1','C1','D1',1),('D1A1','D1','A1',1),
        ('AA1','A','A1',1),('BB1','B','B1',1),('CC1','C','C1',1),('DD1','D','D1',1),
        ('BC1','B','C1',1),('AC','A','C',1),('AD1','A','D1',1),('D1C','D1','C',1)]

def seg_profile(pname, qname, trim=8):
    p = np.array(V[pname], float); q = np.array(V[qname], float)
    d = q - p; L = float(np.hypot(*d)); u = d / L
    n = np.array([-u[1], u[0]])
    ts = np.arange(trim, L - trim, 1.0)
    ws, mins = [], []
    for t in ts:
        pt = p + u * t
        prof = []
        for o in np.arange(-4, 4.001, 0.25):
            xx, yy = pt + n * o
            xi, yi = int(np.floor(xx)), int(np.floor(yy))
            fx, fy = xx - xi, yy - yi
            v = (a[yi, xi]*(1-fx)*(1-fy) + a[yi, xi+1]*fx*(1-fy) +
                 a[yi+1, xi]*(1-fx)*fy + a[yi+1, xi+1]*fx*fy)
            prof.append(v)
        prof = np.array(prof)
        inkw = ((255 - prof) / (255 - 0) ).sum() * 0.25
        ws.append(inkw)
        mins.append(prof.min())
    ws = np.array(ws); mins = np.array(mins)
    on = ws > 0.8
    return L, np.median(ws[on]) if on.any() else 0, np.median(mins[on]) if on.any() else 255

print("\n== per segment: median ink width (px) / median darkest value ==")
for name, pn, qn, _ in SEGS:
    L, w, mn = seg_profile(pn, qn)
    ink = "BLACK" if mn < 30 else ("gray64" if 55 <= mn <= 75 else f"val{mn:.0f}")
    print(f"{name:5s} L={L:6.1f} width={w:5.2f}px darkest={mn:6.1f} -> {ink}")

print("\n== width profile near ends (arrowhead?) : every 4px, first/last 36px ==")
for name, pn, qn in [('BC1','B','C1'), ('AC','A','C'), ('D1A','D1','A'), ('D1C','D1','C'),
                     ('AD1','A','D1'), ('AD','A','D'), ('DC','D','C'), ('DD1','D','D1')]:
    p = np.array(V[pn], float); q = np.array(V[qn], float)
    d = q - p; L = float(np.hypot(*d)); u = d / L
    n = np.array([-u[1], u[0]])
    def w_at(t):
        pt = p + u * t
        tot = 0.0
        for o in np.arange(-4, 4.001, 0.25):
            xx, yy = pt + n * o
            xi, yi = int(np.floor(xx)), int(np.floor(yy))
            fx, fy = xx - xi, yy - yi
            v = (a[yi, xi]*(1-fx)*(1-fy) + a[yi, xi+1]*fx*(1-fy) +
                 a[yi+1, xi]*(1-fx)*fy + a[yi+1, xi+1]*fx*fy)
            tot += (255 - v) / 255
        return tot * 0.25
    head = [round(w_at(t), 1) for t in np.arange(3, 37, 4)]
    tail = [round(w_at(L - t), 1) for t in np.arange(3, 37, 4)]
    print(f"{name:4s} near {pn}: {head}   near {qn}: {tail}")
