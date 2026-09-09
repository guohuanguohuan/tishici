# -*- coding: utf-8 -*-
"""取证B组·墨隙实测：main.pdf 中正文/表格的 = 与 ∥ 两侧墨隙（1200dpi 逐列扫描）。
输出 mm 数值＋证据裁片图（红标墨隙边界）。只读项目 PDF，产物写本目录。"""
import os, json
import pymupdf
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\提示词\工作区\字替对照-0909\variantF\main.pdf"
DPI = 1200
SC = DPI / 72.0            # px per pt
PT2MM = 25.4 / 72.0
THR = 160                  # 灰度<160 记墨

# 目标清单：(标签, page, 符号bbox(pt, union for ∥), 类别 body/table, 上下式子)
TARGETS = [
    ("正文·p1条目3  0∥a",      1, (228.61, 565.79, 236.88, 575.56), "body", "∥"),
    ("正文·p2条目2  a∥b",       2, (79.53, 221.19, 87.80, 230.96),  "body", "∥"),
    ("正文·p2条目2  a=λb",      2, (277.90, 222.90, 284.54, 232.95), "body", "="),
    ("正文·p2判断(2)解析 a=λb",  2, (220.70, 569.80, 227.34, 579.85), "body", "="),
    ("表格·p1特殊向量表 a∥b",    1, (498.59, 432.15, 507.20, 442.32), "table", "∥"),
    ("表格·p1特殊向量表 a=b",    1, (498.60, 475.40, 505.50, 485.86), "table", "="),
    ("表格·p2运算律表 a∥b",      2, (96.51, 458.74, 105.11, 468.90),  "table", "∥"),
    ("表格·p2运算律表 a=λb",     2, (207.80, 460.60, 214.44, 471.06), "table", "="),
]

doc = pymupdf.open(SRC)
WIN = 22.0     # 左右搜索窗(pt)
results = []
for label, pno, (x0, y0, x1, y1), cls, sym in TARGETS:
    page = doc[pno - 1]
    band_y0 = y0 - 2.0 if sym == "∥" else y0 - 1.0
    band_y1 = y1 + 1.2 if sym == "∥" else y1 + 1.0
    clip = pymupdf.Rect(x0 - WIN, band_y0, x1 + WIN, band_y1)
    pix = page.get_pixmap(dpi=DPI, clip=clip, colorspace=pymupdf.csGRAY)
    img = Image.frombytes("L", (pix.width, pix.height), pix.samples)
    W, H = img.size
    px = img.load()
    inkcol = [any(px[c, r] < THR for r in range(H)) for c in range(W)]
    # 墨列段
    segs = []
    c = 0
    while c < W:
        if inkcol[c]:
            s = c
            while c < W and inkcol[c]:
                c += 1
            segs.append((s, c - 1))
        else:
            c += 1
    # 符号自身墨段：位于符号bbox内的段（pt→px 偏移）
    bx0 = (x0 - (x0 - WIN)) * SC
    bx1 = (x1 - (x0 - WIN)) * SC
    sym_segs = [s for s in segs if s[0] >= bx0 - 3 and s[1] <= bx1 + 3]
    if not sym_segs:
        print(f"[{label}] 未找到符号墨段! segs={segs[:10]}")
        continue
    sym_l, sym_r = sym_segs[0][0], sym_segs[-1][1]
    # 左邻墨段（与符号间白隙≥3px 视为分开）
    left = [s for s in segs if s[1] < sym_l - 3]
    right = [s for s in segs if s[0] > sym_r + 3]
    gl = (sym_l - left[-1][1] - 1) / SC * PT2MM if left else None
    gr = (right[0][0] - sym_r - 1) / SC * PT2MM if right else None
    # 符号自身墨宽
    symw = (sym_r - sym_l + 1) / SC * PT2MM
    results.append({"label": label, "page": pno, "class": cls, "sym": sym,
                    "gapL_mm": round(gl, 3) if gl is not None else None,
                    "gapR_mm": round(gr, 3) if gr is not None else None,
                    "sym_ink_mm": round(symw, 3)})
    print(f"{label:26s} {sym} 左隙={gl and round(gl,2)}mm 右隙={gr and round(gr,2)}mm 符号墨宽={symw:.2f}mm")
    # 证据裁片：再渲一张 600dpi 彩色宽视野（±16pt），红竖线标符号墨缘与邻墨缘
    dpi2 = 600; sc2 = dpi2 / 72.0
    clip2 = pymupdf.Rect(x0 - 16, band_y0 - 0.5, x1 + 16, band_y1 + 0.5)
    pix2 = page.get_pixmap(dpi=dpi2, clip=clip2)
    img2 = Image.frombytes("RGB", (pix2.width, pix2.height), pix2.samples)
    dr = ImageDraw.Draw(img2)
    def X(pt): return (pt - clip2.x0) * sc2
    dr.line([X(x0), 0, X(x0), img2.height], fill=(255, 0, 0), width=1)
    dr.line([X(x1), 0, X(x1), img2.height], fill=(255, 0, 0), width=1)
    if left:
        dr.line([X(x0 - WIN + left[-1][1] / SC), 0, X(x0 - WIN + left[-1][1] / SC), img2.height], fill=(0, 128, 255), width=1)
    if right:
        dr.line([X(x0 - WIN + right[0][0] / SC), 0, X(x0 - WIN + right[0][0] / SC), img2.height], fill=(0, 180, 0), width=1)
    fn = f"crop_{cls}_{sym}_{pno}_{label.split()[-1]}.png".replace("/", "-")
    img2.save(os.path.join(HERE, fn))

json.dump(results, open(os.path.join(HERE, "gaps_main.json"), "w"), ensure_ascii=False, indent=1)
print("\nsaved", len(results), "targets; crops in", HERE)
