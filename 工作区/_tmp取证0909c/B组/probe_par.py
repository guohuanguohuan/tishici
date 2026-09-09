# -*- coding: utf-8 -*-
"""取证B组·∥定位：dump p1/p2 所有 fill 矢量路径，找 TikZ 双平行四边形（每笔≈0.526em 宽×0.972em 高，两笔成对）。"""
import pymupdf, json, os

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\main.pdf"
doc = pymupdf.open(SRC)

out = []
for pno in (1, 2):
    page = doc[pno - 1]
    fills = []
    for d in page.get_drawings():
        if d["fill"] is None:
            continue
        r = pymupdf.Rect(d["rect"])
        fills.append((round(r.x0,2), round(r.y0,2), round(r.x1,2), round(r.y1,2),
                      round(r.width,2), round(r.height,2), len(d["items"])))
    print(f"--- p{pno}: {len(fills)} fill drawings")
    # ∥ 候选：h 在 8.5–11.5pt，w 在 3.5–7pt（单笔≈0.526em），或成对合并宽 7–11pt
    for f in fills:
        x0,y0,x1,y1,w,h,n = f
        if 7.5 < h < 12.0 and 2.5 < w < 8.0:
            out.append({"page": pno, "rect": [x0,y0,x1,y1], "w": w, "h": h, "n_items": n})
for r in out:
    print(r)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "par_candidates.json"), "w"), indent=1)
