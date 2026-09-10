# -*- coding: utf-8 -*-
"""标定环 v3：以已知 TikZ mm 坐标的四条棱做子像素配准 → 精确映射 → 量标签偏差 → 反推 params。
用法：python calib.py [迭代数]"""
import json, subprocess, os, sys, shutil
import numpy as np
from scipy import ndimage
import fitz

K = 42.0/764.0; DPI = 600.0; MMPP = 25.4/DPI
TARGETS = {"A":[79.5,721.0],"B":[523.5,725.0],"C":[726.5,512.5],"D":[216.0,496.0],"E":[310.5,147.0],
           "A1":[36.0,222.0],"B1":[571.5,278.0],"C1":[704.5,50.5],"D1":[233.0,38.5]}
TGT_CAP = 63.0

def compile_pdf():
    for f in ("image2_重绘.tex","image2_重绘_预览壳.tex"):
        shutil.copy(f, os.path.join("build", f))
    subprocess.run(["xelatex","-interaction=nonstopmode","-halt-on-error","image2_重绘_预览壳.tex"],
                   cwd="build", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def pdf_page_mm():
    doc = fitz.open(os.path.join("build","image2_重绘_预览壳.pdf"))
    r = doc[0].rect
    return (r.width*25.4/72.0, r.height*25.4/72.0)

def render():
    doc = fitz.open(os.path.join("build","image2_重绘_预览壳.pdf"))
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(DPI/72.0, DPI/72.0), alpha=False)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:,:,:3].mean(axis=2)

def runs(v, i0, eps=0.55):
    out=[]; s=None
    for i,x in enumerate(v):
        if x>eps and s is None: s=i
        elif x<=eps and s is not None: out.append((i0+s, i0+i-1)); s=None
    if s is not None: out.append((i0+s, i0+len(v)-1))
    return out

def pick(rs, exp):
    return min(rs, key=lambda r: 0 if r[0]<=exp<=r[1] else min(abs(r[0]-exp), abs(r[1]-exp)))

def row_centroid(ik, y, xexp, half=40):
    x0=max(0,int(xexp)-half); x1=min(ik.shape[1], int(xexp)+half)
    rs = runs(ik[y, x0:x1], x0)
    if not rs: return None
    lo,hi = pick(rs, xexp)
    w = ik[y, lo:hi+1]; xs=np.arange(lo,hi+1)
    return float((w*xs).sum()/w.sum())

def col_centroid(ik, x, yexp, half=40):
    y0=max(0,int(yexp)-half); y1=min(ik.shape[0], int(yexp)+half)
    rs = runs(ik[y0:y1, x], y0)
    if not rs: return None
    lo,hi = pick(rs, yexp)
    w = ik[lo:hi+1, x]; ys=np.arange(lo,hi+1)
    return float((w*ys).sum()/w.sum())

def fit_registration(ik, C, page_mm):
    """以『线网连通域』为掩膜、四条已知棱做子像素配准（避开标签与虚线）。"""
    H, W = ik.shape
    ppm = W/page_mm[0]
    b = ik > 0.5
    lab, n = ndimage.label(b, structure=np.ones((3,3),int))
    sizes = ndimage.sum(b, lab, range(1,n+1)); big = int(np.argmax(sizes))+1
    net = (lab == big)
    nys, nxs = np.nonzero(net)
    nx0,nx1,ny0,ny1 = nxs.min(),nxs.max(),nys.min(),nys.max()
    # 初估：线网 bbox ≈ 已知 mm 极值（含半线宽）
    hw = 0.308/2
    bbox_mm = dict(x0=C["A"][0]-hw, x1=C["C"][0]+hw,
                   y1=C["D1"][1]+hw, y0=C["A"][1]-hw)
    def guess_x(Xmm):
        t=(Xmm-bbox_mm["x0"])/(bbox_mm["x1"]-bbox_mm["x0"])
        return nx0 + t*(nx1-nx0)
    def guess_y(Ymm):
        t=(Ymm-bbox_mm["y0"])/(bbox_mm["y1"]-bbox_mm["y0"])
        return ny1 - t*(ny1-ny0)
    def run_centroid_x(y, xexp, half=40):
        x0=max(0,int(xexp)-half); x1=min(W, int(xexp)+half)
        rs = runs(net[y, x0:x1], x0)
        if not rs: return None
        lo,hi = pick(rs, xexp)
        w = ik[y, lo:hi+1]; xs=np.arange(lo,hi+1)
        return float((w*xs).sum()/w.sum())
    def run_centroid_y(x, yexp, half=40):
        y0=max(0,int(yexp)-half); y1=min(H, int(yexp)+half)
        rs = runs(net[y0:y1, x], y0)
        if not rs: return None
        lo,hi = pick(rs, yexp)
        w = ik[lo:hi+1, x]; ys=np.arange(lo,hi+1)
        return float((w*ys).sum()/w.sum())
    XA, XC = C["A"][0], C["C"][0]
    ys_rows = np.linspace(guess_y(C["A"][1]+4), guess_y(C["A1"][1]-4), 7)
    pa=[]; pc=[]
    for y in ys_rows:
        y=int(round(y))
        a_=run_centroid_x(y, guess_x(XA)); c_=run_centroid_x(y, guess_x(XC))
        if a_ and c_: pa.append(a_); pc.append(c_)
    xA_ras, xB_ras = float(np.mean(pa)), float(np.mean(pc))
    YA, YB = C["A"][1], C["A1"][1]
    xs_cols = np.linspace(guess_x(XA+4), guess_x(C["C"][0]-6), 7)
    ra=[]; rb=[]
    for x in xs_cols:
        x=int(round(x))
        a_=run_centroid_y(x, guess_y(YA)); b_=run_centroid_y(x, guess_y(YB))
        if a_ and b_: ra.append(a_); rb.append(b_)
    yA_ras, yB_ras = float(np.mean(ra)), float(np.mean(rb))
    kx = (XC-XA)/(xB_ras-xA_ras)*ppm      # mm per raster px（应≈1）
    ky = (YB-YA)/(yB_ras-yA_ras)*ppm
    return dict(xA_ras=xA_ras, xA_mm=XA, xB_ras=xB_ras, xB_mm=XC,
                yA_ras=yA_ras, yA_mm=YA, yB_ras=yB_ras, yB_mm=YB, ppm=ppm, kx=kx, ky=ky)

def to_srcpx(R, C, reg):
    kx = (reg["xB_mm"]-reg["xA_mm"])/(reg["xB_ras"]-reg["xA_ras"])
    Xmm = reg["xA_mm"] + (R[0]-reg["xA_ras"])*kx
    ky = (reg["yB_mm"]-reg["yA_mm"])/(reg["yB_ras"]-reg["yA_ras"])
    Ymm = reg["yA_mm"] + (R[1]-reg["yA_ras"])*ky
    return Xmm/K, (42.0-Ymm)/K

def to_raster(tx, ty, C, reg):
    Xmm = tx*K; Ymm = 42.0 - ty*K
    kx = (reg["xB_mm"]-reg["xA_mm"])/(reg["xB_ras"]-reg["xA_ras"])
    ky = (reg["yB_mm"]-reg["yA_mm"])/(reg["yB_ras"]-reg["yA_ras"])
    Rx = reg["xA_ras"] + (Xmm-reg["xA_mm"])/kx
    Ry = reg["yA_ras"] + (Ymm-reg["yA_mm"])/ky
    return Rx, Ry

def label_groups(a, thr=128, min_area=400, gap=15, min_group_area=800):
    b = a < thr
    lab, n = ndimage.label(b, structure=np.ones((3,3),int))
    sizes = ndimage.sum(b, lab, range(1,n+1)); big = int(np.argmax(sizes))+1
    blobs=[]
    for i in range(1,n+1):
        if i==big: continue
        ys,xs = np.nonzero(lab==i)
        if len(xs)<min_area: continue
        blobs.append(dict(x0=int(xs.min()),x1=int(xs.max()),y0=int(ys.min()),y1=int(ys.max()),area=len(xs)))
    used=[False]*len(blobs); out=[]
    for i,c in enumerate(blobs):
        if used[i]: continue
        g=dict(c); used[i]=True; ch=True
        while ch:
            ch=False
            for j,d in enumerate(blobs):
                if used[j]: continue
                if not (d["x0"]>g["x1"]+gap or d["x1"]<g["x0"]-gap or d["y0"]>g["y1"]+gap or d["y1"]<g["y0"]-gap):
                    g["x0"]=min(g["x0"],d["x0"]); g["x1"]=max(g["x1"],d["x1"])
                    g["y0"]=min(g["y0"],d["y0"]); g["y1"]=max(g["y1"],d["y1"]); g["area"]+=d["area"]
                    used[j]=True; ch=True
        if g["area"]<min_group_area: continue
        g["cx"]=(g["x0"]+g["x1"])/2; g["cy"]=(g["y0"]+g["y1"])/2
        g["w"]=g["x1"]-g["x0"]+1; g["h"]=g["y1"]-g["y0"]+1
        out.append(g)
    return out

def run_once(verbose=True):
    subprocess.run([sys.executable,"gen.py"], check=True, stdout=subprocess.DEVNULL)
    compile_pdf()
    a = render(); ik = 1.0-a/255.0
    C = json.load(open("coords.json", encoding="utf-8"))
    page_mm = pdf_page_mm()
    reg = fit_registration(ik, C, page_mm)
    ky_ = abs((reg["yB_mm"]-reg["yA_mm"])/(reg["yB_ras"]-reg["yA_ras"]))
    if verbose:
        print("  配准：xA_ras=%.2f yA_ras=%.2f yB_ras=%.2f | 标尺 kx=%.5f ky=%.5f (应≈1) ppm=%.3f"
              % (reg["xA_ras"], reg["yA_ras"], reg["yB_ras"], reg["kx"], reg["ky"], reg["ppm"]))
    # 连通域（排除线网）
    b = a < 128
    lab, n = ndimage.label(b, structure=np.ones((3,3),int))
    sizes = ndimage.sum(b, lab, range(1,n+1)); big = int(np.argmax(sizes))+1
    comps=[]
    for i in range(1,n+1):
        if i==big: continue
        ys,xs = np.nonzero(lab==i)
        if len(xs) < 250: continue
        comps.append(dict(x0=int(xs.min()),x1=int(xs.max()),y0=int(ys.min()),y1=int(ys.max()),area=len(xs)))
    res={}
    for nm,(tx,ty) in TARGETS.items():
        ex, ey = to_raster(tx, ty, C, reg)          # 期望栅格位置（由目标反推）
        R = 60/reg["kx"]/K if False else 60*reg["ppm"]/ (K*reg["ppm"])  # 60 源px 对应栅格 px
        R = 60*K/ (1/reg["ppm"])                     # = 60*K*ppm
        R = 60 * K * reg["ppm"]
        cand = [c for c in comps if abs((c["x0"]+c["x1"])/2-ex) < R and abs((c["y0"]+c["y1"])/2-ey) < R]
        if not cand:
            if verbose: print("  %-3s 未找到（窗口 %.0fpx@600dpi）" % (nm, R)); continue
        g = max(cand, key=lambda c: c["area"])
        sx, sy = to_srcpx(((g["x0"]+g["x1"])/2, (g["y0"]+g["y1"])/2), C, reg)
        r = dict(sx=sx, sy=sy, dx=sx-TARGETS[nm][0], dy=sy-TARGETS[nm][1],
                 w=(g["x1"]-g["x0"]+1)/(reg["ppm"]*K), h=(g["y1"]-g["y0"]+1)/(reg["ppm"]*K),
                 area=g["area"], ra=(g["x0"],g["x1"],g["y0"],g["y1"]))
        res.setdefault(nm,[]).append(r)
        if verbose:
            print("  %-3s 源px中心=(%.1f,%.1f) Δ=(%+.2f,%+.2f) 字母盒=%.0fx%.0fpx 面积=%d" %
                  (nm, sx, sy, r["dx"], r["dy"], r["w"], r["h"], r["area"]))
    return res

if __name__=="__main__":
    it = int(sys.argv[1]) if len(sys.argv)>1 else 1
    for k in range(it):
        print("== 迭代 %d ==" % (k+1))
        res = run_once()
        P=json.load(open("params.json",encoding="utf-8"))
        caps=[r["h"] for r in res.get("A",[])]
        if caps and abs(caps[0]-TGT_CAP)>0.05 and caps[0]>0:
            cur=P["fontsize_pt"]; new=cur*TGT_CAP/caps[0]
            print("  字号 %.2f → %.2f pt（A 高 %.1f / 目标 %.1f）" % (cur,new,caps[0],TGT_CAP))
            P["fontsize_pt"]=round(new,2)
        for nm,lst in res.items():
            P["label_offset_px"].setdefault(nm,[0.0,0.0])
            P["label_offset_px"][nm][0]-=lst[0]["dx"]; P["label_offset_px"][nm][1]-=lst[0]["dy"]
        json.dump(P, open("params.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
