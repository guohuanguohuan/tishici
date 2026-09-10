# -*- coding: utf-8 -*-
"""image5: precise centerline/vertex/width/dash metrics."""
import numpy as np
from PIL import Image

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image5.png"
im = Image.open(SRC)
alpha = np.array(im)[:, :, 3].astype(float) / 255.0
H, W = alpha.shape
ink = alpha > 0.5

# --- component containing the solid line network: seed at B vertex neighbourhood
from scipy import ndimage
lab, n = ndimage.label(ink, structure=np.ones((3, 3)))
sizes = np.bincount(lab.ravel()); sizes[0] = 0
big = (lab == sizes.argmax())         # solid-line network = largest comp
print("big comp px:", big.sum(), "of", ink.sum())


def perp_profile(mask, p, q, t, half=9):
    """centroid offset perpendicular to p->q at arclength t"""
    p = np.array(p, float); q = np.array(q, float)
    d = q - p; L = np.hypot(*d); u = d / L; nvec = np.array([-u[1], u[0]])
    pt = p + u * t
    offs = np.arange(-half, half + 0.001, 0.25)
    vals = []
    for o in offs:
        x, y = pt + nvec * o
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < W and 0 <= yi < H:
            vals.append(mask[yi, xi])
        else:
            vals.append(False)
    vals = np.array(vals, float)
    if vals.sum() < 3:
        return None, 0.0
    c = (offs * vals).sum() / vals.sum()
    width = vals.sum() * 0.25
    return c, width


def fit_line(mask, p, q, trim=14, step=3, half=9):
    p = np.array(p, float); q = np.array(q, float)
    L = np.hypot(*(q - p)); u = (q - p) / L; nvec = np.array([-u[1], u[0]])
    pts, ws = [], []
    for t in np.arange(trim, L - trim, step):
        c, w = perp_profile(mask, p, q, t, half)
        if c is None:
            continue
        pts.append(p + u * t + nvec * c); ws.append(w)
    pts = np.array(pts)
    # total least squares
    m = pts.mean(0)
    uu, ss, vv = np.linalg.svd(pts - m)
    dirv = vv[0]
    if dirv @ u < 0:
        dirv = -dirv
    return m, dirv, np.median(ws), len(pts)


def inter(l1, l2):
    (m1, d1, _, _), (m2, d2, _, _) = l1, l2
    A = np.array([d1, -d2]).T
    b = m2 - m1
    t = np.linalg.solve(A, b)
    return m1 + d1 * t[0]


# rough endpoints (original px coords)
R = {
    'A':  (126, 740), 'B': (649, 172), 'C': (1663, 740), 'D': (1250, 1149),
}
edges = {
    'AB': (R['A'], R['B']), 'BC': (R['B'], R['C']),
    'AD': (R['A'], R['D']), 'CD': (R['C'], R['D']),
    'BD': (R['B'], R['D']),
}
L = {}
for k, (p, q) in edges.items():
    m, d, w, cnt = fit_line(big, p, q)
    L[k] = (m, d, w, cnt)
    ang = np.degrees(np.arctan2(d[1], d[0])) % 180
    print(f"{k}: dir=({d[0]:+.5f},{d[1]:+.5f}) ang={ang:7.3f}  width={w*0.25*4:.2f}px  n={cnt}")

VB = inter(L['AB'], L['BC']); VA = inter(L['AB'], L['AD'])
VC = inter(L['BC'], L['CD']); VD = inter(L['AD'], L['CD'])
print("\nvertices:")
for nm, v in (('A', VA), ('B', VB), ('C', VC), ('D', VD)):
    print(f"  {nm} = ({v[0]:.2f}, {v[1]:.2f})")
print("  check BD vs B,D:", inter(L['BD'], L['AB']), inter(L['BD'], L['BC']))

# --- dashed lines ---
def dashed_metrics(x0, x1, y0, y1, axis):
    """axis='h': scan row y=cy; returns dash runs along x."""
    runs = []
    if axis == 'h':
        row = ink[y0:y1, :].any(0)
        idx = np.where(row)[0]
    else:
        col = ink[:, x0:x1].any(1)
        idx = np.where(col)[0]
    if len(idx) == 0:
        return []
    start = idx[0]; prev = idx[0]
    for i in idx[1:]:
        if i > prev + 1:
            runs.append((start, prev)); start = i
        prev = i
    runs.append((start, prev))
    return runs


print("\nAC dashed row y[733,743):")
runs = dashed_metrics(0, 0, 733, 743, 'h')
print("  n=", len(runs))
for r in runs[:6]:
    print("   ", r, "len", r[1] - r[0] + 1)
seg = [r[1] - r[0] + 1 for r in runs[1:-1]]
per = [runs[i + 1][0] - runs[i][0] for i in range(1, min(len(runs) - 1, 18))]
print("  median dash len:", np.median(seg), " median period:", np.median(per))

print("\nBM dashed col x[643,653):")
runs = dashed_metrics(643, 653, 0, 0, 'v')
print("  n=", len(runs), runs[:4])
print("  median dash len:", np.median([r[1] - r[0] + 1 for r in runs[1:-1]]),
      " median period:", np.median([runs[i + 1][0] - runs[i][0] for i in range(1, len(runs) - 1)]))

print("\nDN dashed col x[1241,1251):")
runs = dashed_metrics(1241, 1251, 0, 0, 'v')
print("  n=", len(runs), runs[:4])
print("  median dash len:", np.median([r[1] - r[0] + 1 for r in runs[1:-1]]),
      " median period:", np.median([runs[i + 1][0] - runs[i][0] for i in range(1, len(runs) - 1)]))

# --- MD dashed line width & dash pattern (sample along the line) ---
M = np.array([648.0, 738.0]); 
pq = VD - M
Lmd = np.hypot(*pq); u = pq / Lmd; nv = np.array([-u[1], u[0]])
print(f"\nMD: from M(648,738) to D({VD[0]:.1f},{VD[1]:.1f}) len={Lmd:.1f}px dir=({u[0]:+.4f},{u[1]:+.4f})")
prof = []
for t in np.arange(0, Lmd, 0.5):
    pt = M + u * t
    hit = 0; wid = 0.0
    for o in np.arange(-8, 8.001, 0.25):
        x, y = pt + nv * o
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < W and 0 <= yi < H and ink[yi, xi]:
            hit += 1
    prof.append((t, hit))
prof = np.array(prof)
# runs of "on"
on = prof[:, 1] > 0
runs = []
start = None
for i, v in enumerate(on):
    if v and start is None: start = i
    if not v and start is not None:
        runs.append((prof[start, 0], prof[i - 1, 0])); start = None
if start is not None: runs.append((prof[start, 0], prof[-1, 0]))
print("  MD dash runs (arclen):")
for r in runs:
    print(f"    {r[0]:7.1f} -> {r[1]:7.1f}  len={r[1]-r[0]:5.1f}  gap_next={'' }")
lens = [r[1] - r[0] for r in runs[1:-1]]
pers = [runs[i + 1][0] - runs[i][0] for i in range(1, len(runs) - 1)]
print("  median on:", np.median(lens) if lens else None, " median period:", np.median(pers) if pers else None)
print("  max perpendicular hits (=> width px):", prof[:, 1].max() * 0.25)
