# -*- coding: utf-8 -*-
# ③片: 逐图左右文隙/上下距测量 + 裁片
import numpy as np, json, os
from PIL import Image

B = r"C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/"
OUT = r"C:/提示词/工作区/全品结构提取/数学选必一/_tmp扫差0908b/"
MMX, MMY = 210/2977, 297/4176
THR = 128
CANDS = json.load(open(OUT+"_③图候选.json"))

def ink(a): return a < THR

for page, cands in CANDS.items():
    a = ink(np.asarray(Image.open(B+page).convert("L")))
    H, W = a.shape
    for ci, (x0, y0, x1, y1, w, h) in enumerate(cands):
        if w > 1000 and h < 130: continue  # 花形行
        if page == "p15.png" and y0 > 3100: continue  # 流程图
        col_l, col_r = (250, 1430) if x0 < 1480 else (1546, 2722)
        # 同带(y0..y1)内图外墨迹的x分布
        band = a[y0:y1+1, :]
        xs = np.where(band.any(axis=0))[0]
        left_ink = xs[(xs >= col_l-10) & (xs < x0-8)]
        right_ink = xs[(xs > x1+8) & (xs <= col_r+10)]
        lgap = (x0 - left_ink.max())*MMX if len(left_ink) else None
        rgap = (right_ink.min() - x1)*MMX if len(right_ink) else None
        # 上下距: 图带正上/正下(x0..x1范围内)的墨
        vcol = a[:, x0:x1+1]
        rows = np.where(vcol.any(axis=1))[0]
        above = rows[rows < y0-4]
        below = rows[rows > y1+4]
        vgap_up = (y0 - above.max())*MMY if len(above) and y0-above.max() < 600 else None
        vgap_dn = (below.min() - y1)*MMY if len(below) and below.min()-y1 < 600 else None
        print("%s#%d x%d-%d y%d-%d(%.0fx%.0fmm) 左隙%s 右隙%s 上距%s 下距%s" % (
            page.replace(".png",""), ci+1, x0, x1, y0, y1, w*MMX, h*MMY,
            "%.1fmm" % lgap if lgap is not None else "无字",
            "%.1fmm" % rgap if rgap is not None else "无字",
            "%.1fmm" % vgap_up if vgap_up is not None else "远",
            "%.1fmm" % vgap_dn if vgap_dn is not None else "远"))
        # 裁片: 图+左右各150px
        m = 150
        crop = Image.open(B+page).crop((max(x0-m, 0), max(y0-90, 0), min(x1+m, W), min(y1+90, H)))
        if crop.width > 1500:
            crop = crop.resize((crop.width//2, crop.height//2), Image.LANCZOS)
        crop.save(OUT+"③_图_%s_%d.png" % (page.replace(".png",""), ci+1))
