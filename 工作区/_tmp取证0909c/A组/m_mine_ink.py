# -*- coding: utf-8 -*-
"""main.pdf p1 意见28/32 墨隙实测：600dpi 渲染→行墨投影→量隙；出证据裁片。
基线(pt)来自 m_mine_text.py 的 fitz 提取。"""
import fitz, numpy as np, sys, io
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding="utf-8")

DPI = 600
S = DPI / 72.0                 # px per pt
PXMM = 25.4 / DPI              # mm per px
doc = fitz.open(r"C:/提示词/工作区/字替对照-0909/variantF/main.pdf")
pix = doc[0].get_pixmap(dpi=DPI, alpha=False)
img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
A = np.asarray(img)

def ink_gap(x0, x1, y1, y2, thr=128):
    """strip between baselines y1,y2 (pt, x0..x1 pt): return gap px & band list."""
    r0, r1 = int(y1 * S) + 1, int(y2 * S)
    c0, c1 = int(x0 * S), int(x1 * S)
    strip = A[r0:r1, c0:c1]
    has = (strip < thr).any(axis=1)
    idx = np.flatnonzero(has)
    if idx.size == 0:
        return None, [], (r0, r1)
    bands, s, p = [], int(idx[0]), int(idx[0])
    for i in idx[1:]:
        i = int(i)
        if i - p > 1:
            bands.append((s, p)); s = i
        p = i
    bands.append((s, p))
    gap = bands[-1][0] - bands[0][1] - 1 if len(bands) >= 2 else 0
    return gap, bands, (r0, r1)

def annotate(x0, x1, y1, y2, fname, title):
    r0, r1 = int(y1 * S) - 4, int(y2 * S) + 4
    c0, c1 = int(x0 * S), int(x1 * S)
    crop = img.crop((c0, r0, c1, r1)).convert("RGB")
    dr = ImageDraw.Draw(crop)
    g, bands, (R0, R1) = ink_gap(x0, x1, y1, y2)
    if g is not None and len(bands) >= 2:
        ya = R0 + bands[0][1] - (r0 - 0)  # last ink row of upper line
        yb = R0 + bands[-1][0]
        for yy in (ya, yb):
            dr.line([(0, yy - r0), (c1 - c0, yy - r0)], fill=(255, 0, 0), width=2)
        ymid = (ya + yb) // 2 - r0
        dr.line([(c1 - c0 - 260, ymid), (c1 - c0, ymid)], fill=(0, 120, 255), width=2)
        dr.text((8, 4), f"{title}  ink-gap {g}px = {g*PXMM:.2f}mm  ({g/S:.2f}pt)",
                fill=(200, 0, 0))
    crop.save(fname)
    return g

LX = (49.0, 282.0)   # left col text x-range pt
RX = (310.0, 546.0)  # right col
res = {}
# 意见28：p1 左栏
res["28 (1)行→(2)段"] = annotate(*LX, 443.03, 466.31, "e28_gap_12.png", "e28 (1)->(2)")
res["28对照:段内行(2)L1→L2"] = annotate(*LX, 466.31, 484.49, "e28_ctrl_intra.png", "e28 ctrl intra-line")
res["28对照:条目1[注意]末→条目2"] = annotate(*LX, 419.75, 443.03, "e28_ctrl_item.png", "e28 ctrl item->item")
res["28对照:条目2注意末→条目3"] = annotate(*LX, 539.04, 557.22, "e28_ctrl_item23.png", "e28 ctrl item2->3")
# 意见32：p1 右栏
res["32 (1)[解析]末→(2)题干"] = annotate(*RX, 591.22, 616.38, "e32_gap_zt12.png", "e32 zt(1)->zt(2)")
res["32对照:(1)题干L2→[解析]"] = annotate(*RX, 554.86, 573.04, "e32_ctrl_stem_jx.png", "e32 ctrl stem->[解析]")
res["32对照:(2)题干→[解析]"] = annotate(*RX, 616.38, 634.56, "e32_ctrl_stem2_jx.png", "e32 ctrl stem2->[解析]")
res["32对照:[解析]L1→L2"] = annotate(*RX, 573.04, 591.22, "e32_ctrl_jx_intra.png", "e32 ctrl jx intra")
res["32头:【诊断分析】→(1)题干"] = annotate(*RX, 516.50, 536.68, "e32_head_stem.png", "e32 head->zt1")

print(f"{'junction':32s} {'gap px':>7s} {'gap mm':>8s} {'gap pt':>8s}")
for k, g in res.items():
    if g is None:
        print(f"{k:32s}   n/a")
    else:
        print(f"{k:32s} {g:7d} {g*PXMM:8.3f} {g/S:8.2f}")

# 区块级证据整图（含多行上下文）
def region(x0, x1, y0, y1, fname, title):
    r0, r1, c0, c1 = int(y0 * S), int(y1 * S), int(x0 * S), int(x1 * S)
    crop = img.crop((c0, r0, c1, r1)).convert("RGB")
    dr = ImageDraw.Draw(crop)
    dr.text((8, 4), title, fill=(200, 0, 0))
    crop.save(fname)

region(*LX, 408, 568, "e28_mine_p1_L_ctx.png", "e28 ours p1 left: tiao1[notice] / tiao2(1) / (2)+notice / tiao3")
region(*RX, 505, 662, "e32_mine_p1_R_ctx.png", "e32 ours p1 right: zhenhead / zt(1)+jx / zt(2)+jx")
print("evidence saved")
