# -*- coding: utf-8 -*-
"""Fit dash phase per line: source pattern vs (on 1.82mm, off 1.40mm) from a given anchor."""
import numpy as np
from PIL import Image

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image3.png"
a = np.array(Image.open(SRC).convert("L")).astype(float)
dark = a < 128
P = 0.165067  # mm per px (x); negligible diff for y

V = {'A': (56, 453), 'B': (356.5, 453.5), 'C': (462, 349), 'D': (161.5, 348.5),
     'A1': (56, 152.5), 'B1': (356, 152.5), 'C1': (462.5, 46.5), 'D1': (162.5, 47)}

ON, OFF, PER = 1.82, 1.40, 3.22

def sample_on(p, q, trim_mm=0.35):
    p = np.array(p, float); q = np.array(q, float)
    d = q - p; L_px = float(np.hypot(*d)); u = d / L_px
    n = np.array([-u[1], u[0]])
    ts = np.arange(trim_mm/P, L_px - trim_mm/P, 0.2)
    out = []
    for t in ts:
        pt = p + u * t
        hit = False
        for o in np.arange(-1.5, 1.51, 0.5):
            x, y = pt + n * o
            if dark[int(round(y)), int(round(x))]: hit = True; break
        out.append((t*P, hit))
    return out

def fit(samples):
    best = (None, 1e9)
    for phi in np.arange(0, PER, 0.02):
        err = 0
        for (s_mm, hit) in samples:
            pos = (s_mm + phi) % PER
            pred = pos < ON
            if pred != hit: err += 1
        if err < best[1]: best = (phi, err)
    frac = best[1] / len(samples)
    return best[0], frac

for nm, (pn, qn) in {'AD  (A->D)': ('A', 'D'), 'DC  (C->D)': ('C', 'D'), 'D1D (D1->D)': ('D1', 'D'),
                     'A-D1(A->D1)': ('A', 'D1'), 'D1-C(D1->C)': ('D1', 'C'), 'A-C (A->C)': ('A', 'C')}.items():
    smp = sample_on(V[pn], V[qn])
    phi, frac = fit(smp)
    rr = ''.join('#' if h else '.' for _, h in smp)
    print(f"{nm}: phase={phi:.2f}mm mismatch={frac*100:.1f}%")
    print("   ", rr[:100])
