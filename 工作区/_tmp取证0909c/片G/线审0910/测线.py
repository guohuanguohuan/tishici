# -*- coding: utf-8 -*-
# 线审0910：六张片G图逐线量测源位图（实/虚、on/off 节距、线宽、灰度）
# 判定口径：沿线 0.25px 步进采样，垂向 ±halfw 窗取墨覆盖；内点空档≥3px ⇒ 虚线；
# on/off 取内部 run 中位数；线宽＝垂向 α 积分/核心墨高（面积÷高）。
import numpy as np, json, os
from PIL import Image

ROOT = r"C:/提示词/工作区/字替对照-0909/variantF/media/media"
OUT  = r"C:/提示词/工作区/_tmp取证0909c/片G/线审0910"

def load_ink(name):
    im = Image.open(os.path.join(ROOT, name)).convert("RGBA")
    a = np.asarray(im).astype(np.float32)
    gray = a[..., 0:3].mean(axis=2)
    alpha = a[..., 3] / 255.0
    ink = (255.0 - gray) / 255.0 * alpha          # 0..1 墨覆盖（合成到白底口径）
    return ink, gray

def line_profile(ink, p0, p1, halfw, step=0.25):
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    d = p1 - p0; L = float(np.hypot(*d)); u = d / L
    n = np.array([-u[1], u[0]])
    ts = np.arange(0.0, L, step)
    offs = np.arange(-halfw, halfw + 1e-9, 0.5)
    H, W = ink.shape
    prof = np.zeros(len(ts)); corev = np.zeros(len(ts))
    OX = offs * n[0]; OY = offs * n[1]
    for i, t in enumerate(ts):
        cx = p0[0] + u[0] * t + OX; cy = p0[1] + u[1] * t + OY
        x0 = np.floor(cx).astype(int); y0 = np.floor(cy).astype(int)
        fx = cx - x0; fy = cy - y0
        ok = (x0 >= 0) & (y0 >= 0) & (x0 < W - 1) & (y0 < H - 1)
        v = np.zeros(len(offs))
        if ok.any():
            xi = x0[ok]; yi = y0[ok]; fxi = fx[ok]; fyi = fy[ok]
            v[ok] = (ink[yi, xi] * (1 - fxi) * (1 - fyi) + ink[yi, xi + 1] * fxi * (1 - fyi)
                     + ink[yi + 1, xi] * (1 - fxi) * fyi + ink[yi + 1, xi + 1] * fxi * fyi)
        prof[i] = v.sum() * 0.5
        corev[i] = v.max()
    return ts, prof, corev, L

def runs_of(mask, step):
    """run-length 编码 True/False 交替段，返回 [(val,len,start_px)]"""
    out = []
    if len(mask) == 0: return out
    cur = mask[0]; start = 0
    for i in range(1, len(mask)):
        if mask[i] != cur:
            out.append((bool(cur), (i - start) * step, start * step))
            cur = mask[i]; start = i
    out.append((bool(cur), (len(mask) - start) * step, start * step))
    return out

def measure(ink, p0, p1, halfw, gray=None, trim=5.0):
    ts, prof, corev, L = line_profile(ink, p0, p1, halfw)
    core_ref = np.percentile(corev, 98) if corev.max() > 0 else 1.0
    onmask = prof > 0.10 * max(core_ref, 1e-6)      # 有墨判定：垂向积分 > 10% 核心高
    rr = runs_of(onmask, 0.25)
    trim_i = int(trim / 0.25)
    inner = rr
    if len(rr) >= 3:
        inner = rr[1:-1]
    elif len(rr) == 2:
        inner = []
    onr = [r[1] for r in inner if r[0] and r[1] >= 1.0]
    offr = [r[1] for r in inner if (not r[0]) and r[2] >= trim and (r[2] + r[1]) <= L - trim]
    # 全长（含端部）空档（判定用，端头 ±3px 内的空档忽略——cap/点造成）
    gaps_all = [r for r in rr if (not r[0]) and r[1] >= 3.0 and r[2] >= 3.0 and (r[2] + r[1]) <= L - 3.0]
    inked_frac = onmask[int(trim / 0.25):len(onmask) - int(trim / 0.25)].mean() if len(onmask) > 2 * trim / 0.25 else onmask.mean()
    # 线宽：取内部实段中点处的垂向 α 积分/核心高
    ws = []
    for r in rr:
        if r[0] and r[1] >= 6.0:
            i0 = int((r[2] + r[1] * 0.5) / 0.25)
            if 0 <= i0 < len(prof) and corev[i0] > 0.2:
                ws.append(prof[i0] / corev[i0])
    width = float(np.median(ws)) if ws else None
    gcore = None
    if gray is not None:
        p0 = np.array(p0, float); p1 = np.array(p1, float)
        d = p1 - p0; u = d / L; n = np.array([-u[1], u[0]])
        vals = []
        for t in np.arange(L * 0.3, L * 0.7, 2.0):
            c = p0 + u * t
            for o in np.arange(-halfw, halfw + 1e-9, 0.5):
                q = c + n * o
                x, y = int(round(q[0])), int(round(q[1]))
                if 0 <= x < gray.shape[1] and 0 <= y < gray.shape[0]:
                    vals.append(gray[y, x])
        gcore = float(np.min(vals)) if vals else None
    dashed = len(gaps_all) >= 1
    return dict(L=round(L, 1), dashed=bool(dashed), ngaps=len(gaps_all),
                gaps=[round(g[1], 1) for g in gaps_all][:12],
                on=round(float(np.median(onr)), 1) if onr else None,
                off=round(float(np.median(offr)), 1) if offr else None,
                inkfrac=round(float(inked_frac), 3),
                width=round(width, 2) if width else None,
                graycore=gcore)

FIGS = {}
def fig(name, pxmm, img, halfw, lines):
    FIGS[name] = dict(img=img, pxmm=pxmm, halfw=halfw, lines=lines)

# ---------------- g1 ----------------
s1 = 691 / 41.100
P1 = dict(A1=(88.008, 105.125), C1=(600.498, 105.117), B1=(419.239, 292.585),
          A=(87.997, 873.843), C=(600.495, 873.999), B=(419.225, 1061.522))
L1 = [("A1-C1", "A1", "C1", "solid", 2.214, 1.480),
      ("C1-B1", "C1", "B1", "solid", None, None),
      ("B1-A1", "B1", "A1", "solid", None, None),
      ("A1-A", "A1", "A", "solid", None, None),
      ("B1-B", "B1", "B", "solid", None, None),
      ("C1-C", "C1", "C", "solid", None, None),
      ("A-B", "A", "B", "solid", None, None),
      ("B-C", "B", "C", "solid", None, None),
      ("A-C", "A", "C", "dash", 2.214, 1.480),
      ("A1-B", "A1", "B", "solid", None, None),
      ("A1-C", "A1", "C", "dash", 2.214, 1.480)]
fig("g1-prism", s1, "image1.png", 6.5, L1)

# ---------------- g2 ----------------
s2 = 764 / 42.0
M2 = dict(A=(5.971, 5.058), B=(28.993, 5.058), A1=(5.971, 28.092), B1=(28.993, 28.092),
          C=(37.547, 13.696), C1=(37.547, 36.723), D=(14.543, 13.713), D1=(14.543, 36.723),
          E=(15.917, 30.809))
P2 = {k: (v[0] * s2, 764 - v[1] * s2) for k, v in M2.items()}
L2 = [("A-D", "A", "D", "dash", 1.209, 0.852),
      ("D-C", "D", "C", "dash", 1.209, 0.852),
      ("D-D1", "D", "D1", "dash", 1.209, 0.852),
      ("A-E", "A", "E", "dash", 1.209, 0.852),
      ("A-B", "A", "B", "solid", None, None),
      ("B-C", "B", "C", "solid", None, None),
      ("C-C1", "C", "C1", "solid", None, None),
      ("C1-B1", "C1", "B1", "solid", None, None),
      ("B1-A1", "B1", "A1", "solid", None, None),
      ("A1-A", "A1", "A", "solid", None, None),
      ("B-B1", "B", "B1", "solid", None, None),
      ("A1-D1", "A1", "D1", "solid", None, None),
      ("D1-C1", "D1", "C1", "solid", None, None),
      ("A1-C1", "A1", "C1", "solid", None, None)]
fig("g2-cubeE", s2, "image2.png", 5.5, L2)

# ---------------- g3 ----------------
s3 = 521 / 86.0
L3 = [("灰AB", (55, 453), (358, 453), "solid", None, None),
      ("灰BC", (356, 454), (462, 349), "solid", None, None),
      ("灰CC1", (462, 45), (462, 349), "solid", None, None),
      ("灰C1D1", (160, 47), (464, 47), "solid", None, None),
      ("灰D1A1", (165, 45), (57, 153), "solid", None, None),
      ("灰A1A", (56, 151), (56, 454), "solid", None, None),
      ("灰A1B1", (56, 153), (358, 153), "solid", None, None),
      ("灰B1B", (356, 151), (356, 455), "solid", None, None),
      ("灰B1C1", (356, 150), (462, 46), "solid", None, None),
      ("灰虚AD", (56, 453), (161.5, 348.5), "dash", 1.82, 1.40),
      ("灰虚DC", (160, 347), (462, 347), "dash", 1.82, 1.40),
      ("灰虚DD1", (162, 46), (162, 349), "dash", 1.82, 1.40),
      ("黑BC1", (356.5, 453.5), (462.5, 46.5), "solid", None, None),
      ("黑虚AC", (56, 453), (462, 349), "dash", 1.82, 1.40),
      ("黑虚AD1", (56, 453), (162.5, 47), "dash", 1.82, 1.40),
      ("黑虚D1C", (162.5, 47), (462, 349), "dash", 1.82, 1.40)]
fig("g3-cube6", s3, "image3.png", 4.0, L3)

# ---------------- g4 ----------------
L4 = [("E-A", (66.80, 205.50), (319.68, 74.50), "solid", None, None),
      ("A-B", (319.68, 74.50), (692.00, 74.50), "solid", None, None),
      ("E-F", (66.80, 205.50), (434.40, 205.50), "solid", None, None),
      ("F-B", (434.40, 205.50), (692.00, 74.50), "solid", None, None),
      ("E-D", (66.80, 205.50), (300.40, 347.375), "solid", None, None),
      ("F-C", (434.40, 205.50), (667.32, 347.375), "solid", None, None),
      ("D-C", (300.40, 347.375), (667.32, 347.375), "solid", None, None),
      ("B-D", (692.00, 74.50), (300.40, 347.375), "solid", None, None)]
fig("g4-dihedral", 788 / 66.3, "image4.png", 4.5, L4)

# ---------------- g5 ----------------
s5 = 1798 / 54.7
M5 = dict(A=(3.9650, 18.6187), B=(19.7139, 35.7637), C=(50.4429, 18.6187),
          D=(37.9027, 6.2360), M=(19.7139, 18.6187), N=(37.9027, 18.6187))
P5 = {k: (v[0] * s5, 1350 - v[1] * s5) for k, v in M5.items()}
L5 = [("A-B", "A", "B", "solid", None, None),
      ("B-C", "B", "C", "solid", None, None),
      ("C-D", "C", "D", "solid", None, None),
      ("D-A", "D", "A", "solid", None, None),
      ("B-D", "B", "D", "solid", None, None),
      ("A-C", "A", "C", "dash", 1.2169, 0.6085),
      ("B-M", "B", "M", "dash", 1.2169, 0.6085),
      ("D-N", "D", "N", "dash", 1.2169, 0.6085),
      ("M-D", "M", "D", "dash", 1.2169, 0.6085)]
fig("g5-fold", s5, "image5.png", 8.0, L5)

# ---------------- g6 ----------------
s6 = 1408 / 86.0
def G6(x, y): return (x * s6, 374 - y * s6)
L6 = [("①面-下", (1.3706, 4.9780), (17.1114, 4.9780), "solid", None, None),
      ("①面-右", (17.1114, 4.9780), (25.8544, 14.1393), "solid", None, None),
      ("①面-上", (25.8544, 14.1393), (10.1245, 14.1381), "solid", None, None),
      ("①面-左", (10.1245, 14.1381), (1.3706, 4.9780), "solid", None, None),
      ("①c杆", (7.5128, 8.1114), (12.5824, 8.1114), "solid", None, None),
      ("①b杆", (12.5824, 8.1114), (17.7436, 8.1114), "solid", None, None),
      ("①面内a", (12.5824, 8.1114), (16.4548, 12.9305), "solid", None, None),
      ("①自由a", (4.0923, 14.2621), (13.1187, 19.1539), "solid", None, None),
      ("①链A", (4.0923, 14.2621), (7.5128, 8.1114), "dash", 0.880, 0.550),
      ("①链B", (13.1187, 19.1539), (16.4548, 12.9305), "dash", 0.880, 0.550),
      ("①链C", (7.5128, 8.1114), (16.4548, 12.9305), "dash", 0.880, 0.550),
      ("②面-下", (31.0565, 5.1001), (46.7900, 5.1001), "solid", None, None),
      ("②面-右", (46.7900, 5.1001), (55.5488, 14.2615), "solid", None, None),
      ("②面-上", (55.5488, 14.2615), (39.8037, 14.2578), "solid", None, None),
      ("②面-左", (39.8037, 14.2578), (31.0565, 5.1001), "solid", None, None),
      ("②直线l", (35.7193, 8.2457), (47.4893, 8.2457), "solid", None, None),
      ("②c杆", (37.2891, 8.2457), (42.3892, 8.2457), "solid", None, None),
      ("②面内a", (42.3892, 8.2457), (46.1212, 13.0527), "solid", None, None),
      ("②自由a", (33.8075, 14.4148), (42.8192, 19.2553), "solid", None, None),
      ("②链A'", (33.8075, 14.4148), (37.2891, 8.2457), "dash", 0.880, 0.550),
      ("②链B'", (42.8192, 19.2553), (46.1212, 13.0527), "dash", 0.880, 0.550),
      ("②链C'", (37.2891, 8.2457), (46.1212, 13.0527), "dash", 0.880, 0.550),
      ("③A-A'", (68.2747, 15.6364), (68.2747, 11.2692), "dash", 1.100, 0.812),
      ("③B-B'", (77.1435, 20.4250), (77.1435, 11.2997), "dash", 1.100, 0.812),
      ("③中斜a'", (68.2564, 11.2997), (77.3934, 16.2166), "dash", 0.880, 0.550),
      ("③A'B'", (68.1342, 11.3180), (77.0335, 11.3180), "solid", None, None),
      ("③自由a", (68.2869, 15.5447), (77.3023, 20.4250), "solid", None, None)]
fig("g6-triple", s6, "sub3_B_4.png", 4.0, L6)

# ---------------- 执行 ----------------
report = {}
for fname, spec in FIGS.items():
    ink, gray = load_ink(spec["img"])
    res = {}
    for item in spec["lines"]:
        nm, a, b, kind, on_mm, off_mm = item
        if isinstance(a, str):
            p0 = spec_px = None
            P = P1 if fname.startswith("g1") else (P2 if fname.startswith("g2") else P5)
            p0, p1 = P[a], P[b]
        else:
            if fname.startswith("g6"):
                p0, p1 = G6(*a), G6(*b)
            else:
                p0, p1 = a, b
        m = measure(ink, p0, p1, spec["halfw"], gray=gray)
        m["declared"] = kind
        if on_mm:
            m["exp_on_px"] = round(on_mm * spec["pxmm"], 1)
            m["exp_off_px"] = round(off_mm * spec["pxmm"], 1)
        res[nm] = m
    report[fname] = dict(img=spec["img"], pxmm=round(spec["pxmm"], 4), lines=res)

with open(os.path.join(OUT, "线审-源位图量测.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)

for fname, r in report.items():
    print("=" * 20, fname, r["img"], "px/mm=%.3f" % r["pxmm"])
    for nm, m in r["lines"].items():
        exp = ""
        if "exp_on_px" in m:
            exp = " 期望on/off=%s/%s" % (m["exp_on_px"], m["exp_off_px"])
        print("%-8s 声明=%-5s 实测=%-5s gaps=%d on=%s off=%s 宽=%s 灰=%s%s" % (
            nm, m["declared"], "虚" if m["dashed"] else "实", m["ngaps"],
            m["on"], m["off"], m["width"],
            ("%.0f" % m["graycore"]) if m["graycore"] is not None else "-", exp))
