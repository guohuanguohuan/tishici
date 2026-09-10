# -*- coding: utf-8 -*-
"""原生 600dpi 复核（不经重采样）：把重绘栅格各要素直接折回源图像素，与源图实测值对照。
   因为片段外框已固定为 42×42mm 画布，栅格原点即源图 (0,0)，折算只需除 (ppm*K)。"""
import json
import numpy as np
import fitz

K = 42.0/764.0
C = json.load(open("coords.json", encoding="utf-8"))
doc = fitz.open("build/image2_重绘_预览壳.pdf")
pg = doc[0]
pix = pg.get_pixmap(matrix=fitz.Matrix(600/72.0, 600/72.0), alpha=False)
g = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].mean(axis=2)
ink = 1.0 - g/255.0
ppm = pix.width/(pg.rect.width*25.4/72.0)
SC = ppm*K                       # 每源像素占多少栅格像素
HALF = 0.5                       # 栅格像素中心→mm 的半步修正（源px = (栅格px+0.5)/SC）
H, W = ink.shape

def _runs(m):
    out = []; s = None
    for i, t in enumerate(m):
        if t and s is None: s = i
        elif not t and s is not None: out.append((s, i-1)); s = None
    if s is not None: out.append((s, len(m)-1))
    return out

def cen_row(y, xe, half=40):
    x0 = max(0, int(xe)-half); x1 = min(W, int(xe)+half)
    v = ink[y, x0:x1]; rs = _runs(v > 0.55)
    if not rs: return None
    lo, hi = min(rs, key=lambda r: 0 if x0+r[0] <= xe <= x0+r[1] else min(abs(x0+r[0]-xe), abs(x0+r[1]-xe)))
    w = v[lo:hi+1]; xs = np.arange(x0+lo, x0+hi+1)
    return float((w*xs).sum()/w.sum()) + HALF

def cen_col(x, ye, half=40):
    y0 = max(0, int(ye)-half); y1 = min(H, int(ye)+half)
    v = ink[y0:y1, x]; rs = _runs(v > 0.55)
    if not rs: return None
    lo, hi = min(rs, key=lambda r: 0 if y0+r[0] <= ye <= y0+r[1] else min(abs(y0+r[0]-ye), abs(y0+r[1]-ye)))
    w = v[lo:hi+1]; ys = np.arange(y0+lo, y0+hi+1)
    return float((w*ys).sum()/w.sum()) + HALF

rows = []
def chk(name, got, exp, note=""):
    rows.append((name, exp, got, got-exp))

# 竖棱（源图 x 实测）
for nm, X, ys, exp in [("A-A1 竖棱 x", (C["A"][0]+C["A1"][0])/2, [400, 500, 600], 108.609),
                       ("B-B1 竖棱 x", (C["B"][0]+C["B1"][0])/2, [400, 500, 600], 527.391),
                       ("C-C1 竖棱 x", (C["C"][0]+C["C1"][0])/2, [250, 350, 450], 683.000)]:
    vals = [cen_row(int(y*SC), X*ppm)/SC for y in ys]
    chk(nm, float(np.mean(vals)), exp)
# 横棱（源图 y 实测）
for nm, Y, xs, exp in [("A-B 横棱 y", (C["A"][1]+C["B"][1])/2, [250, 350, 450], 672.000),
                       ("A1-B1 横棱 y", (C["A1"][1]+C["B1"][1])/2, [250, 350, 450], 253.000),
                       ("D1-C1 横棱 y", (C["D1"][1]+C["C1"][1])/2, [350, 450, 550], 96.000)]:
    vals = [cen_col(int(x*SC), (42-Y)*ppm)/SC for x in xs]
    chk(nm, float(np.mean(vals)), exp)
# 线宽（源图同法：竖棱横向厚 5.75 / 横棱纵向厚 5.00）
def thick_x(y, xe, half=14):
    x0 = max(0, int(xe)-half); v = ink[y, x0:x0+2*half]
    rs = _runs(v > 0.55); lo, hi = min(rs, key=lambda r: -r[1]+r[0])
    return v[lo:hi+1].sum()/SC
def thick_y(x, ye, half=14):
    y0 = max(0, int(ye)-half); v = ink[y0:y0+2*half, x]
    rs = _runs(v > 0.55); lo, hi = min(rs, key=lambda r: -r[1]+r[0])
    return v[lo:hi+1].sum()/SC
chk("线宽 竖棱", float(np.mean([thick_x(int(y*SC), (C["A"][0])*ppm) for y in (400, 500, 600)])), 5.749)
chk("线宽 横棱", float(np.mean([thick_y(int(x*SC), (42-C["A"][1])*ppm) for x in (250, 350, 450)])), 5.000)
# 竖直虚线 dash on/off 与各段起点（源图实测）
prof = ink[:, int(C["D"][0]*ppm)-4:int(C["D"][0]*ppm)+5].sum(axis=1)
runs_ = []
s = None
for i, v in enumerate(prof):
    if v > 4.0 and s is None: s = i
    elif v <= 4.0 and s is not None: runs_.append((s, i-1)); s = None
seg = [((a+HALF)/SC, (b+HALF)/SC) for a, b in runs_]
seg = [t for t in seg if 40 < t[0] < 480 and (t[1]-t[0]) < 30]
ons = [b-a for a, b in seg]; offs = [seg[i+1][0]-seg[i][1] for i in range(len(seg)-1)]
chk("虚线 on", float(np.median(ons)), 22.0)
chk("虚线 off", float(np.median(offs)), 15.5)
src_starts = [126, 163, 201, 238, 313, 351, 388, 426, 463, 501]
gs = [a for a, b in seg]
got_starts = [round(a, 1) for a in gs if 120 < a < 510][:10]
print("dash 起点：源 %s" % src_starts)
print("dash 起点：绘 %s（最大偏差 %.1fpx）"
      % (got_starts, max(abs(a-b) for a, b in zip(got_starts, src_starts))))
print("\n%-14s %10s %10s %8s %8s" % ("要素(原生600dpi)", "源图", "重绘", "Δpx", "Δmm"))
mx = 0.0
for nm, exp, got, d in rows:
    mx = max(mx, abs(d))
    print("%-14s %10.3f %10.3f %8.3f %8.4f" % (nm, exp, got, d, d*K))
print("最大偏差 %.3f px = %.4f mm" % (mx, mx*K))
