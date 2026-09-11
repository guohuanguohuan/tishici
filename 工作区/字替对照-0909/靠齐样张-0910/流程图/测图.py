# TS-01 参数标定 v3：剖面投影法（框与箭头被箭头链连成一体，改用行列投影切分）
import numpy as np
from PIL import Image
from scipy import ndimage

P = r"C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/p15.png"
PXMM = 14.176
img = np.array(Image.open(P).convert("L"))
dark = img < 128

def mm(v):
    return round(v / PXMM, 2)

def pt(v):
    return round(v / PXMM * 72 / 25.4, 2)

def runs(m, off=0):
    idx = np.flatnonzero(m)
    if idx.size == 0:
        return []
    sp = np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)
    return [(int(s[0]) + off, int(s[-1]) + off) for s in sp]

FL_Y0, FL_Y1 = 3145, 3862
FL_X0, FL_X1 = 1555, 2715
DZ = (1555, 1836)   # 菱形区（含竖箭头）
RZ = (1836, 2715)   # 矩形区

fl = dark[FL_Y0:FL_Y1, FL_X0:FL_X1]

# ---- 矩形左右缘：列投影 ----
colcnt = fl[:, RZ[0] - FL_X0:RZ[1] - FL_X0].sum(axis=0)
cols = np.flatnonzero(colcnt > 250) + RZ[0]
rr = runs(cols >= 0, cols[0]) if cols.size else []
groups = runs(np.isin(np.arange(RZ[0], RZ[1]), cols), RZ[0])
edge_cols = [g for g in groups if g[1] - g[0] <= 6]
XL, XR = edge_cols[0][0], edge_cols[-1][1]
print(f"矩形左缘 x={XL} 右缘 x={XR} | 矩形宽 {XR-XL+1}px/{mm(XR-XL+1)}mm")

# ---- 矩形上下缘：行投影 ----
rowcnt = dark[FL_Y0:FL_Y1, XL:XR + 1].sum(axis=1)
rows = np.flatnonzero(rowcnt > 550) + FL_Y0
eg = runs(np.isin(np.arange(FL_Y0, FL_Y1), rows), FL_Y0)
assert len(eg) % 2 == 0, f"边带数{len(eg)}"
rects = [(eg[i][0], eg[i + 1][1]) for i in range(0, len(eg), 2)]
print("== 矩形 ==")
for i, (yt, yb) in enumerate(rects, 1):
    top_xs = np.flatnonzero(dark[yt, XL:XR + 1])
    xa = top_xs[0] + XL
    yl = np.flatnonzero(dark[yt:yb + 1, XL])[0] + yt
    r_x, r_y = xa - XL, yl - yt
    xc = (XL + XR) // 2
    th_h = runs(dark[yt - 2:yt + 9, xc])[0]
    th_v = runs(dark[(yt + yb) // 2, XL - 2:XL + 9])[0]
    print(f"矩{i}: y{yt}..{yb} 高{yb-yt+1}px/{mm(yb-yt+1)}mm 圆角x{r_x}px/y{r_y}px/"
          f"{mm(r_x)}mm 框线厚横{th_h[1]-th_h[0]+1}px 纵{th_v[1]-th_v[0]+1}px/{pt(th_v[1]-th_v[0]+1)}pt")

# ---- 菱形：行宽轮廓找尖 ----
dz = dark[FL_Y0:FL_Y1, DZ[0]:DZ[1]]
w = np.zeros(FL_Y1 - FL_Y0, dtype=int)
for j in range(len(w)):
    xs = np.flatnonzero(dz[j])
    if xs.size:
        w[j] = xs[-1] - xs[0] + 1
tips = []
for j in range(4, len(w) - 4):
    if 0 < w[j] <= 5 and max(w[j - 4], w[j + 4]) >= 12:
        if not tips or j - tips[-1][-1] > 6:
            tips.append([j + FL_Y0])
        else:
            tips[-1].append(j + FL_Y0)
tipys = [int(np.mean(t)) for t in tips]
print(f"\n== 菱形 == 尖头行: {tipys}")
assert len(tipys) % 2 == 0
dias = [(tipys[i], tipys[i + 1]) for i in range(0, len(tipys), 2)]
dinfo = []
for i, (yt, yb) in enumerate(dias, 1):
    ym = (yt + yb) // 2
    rr = runs(dark[ym, DZ[0]:DZ[1]], DZ[0])
    xl, xr = rr[0][0], rr[-1][1]
    ycut = ym + 25
    rr2 = runs(dark[ycut, DZ[0]:DZ[1]], DZ[0])
    cuts = [b - a + 1 for a, b in rr2[:2]]
    Hd, Wd = yb - yt, xr - xl
    m = Hd / Wd
    tper = [round(c * m / np.sqrt(1 + m * m), 1) for c in cuts]
    print(f"菱{i}: y尖{yt}..{yb} x顶点{xl}..{xr} | W={Wd}px/{mm(Wd)}mm H={Hd}px/{mm(Hd)}mm "
          f"H/W={Hd/Wd:.2f} 斜边垂厚≈{tper}px")
    dinfo.append((yt, yb, xl, xr, ym))

# ---- 框内文字（连通域，域限流程图） ----
lab, n = ndimage.label(fl)
areas = np.bincount(lab.ravel())
objs = ndimage.find_objects(lab)
comps = []
for i, sl in enumerate(objs, 1):
    if sl is None or areas[i] < 40 or areas[i] > 30000:
        continue
    ys, xs = sl
    comps.append(dict(y0=ys.start + FL_Y0, y1=ys.stop - 1 + FL_Y0,
                      x0=xs.start + FL_X0, x1=xs.stop - 1 + FL_X0,
                      h=ys.stop - ys.start, w=xs.stop - xs.start, a=int(areas[i])))
print("\n== 文字 ==")
for i, (yt, yb, xl, xr, ym) in enumerate(dinfo, 1):
    inner = [c for c in comps if c['x0'] > xl + 12 and c['x1'] < xr - 12
             and c['y0'] > yt + 12 and c['y1'] < yb - 12]
    if not inner:
        continue
    ty0 = min(c['y0'] for c in inner)
    ty1 = max(c['y1'] for c in inner)
    tx0 = min(c['x0'] for c in inner)
    tx1 = max(c['x1'] for c in inner)
    print(f"菱{i}字: 墨x{tx0}..{tx1} y{ty0}..{ty1} 墨高{ty1-ty0+1}px/{mm(ty1-ty0+1)}mm "
          f"墨宽{tx1-tx0+1}px/{mm(tx1-tx0+1)}mm")
# 笔画宽：菱2 文字中带水平 run
yt, yb, xl, xr, ym = dinfo[1]
inner = [c for c in comps if c['x0'] > xl + 12 and c['x1'] < xr - 12
         and c['y0'] > yt + 12 and c['y1'] < yb - 12]
tcy = (min(c['y0'] for c in inner) + max(c['y1'] for c in inner)) // 2
for dy in (-8, 0, 8):
    rr3 = [b - a + 1 for a, b in runs(dark[tcy + dy, xl + 12:xr - 12]) if b - a + 1 < 14]
    print(f"菱2字笔画横截 y{tcy+dy}: {rr3}")

for i, (yt, yb) in enumerate(rects, 1):
    inner = [c for c in comps if c['x0'] > XL + 4 and c['x1'] < XR - 4
             and c['y0'] > yt + 4 and c['y1'] < yb - 4]
    ty0 = min(c['y0'] for c in inner)
    ty1 = max(c['y1'] for c in inner)
    tx0 = min(c['x0'] for c in inner)
    tx1 = max(c['x1'] for c in inner)
    hz = sorted(c['h'] for c in inner if 26 <= c['h'] <= 62)
    print(f"矩{i}字: 墨x{tx0}..{tx1} y{ty0}..{ty1} | 左衬{tx0-XL}px/{mm(tx0-XL)}mm "
          f"右衬{XR-tx1}px 上衬{ty0-yt}px 下衬{yb-ty1}px 汉字墨高中位"
          f"{hz[len(hz)//2] if hz else 0}px/{mm(hz[len(hz)//2]) if hz else 0}mm")

# ---- 箭头 ----
print("\n== 箭头 ==")
print("-- 竖箭头（菱间）--")
for i in range(len(dinfo) - 1):
    y_top = dinfo[i][1] + 1
    y_bot = dinfo[i + 1][0] - 1
    xc = (dinfo[i][2] + dinfo[i][3]) // 2
    seg = dark[y_top:y_bot + 1, xc - 12:xc + 13]
    ws = []
    for j in range(seg.shape[0]):
        r = np.flatnonzero(seg[j])
        ws.append(r[-1] - r[0] + 1 if r.size else 0)
    ws = np.array(ws)
    nz = np.flatnonzero(ws > 0)
    line = nz[ws[nz] <= 4]
    head = nz[ws[nz] > 4]
    print(f"隙{i+1}: y{y_top}..{y_bot} 总隙{y_bot-y_top+1}px/{mm(y_bot-y_top+1)}mm "
          f"墨起y{y_top+nz[0]} 墨止y{y_top+nz[-1]} 线厚{ws[line].min() if line.size else 0}px "
          f"头宽{ws[head].max() if head.size else 0}px 头长{head[-1]-head[0]+1 if head.size else 0}px")
print("-- 横箭头（菱→矩形）--")
for i, (yt, yb, xl, xr, ym) in enumerate(dinfo, 1):
    x0, x1 = xr + 2, XL - 1
    ext = []
    for x in range(x0, x1 + 1):
        r = np.flatnonzero(dark[ym - 14:ym + 15, x])
        ext.append(r[-1] - r[0] + 1 if r.size else 0)
    ext = np.array(ext)
    nz = np.flatnonzero(ext > 0)
    if not nz.size:
        print(f"行{i}: 无墨")
        continue
    head = nz[ext[nz] > 5]
    line = nz[ext[nz] <= 4]
    print(f"行{i}: x{x0+nz[0]}..{x0+nz[-1]} 总长{nz[-1]-nz[0]+1}px/{mm(nz[-1]-nz[0]+1)}mm "
          f"线厚{ext[line].min() if line.size else 0}px 头高{ext[head].max() if head.size else 0}px/"
          f"{mm(ext[head].max()) if head.size else 0}mm 头长{head[-1]-head[0]+1 if head.size else 0}px/"
          f"{mm(head[-1]-head[0]+1) if head.size else 0}mm 尖距矩缘{XL-(x0+nz[-1])}px")
    print(f"     箭y带 y{ym-14+int(np.argmax([dark[ym-14:ym+15, x0+nz[-1]].sum(),1]))}≈ym{ym} 矩心y{(rects[i-1][0]+rects[i-1][1])//2} 菱心y{ym}")

# ---- 版面 ----
print("\n== 版面 ==")
lead = [c for c in comps if c['y1'] < FL_Y0 - 2 and c['h'] > 10]
foot = [y for y in range(3900, 4130) if dark[y, 300:2700].sum() > 3]
body_xs = np.flatnonzero(dark[2700:3040, 1400:2900].any(axis=0))
colL, colR = body_xs[0] + 1400, body_xs[-1] + 1400
hzl = sorted(c['h'] for c in lead if 26 <= c['h'] <= 60)
ly0 = min(c['y0'] for c in lead)
ly1 = max(c['y1'] for c in lead)
lx0 = min(c['x0'] for c in lead)
lx1 = max(c['x1'] for c in lead)
print(f"引导行: y{ly0}..{ly1} 墨高{ly1-ly0+1}px/{mm(ly1-ly0+1)}mm x{lx0}..{lx1} "
      f"汉字墨高中位{hzl[len(hzl)//2] if hzl else 0}px/{mm(hzl[len(hzl)//2]) if hzl else 0}mm")
print(f"图顶距引导行底 {FL_Y0+ (dias[0][0]-FL_Y0) - ly1}px/{mm(dias[0][0]-ly1)}mm")
print(f"图底 y{dias[-1][1]} → 页脚顶 y{foot[0]}：{foot[0]-dias[-1][1]}px/{mm(foot[0]-dias[-1][1])}mm")
print(f"右栏 x{colL}..{colR} 宽{colR-colL+1}px/{mm(colR-colL+1)}mm | "
      f"图左距栏{dias[0][2]-colL}px 图右距栏{colR-XR}px")
print(f"菱心x={(dinfo[0][2]+dinfo[0][3])//2} 矩中x={(XL+XR)//2} 栏中x={(colL+colR)//2}")
print(f"流程图bbox: x{dinfo[0][2]}..{XR} y{dias[0][0]}..{dias[-1][1]} | "
      f"{XR-dinfo[0][2]+1}x{dias[-1][1]-dias[0][0]+1}px = "
      f"{mm(XR-dinfo[0][2]+1)}x{mm(dias[-1][1]-dias[0][0]+1)}mm")
for i in range(4):
    rc = (rects[i][0] + rects[i][1]) // 2
    print(f"行{i+1}: 矩顶-菱尖{rects[i][0]-dinfo[i][0]:+d}px 矩底-菱尖{rects[i][1]-dinfo[i][1]:+d}px "
          f"矩高{(rects[i][1]-rects[i][0])}px 菱高{(dinfo[i][1]-dinfo[i][0])}px")
