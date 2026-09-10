# 片G · sub3 几何量测对比：源 vs 重绘，逐条线测「中心位置 / 线宽」，输出 Δ（重绘−源，源 px）
# 用法：python sub3_probe.py
import numpy as np
import math
from PIL import Image

S = 1.0
def load(f):
    return np.array(Image.open(f).convert("L")).astype(float) / 255.0 < 0.5
src = load("sub3_source.png")
red = load("sub3_render1x.png")
H, W = src.shape

def hline(img, x0, x1, yc, band, step=2):
    """水平线：逐列取带内墨迹段中心，返回 (中位 y, 中位厚度, 列数)"""
    ys = []; th = []
    for xp in range(x0, x1, step):
        X = int(xp * S)
        col = img[max(0, int((yc - band) * S)):int((yc + band) * S), X]
        idx = np.nonzero(col)[0]
        if len(idx) == 0:
            continue
        ys.append((idx.mean() + int((yc - band) * S)) / S)
        th.append(len(idx) / S)
    if not ys:
        return None
    return float(np.median(ys)), float(np.median(th)), len(ys)

def vline(img, y0, y1, xc, band, step=2):
    xs = []; th = []
    for yp in range(y0, y1, step):
        Y = int(yp * S)
        row = img[Y, max(0, int((xc - band) * S)):int((xc + band) * S)]
        idx = np.nonzero(row)[0]
        if len(idx) == 0:
            continue
        xs.append((idx.mean() + int((xc - band) * S)) / S)
        th.append(len(idx) / S)
    if not xs:
        return None
    return float(np.median(xs)), float(np.median(th)), len(xs)

def seg_off(img, p0, p1, ts, tol=8.0):
    """斜线：沿线段采样，返回垂直方向墨迹中心的平均偏移（相对给定线段）"""
    p0 = np.array(p0, float) * S; p1 = np.array(p1, float) * S
    d = (p1 - p0) / np.linalg.norm(p1 - p0); n = np.array([-d[1], d[0]])
    offs = []
    for t in ts:
        c = p0 + (p1 - p0) * t
        best = []
        for u in np.arange(-tol * S, tol * S, 0.25):
            P = c + n * u
            X, Y = int(round(P[0])), int(round(P[1]))
            if 0 <= Y < H and 0 <= X < W and img[Y, X]:
                best.append(u)
        if best and (max(best) - min(best)) < 6 * S:
            offs.append((min(best) + max(best)) / 2 / S)
    return float(np.median(offs)) if offs else float("nan")

def cmp_h(label, x0, x1, yc, band=6):
    a = hline(src, x0, x1, yc, band); b = hline(red, x0, x1, yc, band)
    if not a or not b:
        print(f"{label:<16} 测量失败 源{a} 绘{b}"); return
    print(f"{label:<16} 源y={a[0]:7.2f}(t{a[1]:.2f})  绘y={b[0]:7.2f}(t{b[1]:.2f})  Δy={b[0]-a[0]:+6.2f}px = {(b[0]-a[0])*0.06108:+.3f}mm  n={a[2]}/{b[2]}")

def cmp_v(label, y0, y1, xc, band=6):
    a = vline(src, y0, y1, xc, band); b = vline(red, y0, y1, xc, band)
    if not a or not b:
        print(f"{label:<16} 测量失败 源{a} 绘{b}"); return
    print(f"{label:<16} 源x={a[0]:7.2f}(t{a[1]:.2f})  绘x={b[0]:7.2f}(t{b[1]:.2f})  Δx={b[0]-a[0]:+6.2f}px = {(b[0]-a[0])*0.06108:+.3f}mm  n={a[2]}/{b[2]}")

print("== 平面四边 ==")
cmp_h("①顶边", 200, 400, 142.5); cmp_h("①底边", 60, 240, 292.5)
cmp_h("②顶边", 680, 880, 140.5); cmp_h("②底边", 540, 730, 290.5)
cmp_h("③顶边", 1160, 1380, 141.0); cmp_h("③底边", 1040, 1220, 291.0)
cmp_v("①左边", 200, 270, 80.5); cmp_v("①右边", 200, 270, 348.5)
cmp_v("②左边", 200, 270, 567.5); cmp_v("②右边", 200, 270, 834.0)
cmp_v("③左边", 200, 270, 1053.0); cmp_v("③右边", 200, 270, 1320.0)
print("== 水平线 ==")
cmp_h("①c/b基线", 130, 200, 241.2, 5)
cmp_h("②l线", 600, 680, 239.0, 5)
cmp_h("③A'B'", 1130, 1230, 188.7, 5)
print("== 斜线（垂直偏移，正=偏左下法向） ==")
segs = [("①自由a", (66.8, 142.6), (215.4, 61.6)),
        ("①面内a", (206.0, 241.2), (269.4, 162.3)),
        ("①链A", (66.8, 142.6), (123.0, 241.2)),
        ("①链C", (123.0, 241.2), (220.0, 189.0)),
        ("②自由a", (552.9, 142.2), (699.7, 56.3)),
        ("②面内a", (694.0, 239.0), (755.1, 160.3)),
        ("③自由a", (1113.7, 121.8), (1265.6, 39.6)),
        ("③中斜", (1117.0, 189.5), (1240.0, 118.0))]
for label, p0, p1 in segs:
    ts = np.linspace(0.25, 0.7, 12)
    a = seg_off(src, p0, p1, ts); b = seg_off(red, p0, p1, ts)
    print(f"{label:<16} 源off={a:+6.2f}px  绘off={b:+6.2f}px  Δ={b-a:+6.2f}px = {(b-a)*0.06108:+.3f}mm")
print("== 竖直虚线 ==")
cmp_v("③A-A'线", 145, 185, 1122.8, 8)
cmp_v("③B-B'线", 95, 180, 1263.0, 8)
print("== 圈号 ==")
for label, cx, cy in [("①", 156.5, 341.5), ("②", 651.5, 342.0), ("③", 1142.0, 342.0)]:
    out = []
    for img in (src, red):
        win = img[int((cy - 26) * S):int((cy + 26) * S), int((cx - 26) * S):int((cx + 26) * S)]
        ys, xs = np.nonzero(win)
        out.append(((xs.mean() + int((cx - 26) * S)) / S, (ys.mean() + int((cy - 26) * S)) / S,
                    (xs.max() - xs.min()) / S, (ys.max() - ys.min()) / S))
    print(f"  圈{label} 源c=({out[0][0]:.1f},{out[0][1]:.1f}) 径({out[0][2]:.1f},{out[0][3]:.1f}) | 绘c=({out[1][0]:.1f},{out[1][1]:.1f}) 径({out[1][2]:.1f},{out[1][3]:.1f})")
