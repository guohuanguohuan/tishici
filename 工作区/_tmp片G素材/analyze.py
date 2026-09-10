# -*- coding: utf-8 -*-
"""Pixel-level analysis of image3.png (cube figure) for TikZ redraw."""
import numpy as np
from PIL import Image
import cv2

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image3.png"
img = Image.open(SRC).convert("L")
a = np.array(img)
H, W = a.shape
print("size:", W, "x", H)
dark = a < 128
ys, xs = np.where(dark)
print("content bbox: x", xs.min(), "-", xs.max(), " y", ys.min(), "-", ys.max())

# ---------- line detection ----------
bw = (dark * 255).astype(np.uint8)
lines = cv2.HoughLinesP(bw, 1, np.pi / 720, threshold=18,
                        minLineLength=9, maxLineGap=4)
print("raw segments:", len(lines))

segs = [tuple(l[0]) for l in lines]

def line_params(x1, y1, x2, y2):
    th = np.arctan2(y2 - y1, x2 - x1) % np.pi
    # normal form
    rho = x1 * (-np.sin(th)) + y1 * (np.cos(th))  # normal n=(-sin,cos)
    return th, rho

groups = []
for s in segs:
    th, rho = line_params(*s)
    placed = False
    for g in groups:
        dth = min(abs(th - g['th']), np.pi - abs(th - g['th']))
        drho = abs(rho - g['rho'])
        if dth < np.deg2rad(2.5) and drho < 3.0:
            g['segs'].append(s)
            # update weighted mean
            n = len(g['segs'])
            g['th'] = g['th'] * (n - 1) / n + th / n
            g['rho'] = g['rho'] * (n - 1) / n + rho / n
            placed = True
            break
    if not placed:
        groups.append({'th': th, 'rho': rho, 'segs': [s]})

print("groups:", len(groups))

# for each group: find extent along direction, coverage
results = []
for g in groups:
    th, rho = g['th'], g['rho']
    d = np.array([np.cos(th), np.sin(th)])   # direction
    n = np.array([-np.sin(th), np.cos(th)])  # normal
    pts = []
    for (x1, y1, x2, y2) in g['segs']:
        for (x, y) in ((x1, y1), (x2, y2)):
            pts.append(np.array([x, y]))
    ts = [p @ d for p in pts]
    t0, t1 = min(ts), max(ts)
    # anchor: projection of some dark pixel; recompute rho from all pixels better:
    # sample along the line
    tsamp = np.arange(t0, t1 + 0.5, 1.0)
    cov = []
    for t in tsamp:
        p = d * t + n * rho
        x, y = int(round(p[0])), int(round(p[1]))
        hit = False
        for dy in (-2, -1, 0, 1, 2):
            yy = y + dy
            if 0 <= yy < H and 0 <= x < W and dark[yy, x]:
                hit = True
                break
        cov.append(1 if hit else 0)
    cov = np.array(cov)
    ratio = cov.mean() if len(cov) else 0
    # dash runs
    runs = []
    if len(cov):
        cur = cov[0]; ln = 0
        for c in cov:
            if c == cur:
                ln += 1
            else:
                runs.append((cur, ln)); cur = c; ln = 1
        runs.append((cur, ln))
    results.append(dict(th=th, rho=rho, t0=t0, t1=t1, ratio=ratio,
                        runs=runs, nseg=len(g['segs']), len=t1 - t0))

results.sort(key=lambda r: -r['len'])
print("\n=== candidate lines (merged), sorted by length ===")
for r in results:
    if r['len'] < 25:
        continue
    th, rho = r['th'], r['rho']
    d = np.array([np.cos(th), np.sin(th)]); n = np.array([-np.sin(th), np.cos(th)])
    p0 = d * r['t0'] + n * rho; p1 = d * r['t1'] + n * rho
    druns = [f"{'D' if c else '_'}{l}" for c, l in r['runs']]
    print(f"len={r['len']:6.1f} ratio={r['ratio']:.2f} nseg={r['nseg']:3d} "
          f"th={np.rad2deg(th):6.1f}deg rho={rho:7.1f} "
          f"({p0[0]:.0f},{p0[1]:.0f})->({p1[0]:.0f},{p1[1]:.0f}) runs={''.join(druns[:24])}")
