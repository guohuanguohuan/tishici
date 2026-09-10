# -*- coding: utf-8 -*-
"""Circle-fit the six vertex dots on image1 (alpha ink), excluding points near incident lines."""
import numpy as np
from PIL import Image
import json

im = Image.open(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image1.png")
al = np.array(im)[..., 3].astype(float) / 255.0
H, W = al.shape

V = json.load(open('img1_verts.json'))
F = json.load(open('img1_fits.json'))
EDGES = {k: (np.array(v[0]), np.array(v[1])) for k, v in F.items()}
# segments that actually exist (endpoints = the fitted segment ends, extended a bit)
SEGS = ['A1A', 'A1C1', 'A1B1', 'B1C1', 'B1B', 'C1C', 'AB', 'BC', 'A1B', 'A1C']


def dist_to_seg(p, a, b):
    d = b - a; L2 = (d ** 2).sum()
    t = np.clip(np.dot(p - a, d) / L2, 0, 1)
    return float(np.hypot(*(p - (a + t * d))))


def boundary_points(cx, cy, R=18):
    pts = []
    x0, x1 = int(cx - R), int(cx + R)
    y0, y1 = int(cy - R), int(cy + R)
    for y in range(y0, y1 + 1):
        row = al[y, x0:x1 + 1] > 0.5
        idx = np.where(row)[0]
        if len(idx) == 0:
            continue
        for i in (idx[0], idx[-1]):
            pts.append((x0 + i, y))
    for x in range(x0, x1 + 1):
        col = al[y0:y1 + 1, x] > 0.5
        idx = np.where(col)[0]
        if len(idx) == 0:
            continue
        for i in (idx[0], idx[-1]):
            pts.append((x, y0 + i))
    # keep only pts far from every incident line's centreline
    keep = []
    for (x, y) in pts:
        p = np.array([x + 0.0, y + 0.0])
        dmin = min(dist_to_seg(p, EDGES[k][0], EDGES[k][1]) for k in SEGS)
        if dmin > 5.0:
            keep.append(p)
    return np.array(keep)


def fit_circle(pts):
    A = np.c_[2 * pts[:, 0], 2 * pts[:, 1], np.ones(len(pts))]
    b = (pts ** 2).sum(1)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = sol[0], sol[1]
    r = np.sqrt(sol[2] + cx ** 2 + cy ** 2)
    res = np.sqrt(((pts - [cx, cy]) ** 2).sum(1)) - r
    return cx, cy, r, float(np.abs(res).max()), len(pts)


print("=== dot circle fits (boundary pts kept >5px from line centrelines) ===")
out = {}
for k, (cx0, cy0) in V.items():
    pts = boundary_points(cx0, cy0)
    cx, cy, r, mx, n = fit_circle(pts)
    out[k] = dict(cx=cx, cy=cy, r=r, maxdev=mx, npts=n)
    print("  %-2s centre=(%8.3f,%8.3f)  r=%.3f px  maxdev=%.2f  n=%d" % (k, cx, cy, r, mx, n))
    # diff vs vertex (line intersection)
    print("        vs vertex (%8.3f,%8.3f):  d=(%+.2f,%+.2f)" % (cx0, cy0, cx - cx0, cy - cy0))
json.dump(out, open('img1_dots.json', 'w'), indent=1)

# label glyph metrics recap
print("\n=== label glyph bboxes (from connected components, canvas px) ===")
lbl = {
    'A1.A': (63, 1, 111, 59), 'A1.sub': (123, 33, 138, 70),
    'C1.C': (606, 19, 663, 78), 'C1.sub': (666, 51, 681, 88),
    'B1.B': (363, 164, 415, 221), 'B1.sub': (423, 195, 438, 232),
    'A': (1, 783, 55, 850), 'C': (625, 777, 689, 845), 'B': (407, 1091, 466, 1157),
}
s = 41.1 / 691
for k, (x0, y0, x1, y1) in lbl.items():
    print("  %-6s x %3d-%3d (w%2d)  y %4d-%4d (h%2d)  -> mm w%.2f h%.2f  centre=(%.2f,%.2f)mm"
          % (k, x0, x1, x1 - x0 + 1, y0, y1, y1 - y0 + 1, (x1 - x0 + 1) * s, (y1 - y0 + 1) * s,
             (x0 + x1) / 2 * s, (y0 + y1) / 2 * s))
