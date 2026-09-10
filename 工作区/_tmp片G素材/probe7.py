# -*- coding: utf-8 -*-
"""Black dashed lines: dash pattern along-line."""
import numpy as np
from PIL import Image

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image3.png"
a = np.array(Image.open(SRC).convert("L")).astype(float)
dark = a < 128

def runs_along_seg(p, q, trim=6):
    p = np.array(p, float); q = np.array(q, float)
    d = q - p; L = float(np.hypot(*d)); u = d / L
    n = np.array([-u[1], u[0]])
    hits = []
    for t in np.arange(trim, L - trim, 0.25):
        pt = p + u * t
        hit = False
        for o in np.arange(-1.5, 1.501, 0.5):
            x, y = pt + n * o
            xi, yi = int(round(x)), int(round(y))
            if dark[yi, xi]: hit = True; break
        hits.append(hit)
    runs = []
    cur, ln = hits[0], 0
    for h in hits:
        if h == cur: ln += 1
        else: runs.append((cur, ln * 0.25)); cur, ln = h, 1
    runs.append((cur, ln * 0.25))
    return L, runs

V = {'A': (56, 453), 'C': (462, 349), 'D1': (162.5, 47), 'B': (356.5, 453.5), 'C1': (462.5, 46.5)}
for nm, (p, q) in {'A-C': ('A', 'C'), 'A-D1': ('A', 'D1'), 'D1-C': ('D1', 'C'), 'B-C1': ('B', 'C1')}.items():
    L, runs = runs_along_seg(V[p], V[q])
    on = [l for c, l in runs if c]; off = [l for c, l in runs if not c]
    print(f"{nm} L={L:.0f}: n_on={len(on)} on_med={np.median(on):.2f} n_off={len(off)} off_med={np.median(off):.2f}")
    print("   pattern:", ''.join(('#' if c else '.') for c, l in runs)[:110])
