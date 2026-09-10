"""精测 v2：用 run 定位（先找连通 run，再在 run 内算质心），避免窗口混入他线。输出 geom.json"""
from PIL import Image
import numpy as np, json

P = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png"
im = Image.open(P).convert("L")
a = np.array(im).astype(float); ink = 1.0 - a/255.0
EPS = 0.55

def runs_along(vals, idx0):
    out=[]; s=None
    for i,v in enumerate(vals):
        if v>EPS and s is None: s=i
        elif v<=EPS and s is not None: out.append((idx0+s, idx0+i-1)); s=None
    if s is not None: out.append((idx0+s, idx0+len(vals)-1))
    return out

def col_run_centroid(x, y0, y1, yexp, win=14):
    """在列 x 上，取包含 yexp 的那个 run，返回 (y质心, run厚度, run端点)"""
    v = ink[y0:y1, x]; rs = runs_along(v, y0)
    if not rs: return None
    r = min(rs, key=lambda r: 0 if r[0]<=yexp<=r[1] else min(abs(r[0]-yexp),abs(r[1]-yexp)))
    lo,hi = r
    w = ink[lo:hi+1, x]; ys = np.arange(lo,hi+1)
    return (float((w*ys).sum()/w.sum()), float(w.sum()), lo, hi)

def row_run_centroid(y, x0, x1, xexp):
    v = ink[y, x0:x1]; rs = runs_along(v, x0)
    if not rs: return None
    r = min(rs, key=lambda r: 0 if r[0]<=xexp<=r[1] else min(abs(r[0]-xexp),abs(r[1]-xexp)))
    lo,hi = r
    w = ink[y, lo:hi+1]; xs = np.arange(lo,hi+1)
    return (float((w*xs).sum()/w.sum()), float(w.sum()), lo, hi)

def fit(xs_, cs_):
    A = np.vstack([np.array(xs_,float), np.ones(len(xs_))]).T
    m,k = np.linalg.lstsq(A, np.array(cs_,float), rcond=None)[0]
    return float(m), float(k)

lines = {}
# 竖直 3 条
lines["AA1"] = dict(kind="v", x=108.6)
lines["BB1"] = dict(kind="v", x=527.4)
lines["CC1"] = dict(kind="v", x=682.9)
for nm, X, ys in [("AA1",108.6,[300,420,540,640]), ("BB1",527.4,[300,420,540,640]), ("CC1",682.9,[150,250,350,450])]:
    cs=[row_run_centroid(y, int(X)-12, int(X)+13, X) for y in ys]
    print(nm, "centroids", [round(c[0],2) for c in cs], "mass", [round(c[1],2) for c in cs])
    lines[nm]["vals"]=[c[0] for c in cs]; lines[nm]["ys"]=ys
# 水平 3 条
for nm, Y, xs in [("AB",671.9,[150,250,350,450]), ("A1B1",253.5,[150,250,350,450]), ("D1C1",96.5,[300,400,500,620])]:
    cs=[col_run_centroid(x, int(Y)-12, int(Y)+13, Y) for x in xs]
    print(nm, "centroids", [round(c[0],2) for c in cs], "mass", [round(c[1],2) for c in cs])
    lines[nm]=dict(kind="h", vals=[c[0] for c in cs], xs=xs)
# 斜 45° 三条：B-C, A1-D1, B1-C1
for nm, XS, guess in [("BC",[545,575,605,635,655], None), ("A1D1",[125,155,185,215,245], None), ("B1C1",[550,580,610,640,660], None)]:
    pts=[]
    # 先粗估：45° 直线 y≈a*x+b，从两端点插值
    for x in XS:
        best=None
        for y in range(80,690):
            pass
        pts.append(x)
    print(nm, "(见下)")
np.save("ink.npy", ink)
