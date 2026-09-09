# -*- coding: utf-8 -*-
"""细黑岗附注探针：各品牌最细几档在条目岗（靶竖粗 6px）/角度岗（靶 7px）的实际竖粗。
复用 _ht_judge2 的渲染口径（EM=96、PIL anchor=ls、glyph_metrics 同式），只列不改。"""
import numpy as np, json, os
from PIL import Image, ImageFont, ImageDraw
from scipy import ndimage

FB = "C:/提示词/工作区/字替对照-0909/fonts/"
NF = "C:/提示词/工作区/字替对照-0909/variantE/_calib/fonts/"
EM = 96.0

CANDS = {
    "思源": [(f"w{w}", NF + f"NSC-w{w}.ttf") for w in (250, 300, 350, 400)],
    "普惠": [(w, FB + f"PuHuiTi__Alibaba-PuHuiTi-{w}.ttf") for w in ("Regular", "Light", "ExtraLight") if os.path.exists(FB + f"PuHuiTi__Alibaba-PuHuiTi-{w}.ttf")],
    "HarmonyOS": [(w, FB + f"_npm原始包/npm_fontpkg--harmony-os-sans-sc/package/HarmonyOS_Sans_SC_{w}.ttf") for w in ("Thin", "Light", "Regular")],
    "雅黑(校验)": [("Regular", "C:/Windows/Fonts/msyh.ttc")],
}

def glyph_metrics(cell):
    dark = cell < 128
    ys, xs = np.where(dark)
    if ys.size == 0:
        return None
    g = dark[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = g.shape
    lr, lc = [], []
    for row in g:
        idx = np.flatnonzero(row)
        if idx.size:
            for s in np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1):
                lr.append(len(s))
    for col in g.T:
        idx = np.flatnonzero(col)
        if idx.size:
            for s in np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1):
                lc.append(len(s))
    sh = [L for L in lr if L < 0.5 * w]
    sv = [L for L in lc if L < 0.5 * h]
    if not sh or not sv:
        return None
    return dict(竖笔粗=float(np.median(sh)), 横笔粗=float(np.median(sv)))

def render_v(s, font):
    out = []
    for ch in s:
        im = Image.new("L", (int(EM) + 60, int(EM) + 60), 255)
        ImageDraw.Draw(im).text((30, int(EM * 1.6)), ch, font=font, fill=0, anchor="ls")
        m = glyph_metrics(np.asarray(im))
        if m:
            out.append(m)
    return float(np.median([p["竖笔粗"] for p in out])), float(np.median([p["横笔粗"] for p in out]))

for gang, s, target in (("条目10.09", "课时折射现象与折射定律", 6.0), ("角度10.09", "角度二用动量定理定量计算", 7.0)):
    print(f"==== {gang}（靶竖粗 {target:.0f}px） ====")
    for brand, weights in CANDS.items():
        line = []
        for wname, wpath in weights:
            try:
                v, hz = render_v(s, ImageFont.truetype(wpath, int(EM)))
                line.append(f"{wname} 竖{v:.0f}/横{hz:.0f}")
            except Exception as e:
                line.append(f"{wname} ERR")
        print(f"{brand:10s} " + "  ".join(line))
