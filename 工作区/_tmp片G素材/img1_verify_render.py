# -*- coding: utf-8 -*-
"""Final verification: geometry/线宽/虚线/点 from the 600dpi render vs source measurements."""
import numpy as np
from PIL import Image
import json

im = 1.0 - np.array(Image.open('_img1_render600.png').convert('L')).astype(float) / 255.0
HR, WR = im.shape
PX = 25.4 / 600.0                       # mm per render px
S1 = 41.1 / 691                         # mm per source px
HS = 1159


def bil(x, y):
    if x < 0 or y < 0 or x > WR - 2 or y > HR - 2:
        return 0.0
    x0, y0 = int(np.floor(x)), int(np.floor(y))
    fx, fy = x - x0, y - y0
    return (im[y0, x0]*(1-fx)*(1-fy) + im[y0, x0+1]*fx*(1-fy) +
            im[y0+1, x0]*(1-fx)*fy + im[y0+1, x0+1]*fx*fy)


def mm2px(X, Y):
    return X / PX, HR - Y / PX


def perp_centroid(px, py, nx, ny, half=9.0, hw_lim=5.0):
    ss = np.arange(-half, half + 0.05, 0.1)
    vals = np.array([bil(px + nx * s, py + ny * s) for s in ss])
    if vals.sum() < 0.5:
        return None
    c0 = (ss * vals).sum() / vals.sum()
    m = np.abs(ss - c0) <= hw_lim
    if vals[m].sum() < 0.5:
        return None
    return (ss[m]*vals[m]).sum()/vals[m].sum(), vals[m].sum()*0.1


def fit_line(P, Q, trim=10.0, it=4):
    P = np.array(P, float); Q = np.array(Q, float)
    for _ in range(it):
        d = Q - P; L = float(np.hypot(*d)); u = d / L; n = np.array([-u[1], u[0]])
        offs, ws, ts = [], [], []
        for t in np.arange(trim, L - trim, 1.0):
            r = perp_centroid(*(P + u*t), n[0], n[1])
            if r and r[1] > 3.0:
                offs.append(r[0]); ws.append(r[1]); ts.append(t)
        if len(offs) < 5:
            return None
        offs = np.array(offs); ts = np.array(ts)
        med = np.median(offs); keep = np.abs(offs - med) < 1.2
        A = np.vstack([np.ones(keep.sum()), ts[keep]]).T
        (a, b), *_ = np.linalg.lstsq(A, offs[keep], rcond=None)
        P, Q = P + n*a, P + u*L + n*(a + b*L)
    return P, Q, float(np.mean(ws))


def inter(l1, l2):
    (x1, y1), (x2, y2) = l1; (x3, y3), (x4, y4) = l2
    d = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    return (((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4))/d,
            ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4))/d)


# intended (mm) vertices from the fragment
Vmm = {'A1': (5.235, 62.684), 'C1': (35.717, 62.684), 'B1': (24.936, 51.534),
       'A': (5.234, 16.961), 'C': (35.717, 16.952), 'B': (24.935, 5.798)}
PXV = {k: np.array(mm2px(*v)) for k, v in Vmm.items()}
SEG = {'A1A': ('A1', 'A'), 'A1C1': ('A1', 'C1'), 'A1B1': ('A1', 'B1'), 'B1C1': ('B1', 'C1'),
       'B1B': ('B1', 'B'), 'C1C': ('C1', 'C'), 'AB': ('A', 'B'), 'BC': ('B', 'C'),
       'A1B': ('A1', 'B'), 'A1C': ('A1', 'C')}
fits, widths = {}, {}
print("=== render line fits (mm) ===")
for k, (a, b) in SEG.items():
    r = fit_line(PXV[a], PXV[b])
    if r is None:
        print("  %-5s FIT FAILED (no ink?)" % k); continue
    p0, p1, w = r
    fits[k] = (p0, p1); widths[k] = w * PX
    print("  %-5s (%.3f,%.3f)->(%.3f,%.3f)  width=%.3f mm" %
          (k, p0[0]*PX, (HR-p0[1])*PX, p1[0]*PX, (HR-p1[1])*PX, w*PX))
VERT = {}
VERT['A1'] = inter(fits['A1A'], fits['A1C1']); VERT['C1'] = inter(fits['A1C1'], fits['C1C'])
VERT['B1'] = inter(fits['A1B1'], fits['B1B']); VERT['B'] = inter(fits['B1B'], fits['BC'])
VERT['A'] = inter(fits['A1A'], fits['AB']); VERT['C'] = inter(fits['C1C'], fits['BC'])
print("\n=== vertex check (render mm vs intended mm) ===")
vs = json.load(open('img1_verts.json'))
maxd = 0
for k, (px, py) in VERT.items():
    X, Y = px*PX, (HR-py)*PX
    tx, ty = vs[k][0]*S1, (HS-vs[k][1])*S1
    d = np.hypot(X-tx, Y-ty); maxd = max(maxd, d)
    print("  %-2s ren=(%.3f,%.3f) src=(%.3f,%.3f)  d=%.3f mm" % (k, X, Y, tx, ty, d))
print("  max vertex deviation vs source-fit: %.3f mm" % maxd)

print("\n=== stroke width (render) ===")
ws = [widths[k] for k in widths]
print("  mean %.3f mm (src 6.22px = %.3f mm), range %.3f~%.3f" % (np.mean(ws), 6.22*S1, min(ws), max(ws)))

print("\n=== dash pattern (render, along A-C and A1-C) ===")
for nm, (a, b) in (('A-C', (VERT['A'], VERT['C'])), ('A1-C', (VERT['A1'], VERT['C']))):
    P = np.array(a, float); Q = np.array(b, float)
    d = Q-P; L = float(np.hypot(*d)); u = d/L; n = np.array([-u[1], u[0]])
    ts = np.arange(0, L, 0.25)
    prof = np.array([max(bil(*(P+u*t+n*o)) for o in np.arange(-1.0, 1.01, 0.1)) for t in ts])
    on = prof > 0.5
    runs, i = [], 0
    while i < len(on):
        j = i
        while j < len(on) and on[j] == on[i]:
            j += 1
        runs.append((bool(on[i]), (j-i)*0.25*PX))
        i = j
    onl = [l for st, l in runs if st]; offl = [l for st, l in runs if not st]
    print("  %-5s L=%.3fmm  first=%s  on: %s" % (nm, L*PX, 'dash' if runs[0][0] else 'gap',
          ' '.join('%.2f' % v for v in onl[:8])))
    print("        gaps: %s" % ' '.join('%.2f' % v for v in offl[:8]))

print("\n=== dot radius (render, B dot; lower arc only) ===")
bx, by = mm2px(*Vmm['B'])
ys, xs = np.where(im > 0.5)
pts = []
for yy in range(int(by), int(by) + 30):
    row = np.where(im[yy, int(bx)-25:int(bx)+25] > 0.5)[0]
    if len(row):
        pts.append((int(bx)-25+row[0], yy)); pts.append((int(bx)-25+row[-1], yy))
P = np.array(pts, float)
A = np.c_[2*P[:, 0], 2*P[:, 1], np.ones(len(P))]
sol, *_ = np.linalg.lstsq(A, (P**2).sum(1), rcond=None)
cx, cy = sol[0], sol[1]; r = np.sqrt(sol[2] + cx**2 + cy**2)
print("  r = %.3f mm (src 8.92px = %.3f mm); centre (%.3f,%.3f) vs B (%.3f,%.3f)"
      % (r*PX, 8.92*S1, cx*PX, (HR-cy)*PX, Vmm['B'][0], Vmm['B'][1]))

print("\n=== line inventory: coverage of all 15 vertex pairs (render) ===")
names = list(Vmm)
for i in range(6):
    for j in range(i+1, 6):
        a, b = names[i], names[j]
        P = PXV[a]; Q = PXV[b]
        d = Q-P; L = float(np.hypot(*d)); u = d/L
        ts = np.arange(8, L-8, 0.5)
        hit = 0
        for t in ts:
            pt = P + u*t
            best = False
            for o in np.arange(-1.0, 1.01, 0.25):
                nvec = np.array([-u[1], u[0]])
                if bil(*(pt+nvec*o)) > 0.5:
                    best = True; break
            hit += best
        ratio = hit/len(ts) if len(ts) else 0
        flag = 'SOLID' if ratio > 0.9 else ('DASHED' if ratio > 0.4 else ('partial %.2f' % ratio if ratio > 0.05 else 'absent'))
        print("  %-2s-%-2s cov=%.2f -> %s" % (a, b, ratio, flag))
