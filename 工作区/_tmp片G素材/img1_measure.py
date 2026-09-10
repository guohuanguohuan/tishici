# -*- coding: utf-8 -*-
"""image1.png: sub-pixel line fits, vertex intersections, stroke widths, dash metrics, dot radius."""
import numpy as np
from PIL import Image
import json

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image1.png"
im = Image.open(SRC)
al = np.array(im)[..., 3].astype(float) / 255.0   # 0..1 ink coverage
H, W = al.shape


def bil(x, y):
    if x < 0 or y < 0 or x > W - 2 or y > H - 2:
        return 0.0
    x0, y0 = int(np.floor(x)), int(np.floor(y))
    fx, fy = x - x0, y - y0
    return (al[y0, x0] * (1 - fx) * (1 - fy) + al[y0, x0 + 1] * fx * (1 - fy) +
            al[y0 + 1, x0] * (1 - fx) * fy + al[y0 + 1, x0 + 1] * fx * fy)


def perp_centroid(px, py, nx, ny, half=9.0, hw_lim=5.0):
    """alpha-weighted centroid offset along (nx,ny), restricted to +-hw_lim of the first moment."""
    ss = np.arange(-half, half + 0.05, 0.1)
    vals = np.array([bil(px + nx * s, py + ny * s) for s in ss])
    if vals.sum() < 0.5:
        return None
    c0 = (ss * vals).sum() / vals.sum()
    m = np.abs(ss - c0) <= hw_lim
    if vals[m].sum() < 0.5:
        return None
    c1 = (ss[m] * vals[m]).sum() / vals[m].sum()
    w = vals[m].sum() * 0.1    # effective stroke width
    return c1, w


def fit_line(p0, p1, trim=8.0, it=4):
    """Return (point, unit dir, unit normal, mean width, rms) after centroid refits."""
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    for _ in range(it):
        d = p1 - p0; L = float(np.hypot(*d)); u = d / L
        n = np.array([-u[1], u[0]])
        ts_all = np.arange(trim, L - trim, 1.0)
        offs, ws, ts = [], [], []
        for t in ts_all:
            px, py = p0 + u * t
            r = perp_centroid(px, py, n[0], n[1], half=9.0, hw_lim=5.0)
            if r and r[1] > 3.0:
                offs.append(r[0]); ws.append(r[1]); ts.append(t)
        offs = np.array(offs)
        ts = np.array(ts)
        # robust: drop outliers > 1.2px from median
        med = np.median(offs)
        keep = np.abs(offs - med) < 1.2
        if keep.sum() < 5:
            break
        offs_k = offs[keep]; ts_k = ts[keep]
        # LSQ fit: point q(t) = p0 + u*t + n*off  -> fit off(t) = a + b t
        A = np.vstack([np.ones_like(ts_k), ts_k]).T
        coef, *_ = np.linalg.lstsq(A, offs_k, rcond=None)
        a, b = coef
        # rebuild endpoints
        newp0 = p0 + n * a
        newp1 = p0 + u * L + n * (a + b * L)
        p0, p1 = newp0, newp1
        res = offs_k - (a + b * ts_k)
    return p0, p1, np.mean(ws), float(np.sqrt((res ** 2).mean()))


def inter(l1, l2):
    """intersect two lines given by (p0,p1)"""
    (x1, y1), (x2, y2) = l1
    (x3, y3), (x4, y4) = l2
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / d
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / d
    return px, py


# --- initial approximate endpoints (from dot centroids) ---
V0 = {'A1': (91.4, 111.8), 'C1': (600.1, 105.4), 'B1': (419.4, 292.3),
      'A': (89.2, 874.1), 'C': (600.2, 874.0), 'B': (418.7, 1058.6)}

SEG = {
    'A1A': ('A1', 'A'), 'A1C1': ('A1', 'C1'), 'A1B1': ('A1', 'B1'),
    'B1C1': ('B1', 'C1'), 'B1B': ('B1', 'B'), 'C1C': ('C1', 'C'),
    'AB': ('A', 'B'), 'BC': ('B', 'C'), 'A1B': ('A1', 'B'), 'A1C': ('A1', 'C'),
}
fits = {}
print("=== line fits (trim 8px) ===")
for k, (n1, n2) in SEG.items():
    p0, p1, w, rms = fit_line(V0[n1], V0[n2])
    fits[k] = (p0, p1)
    d = p1 - p0
    ang = np.degrees(np.arctan2(d[1], d[0]))
    print("%-5s p0=(%7.2f,%7.2f) p1=(%7.2f,%7.2f) len=%7.2f ang=%7.2f  width=%.3f rms=%.3f"
          % (k, p0[0], p0[1], p1[0], p1[1], np.hypot(*d), ang, w, rms))

print("\n=== vertex = intersection of its two fitted edges ===")
VERT = {}
VERT['A1'] = inter(fits['A1A'], fits['A1C1'])
VERT['C1'] = inter(fits['A1C1'], fits['C1C'])
VERT['B1'] = inter(fits['A1B1'], fits['B1B'])
VERT['B'] = inter(fits['B1B'], fits['BC'])
VERT['A'] = inter(fits['A1A'], fits['AB'])
VERT['C'] = inter(fits['C1C'], fits['BC'])
for k, v in VERT.items():
    print("  %-2s = (%8.3f, %8.3f)   [dot centroid was %s]" % (k, v[0], v[1], V0[k]))

print("\n=== secondary checks: do A1B / A1C / A1B1 / A1C1 / B1C1 pass through fitted vertices? ===")
for k in ('A1B', 'A1C', 'A1B1', 'A1C1', 'B1C1'):
    p0, p1 = fits[k]
    d = p1 - p0; L = np.hypot(*d); u = d / L; n = np.array([-u[1], u[0]])
    # distance of fitted vertex A1, B, C, B1, C1 from this infinite line
    for name, v in VERT.items():
        dist = float(np.dot(np.array(v) - p0, n))
        if abs(dist) < 3:
            print("   %-5s passes %-2s at %+.2f px (t/L=%.3f)" % (k, name, dist, np.dot(np.array(v) - p0, u) / L))

print("\n=== dash metrics along A-C (dashed, y~874) ===")


def dash_profile(p, q, half=1.2):
    p = np.array(p, float); q = np.array(q, float)
    d = q - p; L = float(np.hypot(*d)); u = d / L; n = np.array([-u[1], u[0]])
    ts = np.arange(0, L, 0.25)
    prof = []
    for t in ts:
        pt = p + u * t
        v = 0.0
        for o in np.arange(-half, half + 0.01, 0.1):
            v = max(v, bil(*(pt + n * o)))
        prof.append(v)
    return ts, np.array(prof)


def runs_of(ts, prof, thr=0.5):
    on = prof > thr
    out = []
    i = 0
    while i < len(on):
        j = i
        while j < len(on) and on[j] == on[i]:
            j += 1
        out.append((on[i], ts[i], ts[j - 1], ts[j - 1] - ts[i]))
        i = j
    return out


ts, prof = dash_profile(VERT['A'], VERT['C'])
rr = runs_of(ts, prof)
print("  A-C total len %.2f" % (ts[-1]))
for st, t0, t1, ln in rr[:14]:
    print("   %s %7.2f..%7.2f  len=%6.2f" % ('DASH' if st else 'gap ', t0, t1, ln))

ts, prof = dash_profile(VERT['A1'], VERT['C'])
rr = runs_of(ts, prof)
print("  A1-C total len %.2f" % (ts[-1]))
seg_on = [(t0, t1, ln) for st, t0, t1, ln in rr if st]
seg_off = [(t0, t1, ln) for st, t0, t1, ln in rr if not st]
print("   dashes:", ["%.1f" % l for _, _, l in seg_on])
print("   gaps  :", ["%.1f" % l for _, _, l in seg_off])

print("\n=== dot radius (B dot: no ink below) ===")
bx, by = VERT['B']
for dy in range(0, 22):
    y = int(round(by)) + dy
    row = al[y, int(bx) - 20:int(bx) + 21]
    s = ''.join('#' if v > 0.5 else ('+' if v > 0.15 else '.') for v in row)
    print("  y=%4d %s" % (y, s))

print("\n=== stroke width table (alpha integral, perpendicular) ===")
for k in ('A1A', 'C1C', 'B1B', 'A1C1', 'A1B1', 'B1C1', 'AB', 'BC', 'A1B'):
    p0, p1 = fits[k]
    d = p1 - p0; L = np.hypot(*d); u = d / L; n = np.array([-u[1], u[0]])
    ws = []
    for t in np.linspace(L * 0.25, L * 0.75, 9):
        pt = p0 + u * t
        ss = np.arange(-8, 8, 0.05)
        vals = np.array([bil(*(pt + n * s)) for s in ss])
        ws.append(vals.sum() * 0.05)
    print("  %-5s width mean=%.3f  sd=%.3f" % (k, np.mean(ws), np.std(ws)))

# dashed line widths: sample at dash centers
for nm, (P, Q) in (('A-C dash', (VERT['A'], VERT['C'])), ('A1-C dash', (VERT['A1'], VERT['C']))):
    P = np.array(P, float); Q = np.array(Q, float)
    d = Q - P; L = np.hypot(*d); u = d / L; n = np.array([-u[1], u[0]])
    ws = []
    for t in np.linspace(0.2 * L, 0.8 * L, 40):
        pt = P + u * t
        ss = np.arange(-8, 8, 0.05)
        vals = np.array([bil(*(pt + n * s)) for s in ss])
        w = vals.sum() * 0.05
        if w > 3:   # inside a dash
            ws.append(w)
    print("  %-9s width mean=%.3f n=%d" % (nm, np.mean(ws), len(ws)))

json.dump({k: [list(map(float, v)) for v in val] for k, val in fits.items()},
          open('img1_fits.json', 'w'), indent=1)
json.dump({k: [float(v[0]), float(v[1])] for k, v in VERT.items()},
          open('img1_verts.json', 'w'), indent=1)
print("\nsaved img1_fits.json / img1_verts.json")
