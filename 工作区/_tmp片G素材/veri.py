# -*- coding: utf-8 -*-
"""终检：渲染 → 配准 → 把重绘重采样到源图坐标系(764²) → 同一套量测 → 逐要素对比 + 出对照/差分图。"""
import json, subprocess, os, sys, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import fitz
from scipy import ndimage
import elem

K = 42.0/764.0; DPI = 600.0; MMPP = 25.4/DPI; S = K/MMPP
SRCPNG = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png"
C = json.load(open("coords.json", encoding="utf-8"))

def compile_pdf():
    for f in ("image2_重绘.tex", "image2_重绘_预览壳.tex"):
        shutil.copy(f, os.path.join("build", f))
    subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "image2_重绘_预览壳.tex"],
                   cwd="build", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def render_gray():
    doc = fitz.open(os.path.join("build", "image2_重绘_预览壳.pdf"))
    pg = doc[0]
    pix = pg.get_pixmap(matrix=fitz.Matrix(DPI/72.0, DPI/72.0), alpha=False)
    g = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].mean(axis=2)
    return g, pg.rect

def runs(v, i0, eps=0.55):
    out = []; s = None
    for i, x in enumerate(v):
        if x > eps and s is None: s = i
        elif x <= eps and s is not None: out.append((i0+s, i0+i-1)); s = None
    if s is not None: out.append((i0+s, i0+len(v)-1))
    return out

def pick(rs, exp):
    return min(rs, key=lambda r: 0 if r[0] <= exp <= r[1] else min(abs(r[0]-exp), abs(r[1]-exp)))

def register(ik, page_mm):
    H, W = ik.shape
    ppm = W/page_mm[0]
    b = ik > 0.5
    lab, n = ndimage.label(b, np.ones((3, 3), int))
    sizes = ndimage.sum(b, lab, range(1, n+1)); big = int(np.argmax(sizes))+1
    net = (lab == big)
    nys, nxs = np.nonzero(net)
    nx0, nx1, ny0, ny1 = nxs.min(), nxs.max(), nys.min(), nys.max()
    hw = 0.308/2
    bx = dict(x0=C["A"][0]-hw, x1=C["C"][0]+hw, y1=C["D1"][1]+hw, y0=C["A"][1]-hw)
    gx = lambda X: nx0 + (X-bx["x0"])/(bx["x1"]-bx["x0"])*(nx1-nx0)
    gy = lambda Y: ny1 - (Y-bx["y0"])/(bx["y1"]-bx["y0"])*(ny1-ny0)
    def rcx(y, xe, half=40):
        x0 = max(0, int(xe)-half); x1 = min(W, int(xe)+half)
        rs = runs(net[y, x0:x1], x0)
        if not rs: return None
        lo, hi = pick(rs, xe); w = ik[y, lo:hi+1]; xs = np.arange(lo, hi+1)
        return float((w*xs).sum()/w.sum())
    def rcy(x, ye, half=40):
        y0 = max(0, int(ye)-half); y1 = min(H, int(ye)+half)
        rs = runs(net[y0:y1, x], y0)
        if not rs: return None
        lo, hi = pick(rs, ye); w = ik[lo:hi+1, x]; ys = np.arange(lo, hi+1)
        return float((w*ys).sum()/w.sum())
    XA, XC = C["A"][0], C["C"][0]; YA, YB = C["A"][1], C["A1"][1]
    rows = [int(round(v)) for v in np.linspace(gy(YA+4), gy(YB-4), 7)]
    pa = [rcx(y, gx(XA)) for y in rows]; pc = [rcx(y, gx(XC)) for y in rows]
    pa = [v for v in pa if v]; pc = [v for v in pc if v]
    xA_ras, xC_ras = float(np.mean(pa)), float(np.mean(pc))
    cols = [int(round(v)) for v in np.linspace(gx(XA+4), gx(XC-6), 7)]
    ra = [rcy(x, gy(YA)) for x in cols]; rb = [rcy(x, gy(YB)) for x in cols]
    ra = [v for v in ra if v]; rb = [v for v in rb if v]
    yA_ras, yB_ras = float(np.mean(ra)), float(np.mean(rb))
    kx = (XC-XA)/(xC_ras-xA_ras)*ppm; ky = (YB-YA)/(yB_ras-yA_ras)*ppm
    m1 = K*ppm; b1 = xA_ras - XA*ppm
    m2 = K*ppm; b2 = yA_ras - (42.0-YA)*ppm
    return dict(ppm=ppm, kx=kx, ky=ky, m1=m1, b1=b1, m2=m2, b2=b2,
                xA_ras=xA_ras, xC_ras=xC_ras, yA_ras=yA_ras, yB_ras=yB_ras)

def warp_source_to_frame(reg, W, H):
    src = Image.open(SRCPNG).convert("L")
    a_, b_, c_ = 1/reg["m1"], 0.0, -reg["b1"]/reg["m1"]
    d_, e_, f_ = 0.0, 1/reg["m2"], -reg["b2"]/reg["m2"]
    return src.transform((W, H), Image.AFFINE, (a_, b_, c_, d_, e_, f_), resample=Image.BILINEAR, fillcolor=255)

def resample_redraw_to_src(gray, reg):
    im = Image.fromarray(gray.astype(np.uint8))
    return im.transform((764, 764), Image.AFFINE,
                        (reg["m1"], 0.0, reg["b1"], 0.0, reg["m2"], reg["b2"]),
                        resample=Image.BILINEAR, fillcolor=255)

def bbox_of(a, thr=128):
    ys, xs = np.nonzero(a < thr); return int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())

TARGETS_LAB = {"A": [79.5, 721.0], "B": [523.5, 725.0], "C": [726.5, 512.5], "D": [216.0, 496.0],
               "E": [310.5, 147.0], "A1": [36.0, 222.0], "B1": [571.5, 278.0],
               "C1": [704.5, 50.5], "D1": [233.0, 38.5]}
SRC_LAB_BOX = {"A": (54, 63), "B": (56, 61), "C": (58, 64), "D": (67, 61), "E": (60, 61),
               "A1": (55, 63), "B1": (56, 61), "C1": (58, 64), "D1": (67, 62)}

def main():
    compile_pdf()
    gray, rect = render_gray()
    ik = 1.0-gray/255.0
    reg = register(ik, (rect.width*25.4/72.0, rect.height*25.4/72.0))
    print("配准：kx=%.5f ky=%.5f ppm=%.3f | 源 1px = %.4f 栅格 px" % (reg["kx"], reg["ky"], reg["ppm"], reg["m1"]))
    ren764 = resample_redraw_to_src(gray, reg)
    ren764.save("重绘_源坐标系764.png")
    src = np.array(Image.open(SRCPNG).convert("L"))
    rn = np.array(ren764)
    Ms = elem.measure(src); Mr = elem.measure(rn)
    json.dump(dict(src=Ms, redraw=Mr), open("elem_compare.json", "w"), default=str, indent=1)

    rows = []
    def add(name, a, b):
        d = float(b)-float(a)
        rows.append((name, float(a), float(b), d, d*K))
    for k in ("AA1", "BB1", "CC1", "AB", "A1B1", "D1C1"):
        add(k+" 位置", Ms[k]["pos"], Mr[k]["pos"])
    for k in ("BC", "A1D1", "B1C1", "A1C1"):
        add(k+" 斜率m", Ms[k]["m"], Mr[k]["m"])
    add("虚线竖 x", Ms["dash_vertical_x"], Mr["dash_vertical_x"])
    add("虚线横 y", Ms["dash_horizontal_y"], Mr["dash_horizontal_y"])
    add("AD 斜率m", Ms["AD"]["m"], Mr["AD"]["m"])
    add("AE 斜率m", Ms["AE"]["m"], Mr["AE"]["m"])
    add("线宽 竖棱", Ms["AA1"]["thick"], Mr["AA1"]["thick"])
    add("线宽 横棱", Ms["AB"]["thick"], Mr["AB"]["thick"])
    add("虚线 on", Ms["dash_on_px"], Mr["dash_on_px"])
    add("虚线 off", Ms["dash_off_px"], Mr["dash_off_px"])
    for k in ("A", "B", "A1", "B1", "C", "C1", "D", "D1", "E"):
        for i, ax in enumerate("xy"):
            add("顶点%s.%s" % (k, ax), Ms["V"][k][i], Mr["V"][k][i])
    add("E 参数 t", Ms["E_t"], Mr["E_t"])
    for i, ax in enumerate("xy"):
        add("圆心."+ax, Ms["dot"]["c"][i], Mr["dot"]["c"][i])
    add("圆点 r", Ms["dot"]["r"], Mr["dot"]["r"])
    print("\n%-14s %10s %10s %8s %8s" % ("要素", "源图", "重绘", "Δpx", "Δmm"))
    for name, a, b, d, dmm in rows:
        flag = "  <== 超0.1mm" if abs(dmm) > 0.1 else ""
        print("%-14s %10.3f %10.3f %8.3f %8.4f%s" % (name, a, b, d, dmm, flag))

    # ---- 原生 600dpi 下量重绘竖虚线 dash（折源 px），与源图同法对照 ----
    ppm = reg["ppm"]
    xc = int(round(264.53*K*ppm + reg["b1"]))
    prof = ik[:, xc-4:xc+5].sum(axis=1)
    rr = [q for q in runs(prof, 0, eps=4.0)]
    seg = [((a-reg["b2"])/(K*ppm), (b-reg["b2"])/(K*ppm)) for a, b in rr]
    seg = [t for t in seg if 40 < t[0] < 480 and (t[1]-t[0]) < 30]
    ons = [b-a for a, b in seg]; offs = [seg[i+1][0]-seg[i][1] for i in range(len(seg)-1)]
    print("\n重绘·原生 600dpi 竖虚线（折源px）：on 中位 %.1f / off 中位 %.1f；段数 %d"
          % (float(np.median(ons)), float(np.median(offs)), len(seg)))
    print("源图同法（原生）：on %.1f / off %.1f" % (Ms["dash_on_px"], Ms["dash_off_px"]))
    print("重绘 dash 起点（源px）:", [round(a, 1) for a, b in seg][:12])

    print("\n标签墨迹盒（源坐标系 px）：")
    lab, n = ndimage.label(rn < 128, np.ones((3, 3), int))
    sizes = ndimage.sum(rn < 128, lab, range(1, n+1)); big = int(np.argmax(sizes))+1
    comps = []
    for i in range(1, n+1):
        if i == big: continue
        ys, xs = np.nonzero(lab == i)
        if len(xs) < 250: continue
        comps.append((int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()), len(xs)))
    labrows = []
    for nm, (tx, ty) in TARGETS_LAB.items():
        cand = [c for c in comps if abs((c[0]+c[1])/2-tx) < 60 and abs((c[2]+c[3])/2-ty) < 60]
        if not cand:
            labrows.append((nm, None)); print("  %-3s 未找到" % nm); continue
        g = max(cand, key=lambda c: c[4])
        cx, cy = (g[0]+g[1])/2, (g[2]+g[3])/2
        w, h = g[1]-g[0]+1, g[3]-g[2]+1
        sw, sh = SRC_LAB_BOX[nm]
        print("  %-3s 中心 重绘=(%.1f,%.1f) 源=(%.1f,%.1f) Δ=(%+.1f,%+.1f) | 盒 重绘=%dx%d 源=%dx%d"
              % (nm, cx, cy, tx, ty, cx-tx, cy-ty, w, h, sw, sh))
        labrows.append(dict(name=nm, c=(cx, cy), tgt=(tx, ty), wh=(w, h), src_wh=(sw, sh)))
    json.dump(labrows, open("label_check.json", "w"), default=str, indent=1)

    # ---------- 对照裁片（600dpi）----------
    W, H = gray.shape
    src_in_frame = np.array(warp_source_to_frame(reg, W, H))
    b1_ = bbox_of(src_in_frame); b2_ = bbox_of(gray)
    x0 = max(0, min(b1_[0], b2_[0])-20); x1 = min(W-1, max(b1_[1], b2_[1])+20)
    y0 = max(0, min(b1_[2], b2_[2])-20); y1 = min(H-1, max(b1_[3], b2_[3])+20)
    top = Image.fromarray(src_in_frame[y0:y1+1, x0:x1+1])
    bot = Image.fromarray(gray[y0:y1+1, x0:x1+1])
    gap = 30; pad = 16
    Wc = top.width+2*pad; Hc = top.height+bot.height+gap+2*pad
    comp = Image.new("RGB", (Wc, Hc), (255, 255, 255))
    comp.paste(top.convert("RGB"), (pad, pad))
    comp.paste(bot.convert("RGB"), (pad, pad+top.height+gap))
    d = ImageDraw.Draw(comp)
    d.line([(0, pad+top.height+gap//2), (Wc, pad+top.height+gap//2)], fill=(140, 140, 140), width=1)
    try:
        fnt = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
    except Exception:
        fnt = ImageFont.load_default()
    d.text((pad+2, 1), "上＝源图 image2.png（按源排印宽 42.0mm 缩放）", font=fnt, fill=(0, 0, 0))
    d.text((pad+2, pad+top.height+gap//2+6), "下＝TikZ 重绘（同尺同宽）", font=fnt, fill=(0, 0, 0))
    comp.save("对照_源图vs重绘_600dpi.png")
    print("\n→ 对照_源图vs重绘_600dpi.png  %dx%d px（1px=%.4fmm，等效 %.0f dpi）"
          % (comp.size[0], comp.size[1], MMPP, 25.4/MMPP))
    ov = np.full((top.height, top.width, 3), 255, np.uint8)
    ms = np.array(top) < 128; mr = np.array(bot) < 128
    ov[ms] = [255, 120, 120]; ov[mr] = [120, 180, 255]; ov[ms & mr] = [20, 20, 20]
    Image.fromarray(ov).save("叠加差分_源红_重绘青_600dpi.png")
    print("→ 叠加差分_源红_重绘青_600dpi.png（黑=重合，红=仅源，蓝=仅重绘）")
    print("→ 重绘_源坐标系764.png / elem_compare.json / label_check.json")

main()
