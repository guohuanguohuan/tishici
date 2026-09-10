# -*- coding: utf-8 -*-
"""渲染 PDF（600dpi）→ 与源图同尺对齐 → 出对照裁片；并回头量测重绘标签/几何偏差（供标定）。
用法：python compare.py [--calib]"""
import sys, json, subprocess, os
import numpy as np
from PIL import Image
from scipy import ndimage
import fitz

PDF = os.path.join("build", "image2_重绘_预览壳.pdf")
SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png"
K = 42.0/764.0          # mm per source px
DPI = 600.0
MMPP = 25.4/DPI         # mm per render px
S = K/MMPP              # 1 source px = S render px  (=1.2986 @600dpi)

def load_src():
    im = Image.open(SRC).convert("L")
    a = np.array(im)
    return a

def render_pdf():
    doc = fitz.open(PDF)
    pg = doc[0]
    zoom = DPI/72.0
    pix = pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("L")
    return np.array(img), pg.rect

def bbox(a, thr=128, pad=0):
    b = a < thr
    ys, xs = np.nonzero(b)
    return xs.min()+pad, xs.max()-pad, ys.min()+pad, ys.max()-pad

def components(a, thr=128, min_area=60):
    b = a < thr
    lab, n = ndimage.label(b, structure=np.ones((3,3), int))
    out = []
    big = 0; bigi = 0
    for i in range(1, n+1):
        ys, xs = np.nonzero(lab == i)
        if len(xs) > big: big, bigi = len(xs), i
        out.append((i, xs, ys))
    res = []
    for i, xs, ys in out:
        if i == bigi:            # 主连通域＝线网（含圆点 E，若与线相连）
            res.append(dict(kind="net", i=i, area=len(xs),
                            x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()),
                            cx=float(xs.mean()), cy=float(ys.mean())))
            continue
        if len(xs) < min_area: continue
        res.append(dict(kind="blob", i=i, area=len(xs),
                        x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()),
                        cx=float(xs.mean()), cy=float(ys.mean())))
    return res

def group_labels(comps, gap=26):
    """把西文字母＋下标数字连成组"""
    blobs = [c for c in comps if c["kind"] == "blob"]
    used = [False]*len(blobs); groups = []
    for i, c in enumerate(blobs):
        if used[i]: continue
        gx0, gx1, gy0, gy1 = c["x0"], c["x1"], c["y0"], c["y1"]
        used[i] = True
        changed = True
        while changed:
            changed = False
            for j, d in enumerate(blobs):
                if used[j]: continue
                if not (d["x0"] > gx1+gap or d["x1"] < gx0-gap or d["y0"] > gy1+gap or d["y1"] < gy0-gap):
                    gx0, gx1 = min(gx0, d["x0"]), max(gx1, d["x1"])
                    gy0, gy1 = min(gy0, d["y0"]), max(gy1, d["y1"])
                    used[j] = True; changed = True
        groups.append(dict(x0=gx0, x1=gx1, y0=gy0, y1=gy1,
                           cx=(gx0+gx1)/2, cy=(gy0+gy1)/2, h=gy1-gy0+1, w=gx1-gx0+1, area=c["area"]))
    return groups

def main():
    src = load_src()
    ren, rect = render_pdf()
    sx0, sx1, sy0, sy1 = bbox(src)
    rx0, rx1, ry0, ry1 = bbox(ren)
    print("源图内容框 x[%d,%d] y[%d,%d]  %dx%d px" % (sx0,sx1,sy0,sy1, sx1-sx0+1, sy1-sy0+1))
    print("重绘内容框 x[%d,%d] y[%d,%d]  %dx%d px  (@%.0fdpi, 1px=%.5fmm)" % (rx0,rx1,ry0,ry1, rx1-rx0+1, ry1-ry0+1, DPI, MMPP))
    print("重绘内容宽 %.3f mm（源 %.3f mm）" % ((rx1-rx0+1)*MMPP, (sx1-sx0+1)*K))
    print("PDF 页面 %.3f×%.3f mm" % (rect.width*25.4/72, rect.height*25.4/72))

    # 同尺：源放大 S 倍
    W = int(round(src.shape[1]*S)); H = int(round(src.shape[0]*S))
    src_big = np.array(Image.fromarray(src).resize((W,H), Image.LANCZOS))
    sb = bbox(src_big)

    # 按内容框中心对齐
    scx, scy = (sb[0]+sb[1])/2, (sb[2]+sb[3])/2
    rcx, rcy = (rx0+rx1)/2, (ry0+ry1)/2
    dx, dy = rcx-scx, rcy-scy
    print("对齐位移（重绘 - 源）: dx=%.1f px dy=%.1f px (@600dpi)" % (dx,dy))

    # ---- 并排对照裁片（上=源，下=重绘，同尺、同宽、居中对齐）----
    pad = 24
    cw = max(src_big.shape[1], ren.shape[0] if False else ren.shape[1])
    Wc = cw + 2*pad
    Hc = src_big.shape[0] + ren.shape[0] + 3*pad + 10
    canvas = Image.new("L", (Wc, Hc), 255)
    top = Image.fromarray(src_big)
    bot = Image.fromarray(ren)
    canvas.paste(top, (int(Wc/2 - top.width/2 + (scx - sb[0]) - (scx - sb[0])), pad))
    # 以内容框中心对齐放置
    off_top = (int(round(Wc/2 - scx)), int(round(pad - sb[2])))
    off_bot = (int(round(Wc/2 - rcx)), int(round(pad + src_big.shape[0] + 3*pad - ry0)))
    canvas.paste(top, off_top, top.point(lambda v: 255-v))   # 用负片做 mask（白底黑线）
    canvas.paste(bot, off_bot, bot.point(lambda v: 255-v))
    canvas.save("对照_源图vs重绘_600dpi.png")
    print("→ 对照_源图vs重绘_600dpi.png  (%dx%d)" % canvas.size)

    # ---- 叠加差分（源=红，重绘=蓝，重合=黑）----
    ov = np.full((Hc, Wc, 3), 255, np.uint8)
    def stamp(arr, off, ch):
        x0, y0 = off
        h, w = arr.shape
        sub = np.zeros((Hc, Wc), bool)
        xs0, ys0 = max(0,x0), max(0,y0)
        xs1, ys1 = min(Wc, x0+w), min(Hc, y0+h)
        if xs1<=xs0 or ys1<=ys0: return
        m = arr[ys0-y0:ys1-y0, xs0-x0:xs1-x0] < 128
        sub[ys0:ys1, xs0:xs1] = m
        for c in range(3):
            if c != ch:
                ov[..., c][sub] = np.minimum(ov[..., c][sub], 160)
    stamp(src_big, off_top, 1)   # 源 → 减绿蓝＝红
    stamp(ren, off_bot, 0)       # 重绘 → 减红＝青
    Image.fromarray(ov).save("叠加差分_源红_重绘青_600dpi.png")
    print("→ 叠加差分_源红_重绘青_600dpi.png")

    # ---- 量测：重绘标签组 vs 源标签组（对齐后比较）----
    sys.path.insert(0, ".")
    G = json.load(open("geom.json", encoding="utf-8"))
    targets = {"A":[79.5,721.0],"B":[523.5,725.0],"C":[726.5,512.5],"D":[216.0,496.0],"E":[310.5,147.0],
               "A1":[49.0,231.0],"B1":[582.5,287.0],"C1":[713.0,59.0],"D1":[244.0,47.5]}
    groups = group_labels(components(ren, thr=128, min_area=200))
    groups = [g for g in groups if g["area"] < 30000]
    print("\n重绘标签组（对齐到源坐标系，px）：")
    report = {}
    for g in sorted(groups, key=lambda g: -g["area"])[:12]:
        # 重绘坐标 → 源坐标： src_x = (ren_x - off_bot_x)/S ；再乘 S 回到放大源系
        rx = g["cx"] - off_bot[0]; ry = g["cy"] - off_bot[1]
        # 在放大源系里的源标签中心
        for nm,(tx,ty) in targets.items():
            txb = sb[0] + tx*S - sb[0]; tyb = ty*S
        # 匹配最近
        best, bd = None, 1e9
        for nm,(tx,ty) in targets.items():
            tX = tx*S; tY = ty*S
            d = ((rx-tX)**2 + (ry-tY)**2)**0.5
            if d < bd: bd, best = d, nm
        print("  c=(%.1f,%.1f) wh=(%d,%d) area=%d → 最近源标签 %s（偏差 %.1f px@600dpi = %.3f mm）"
              % (rx, ry, g["w"], g["h"], g["area"], best, bd, bd*MMPP))
        report.setdefault(best, dict(dx=bd))
    json.dump(report, open("compare_report.json","w"), ensure_ascii=False, indent=1)

main()
