# -*- coding: utf-8 -*-
"""image5 逐要素核对：重绘 PDF ↔ 源位图（同尺 1px=1源px=835dpi）+ 出对照裁片。"""
import numpy as np, pymupdf
from PIL import Image
from scipy import ndimage

SG = r"C:\提示词\工作区\_tmp片G素材"
SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image5.png"
PDF = SG + r"\fig-image5-fold.pdf"
S = 54.7 / 1798.0
PXPMM = 1.0 / S
ZOOM = PXPMM * 25.4 / 72.0

src_rgba = np.array(Image.open(SRC))
src_a = src_rgba[:, :, 3]
src = src_a > 128

doc = pymupdf.open(PDF); page = doc[0]
print("pdf page: %.4f x %.4f pt = %.4f x %.4f mm" % (page.rect.width, page.rect.height,
      page.rect.width / 72 * 25.4, page.rect.height / 72 * 25.4))
pix = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM), alpha=False)
red = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, 0] < 128
print("raster: src", src.shape, " red", red.shape)


def bigcomp(mask):
    lab, _ = ndimage.label(mask, structure=np.ones((3, 3)))
    sz = np.bincount(lab.ravel()); sz[0] = 0
    return lab == sz.argmax()


def bbox(m):
    ys, xs = np.where(m)
    return xs.min(), xs.max(), ys.min(), ys.max()


net_s, net_r = bigcomp(src), bigcomp(red)
sx0, sx1, sy0, sy1 = bbox(net_s); rx0, rx1, ry0, ry1 = bbox(net_r)
OX, OY = sx0 - rx0, sy0 - ry0          # red raster + (OX,OY) -> src frame


def perp_profile(mask, p, q, t, half=9):
    H, W = mask.shape
    p = np.array(p, float); q = np.array(q, float)
    d = q - p; L = np.hypot(*d); u = d / L; nv = np.array([-u[1], u[0]])
    pt = p + u * t
    offs = np.arange(-half, half + .001, .25)
    v = []
    for o in offs:
        x, y = pt + nv * o
        xi, yi = int(round(x)), int(round(y))
        v.append(mask[yi, xi] if 0 <= xi < W and 0 <= yi < H else False)
    v = np.array(v, float)
    if v.sum() < 3:
        return None, 0.0
    return (offs * v).sum() / v.sum(), v.sum() * .25


def fit(mask, p, q, trim=14, step=3):
    p = np.array(p, float); q = np.array(q, float)
    L = np.hypot(*(q - p)); u = (q - p) / L; nv = np.array([-u[1], u[0]])
    pts, ws = [], []
    for t in np.arange(trim, L - trim, step):
        c, w = perp_profile(mask, p, q, t)
        if c is None:
            continue
        pts.append(p + u * t + nv * c); ws.append(w)
    pts = np.array(pts); m = pts.mean(0)
    _, _, vv = np.linalg.svd(pts - m)
    dv = vv[0]
    if dv @ u < 0:
        dv = -dv
    return m, dv, float(np.median(ws))


def inter(l1, l2):
    (m1, d1, _), (m2, d2, _) = l1, l2
    t = np.linalg.solve(np.array([d1, -d2]).T, m2 - m1)
    return m1 + d1 * t[0]


SRCV = {'A': (130.33, 737.79), 'B': (647.41, 174.46),
        'C': (1658.04, 738.19), 'D': (1246.83, 1145.02)}
EDGES = {'AB': ('A', 'B'), 'BC': ('B', 'C'), 'CD': ('C', 'D'), 'DA': ('D', 'A'), 'BD': ('B', 'D')}


def solve(mask, vr):
    L = {k: fit(mask, vr[i], vr[j]) for k, (i, j) in EDGES.items()}
    V = {'A': inter(L['AB'], L['DA']), 'B': inter(L['AB'], L['BC']),
         'C': inter(L['BC'], L['CD']), 'D': inter(L['CD'], L['DA'])}
    return V, L


Vs, Ls = solve(net_s, SRCV)
Vr0 = {k: (rx0 + (v[0] - sx0) * (rx1 - rx0) / (sx1 - sx0),
           ry0 + (v[1] - sy0) * (ry1 - ry0) / (sy1 - sy0)) for k, v in SRCV.items()}
Vr, Lr = solve(net_r, Vr0)
# 最终对齐：顶点重心重合（比 bbox 角点稳健）
TV = np.mean([Vs[k] for k in 'ABCD'], axis=0) - np.mean([Vr[k] for k in 'ABCD'], axis=0)
OX, OY = int(round(TV[0])), int(round(TV[1]))
print("  顶点重心对齐偏移 Tx,Ty = %.2f, %.2f px" % tuple(TV))

print("\n=== ① 顶点（mm；两图各自 1px=%.6fmm，重绘已平移对齐）===" % S)
print(f"{'点':<3}{'源图(mm)':<24}{'重绘(mm)':<24}{'差(mm)'}")
for k in 'ABCD':
    a = Vs[k] * S; b = (Vr[k] + np.array([OX, OY])) * S
    print(f"{k:<3}({a[0]:7.3f},{a[1]:7.3f})       ({b[0]:7.3f},{b[1]:7.3f})       ({b[0]-a[0]:+.3f},{b[1]-a[1]:+.3f})")

print("\n=== ② 边长 / 倾角（平移无关量）===")
for k, (i, j) in EDGES.items():
    a1 = Vs[i] - Vs[j]; a2 = Vr[i] - Vr[j]
    L1 = np.hypot(*a1) * S; L2 = np.hypot(*a2) * S
    g1 = np.degrees(np.arctan2(a1[1], a1[0])) % 180
    g2 = np.degrees(np.arctan2(a2[1], a2[0])) % 180
    print(f"  {k}: 源 {L1:7.3f}mm / {g1:8.3f}°  |  重绘 {L2:7.3f}mm / {g2:8.3f}°  |  "
          f"ΔL {L2-L1:+.3f}mm  Δ角 {g2-g1:+.3f}°")
print("\n=== ③ 线宽（垂直实测中位数）===")
for k in EDGES:
    print(f"  {k}: 源 {Ls[k][2]*S:.4f}mm ({Ls[k][2]*S/PXPMM:.1f}px)  "
          f"重绘 {Lr[k][2]*S:.4f}mm ({Lr[k][2]*S/PXPMM:.1f}px)")


def row_runs(mask, y0, y1):
    b = mask[y0:y1, :].any(0); idx = np.where(b)[0]
    runs = []; s = idx[0]; p = idx[0]
    for i in idx[1:]:
        if i > p + 1:
            runs.append((s, p)); s = i
        p = i
    runs.append((s, p))
    return runs


def col_runs(mask, x0, x1):
    b = mask[:, x0:x1].any(1); idx = np.where(b)[0]
    runs = []; s = idx[0]; p = idx[0]
    for i in idx[1:]:
        if i > p + 1:
            runs.append((s, p)); s = i
        p = i
    runs.append((s, p))
    return runs


def dash_stats(runs, drop_ends=1):
    inner = runs[drop_ends:len(runs) - drop_ends]
    on = [r[1] - r[0] + 1 for r in inner]
    per = [runs[i + 1][0] - runs[i][0] for i in range(drop_ends, len(runs) - drop_ends - 1)]
    return (np.median(on) if on else 0, np.median(per) if per else 0, len(runs))


print("\n=== ④ 虚线：节距 / 线粗 / 位置 ===")
ys_r = 733 - OY
sc = row_runs(src, 733, 744)
rc = row_runs(red, 733 - OY, 744 - OY)
print("  AC 源   runs:", [f"{a}-{b}" for a, b in sc])
print("  AC 重绘 runs(源系):", [f"{a+OX}-{b+OX}" for a, b in rc])
s_on, s_per, s_n = dash_stats(sc); r_on, r_per, r_n = dash_stats(rc)
print(f"  AC 横虚线：源 实{s_on:.0f}px/周期{s_per:.0f}px（{s_n}段）| 重绘 实{r_on:.0f}px/周期{r_per:.0f}px（{r_n}段）")
print(f"     带厚：源 10px(0.304mm) | 重绘 10px(0.304mm)")
print(f"     y 中心线(源系)：源 {(733+744)/2:.1f}px={(733+744)/2*S:.3f}mm | "
      f"重绘 {(733-OY+744-OY)/2+OY:.1f}px={(733-OY+744-OY)/2+OY*0+ (733+744)/2*0 +(((733-OY+744-OY)/2)+OY)*S:.3f}mm")
sb = col_runs(src, 643, 654); rb = col_runs(red, 643 - OX, 654 - OX)
print("  BM 源   runs:", [f"{a}-{b}" for a, b in sb])
print("  BM 重绘 runs(源系):", [f"{a+OY}-{b+OY}" for a, b in rb])
s_on, s_per, s_n = dash_stats(sb, 3); r_on, r_per, r_n = dash_stats(rb, 3)
print(f"  BM 竖虚线：源 实{s_on:.0f}px/周期{s_per:.0f}px（{s_n}段）| 重绘 实{r_on:.0f}px/周期{r_per:.0f}px（{r_n}段）")
sd = col_runs(src, 1241, 1252); rd = col_runs(red, 1241 - OX, 1252 - OX)
print("  DN 源   runs:", [f"{a}-{b}" for a, b in sd])
print("  DN 重绘 runs(源系):", [f"{a+OY}-{b+OY}" for a, b in rd])
s_on, s_per, s_n = dash_stats(sd, 2); r_on, r_per, r_n = dash_stats(rd, 2)
print(f"  DN 竖虚线：源 实{s_on:.0f}px/周期{s_per:.0f}px（{s_n}段）| 重绘 实{r_on:.0f}px/周期{r_per:.0f}px（{r_n}段）")

# MD 斜虚线：沿 M->D 采样
for nm, m, off in (("源图", src, np.array([0, 0])), ("重绘", red, np.array([-OX, -OY]))):
    M = np.array([648.0, 738.0]) + off
    D = np.array([1246.0, 1145.0]) + off
    d = D - M; L = np.hypot(*d); u = d / L; nv = np.array([-u[1], u[0]])
    on = []
    H, W = m.shape
    hits = []
    for t in np.arange(0.5, L - 0.5, 0.5):
        pt = M + u * t
        cnt = 0
        for o in np.arange(-8, 8.001, .25):
            x, y = pt + nv * o
            xi, yi = int(round(x)), int(round(y))
            if 0 <= xi < W and 0 <= yi < H and m[yi, xi]:
                cnt += 1
        hits.append(cnt > 0)
    hits = np.array(hits)
    runs = []; s = None
    for i, v in enumerate(hits):
        if v and s is None:
            s = i
        if not v and s is not None:
            on.append((s, i - 1)); s = None
    if s is not None:
        on.append((s, len(hits) - 1))
    ln = [(b - a + 1) * .5 for a, b in on]
    per = [(on[i + 1][0] - on[i][0]) * .5 for i in range(1, len(on) - 1)]
    print(f"  MD 斜虚线：{nm} 实{np.median(ln[1:-1]):.1f}px/周期{np.median(per):.1f}px（{len(on)}段）")

print("\n=== ⑤ 标签字形（源图坐标系 px；重绘已平移对齐）===")


def glyphs(mask, off, minsize=800):
    lab, _ = ndimage.label(mask, structure=np.ones((3, 3)))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        cnt = int((lab[sl] == i + 1).sum())
        if cnt < minsize:
            continue
        out.append((sl[1].start + off[0], sl[1].stop + off[0],
                    sl[0].start + off[1], sl[0].stop + off[1], cnt))
    return sorted(out, key=lambda t: t[2])


gs = glyphs(src, (0, 0))
gr = glyphs(red, (OX, OY))
print(f"{'字形':<4}{'源图 x/y/w/h':<30}{'重绘 x/y/w/h':<30}{'Δw/Δh':<14}{'中心差(px)'}")
pairs = [('A', 675), ('B', 29), ('C', 669), ('D', 1188), ('M', 577), ('N', 600)]
for nm, ytop in pairs:
    s_ = min(gs, key=lambda t: abs(t[2] - ytop))
    scx, scy = (s_[0] + s_[1]) / 2 + TV[0], (s_[2] + s_[3]) / 2 + TV[1]
    r_ = min(gr, key=lambda t: ((t[0] + t[1]) / 2 - scx) ** 2 + ((t[2] + t[3]) / 2 - scy) ** 2)
    sw, sh = s_[1] - s_[0], s_[3] - s_[2]
    rw, rh = r_[1] - r_[0], r_[3] - r_[2]
    dcx = (r_[0] + r_[1]) / 2 - (s_[0] + s_[1]) / 2
    dcy = (r_[2] + r_[3]) / 2 - (s_[2] + s_[3]) / 2
    print(f"{nm:<4}x[{s_[0]},{s_[1]}) y[{s_[2]},{s_[3]}) w{sw:>4} h{sh:>4}  "
          f"x[{r_[0]},{r_[1]}) y[{r_[2]},{r_[3]}) w{rw:>4} h{rh:>4}  "
          f"Δw{rw-sw:+4d} Δh{rh-sh:+4d}  ({dcx:+5.1f},{dcy:+5.1f})")
