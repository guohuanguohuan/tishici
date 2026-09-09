# -*- coding: utf-8 -*-
"""取证B组·∥胶宽(debug)＋λ左隙分解：∥ 用页面几何全量字符（不分行聚合）找左右邻 advance 框；
λ 侧：条目2 = 右侧 4.87mm 墨隙拆解为 胶宽＋λ左侧边距。"""
import pymupdf

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\main.pdf"
doc = pymupdf.open(SRC)

PARS = [
    (1, 228.61, 565.79, 236.88, 575.56, "body", "条目3 0∥a"),
    (1, 498.59, 432.15, 507.20, 442.32, "table", "特殊向量表 a∥b"),
    (2, 79.53, 221.19, 87.80, 230.96, "body", "条目2 a∥b"),
    (2, 96.51, 458.74, 105.11, 468.90, "table", "运算律表 a∥b"),
    (2, 84.48, 506.55, 92.75, 516.32, "body", "判断(1) a∥b"),
    (2, 118.44, 506.55, 126.71, 516.32, "body", "判断(1) b∥c"),
    (2, 162.02, 506.55, 170.30, 516.32, "body", "判断(1) a∥c"),
    (2, 84.48, 568.07, 92.75, 577.84, "body", "判断(2) a∥b"),
]
for pno, x0, y0, x1, y1, cls, tag in PARS:
    page = doc[pno - 1]
    raw = page.get_text("rawdict")
    yc = (y0 + y1) / 2
    cand = []
    for blk in raw["blocks"]:
        if blk["type"] != 0: continue
        for line in blk["lines"]:
            for span in line["spans"]:
                for ch in span["chars"]:
                    r = pymupdf.Rect(ch["bbox"])
                    if r.y0 < yc + 7 and r.y1 > yc - 7 and r.x1 <= x0 + 1 and r.x0 >= x0 - 30:
                        cand.append((ch["c"], r))
    if not cand:
        print(f"p{pno} {cls:5} {tag}: 无左邻候选")
        continue
    c, r = max(cand, key=lambda t: t[1].x1)
    gl = x0 - r.x1
    # 右邻
    cand2 = []
    for blk in raw["blocks"]:
        if blk["type"] != 0: continue
        for line in blk["lines"]:
            for span in line["spans"]:
                for ch in span["chars"]:
                    rr = pymupdf.Rect(ch["bbox"])
                    if rr.y0 < yc + 7 and rr.y1 > yc - 7 and rr.x0 >= x1 - 1 and rr.x0 <= x1 + 30:
                        cand2.append((ch["c"], rr))
    c2, r2 = (min(cand2, key=lambda t: t[1].x0) if cand2 else ("¶", None))
    gr = (r2.x0 - x1) if r2 else None
    print(f"p{pno} {cls:5} {tag:14s} 左邻{c!r} L={gl:5.2f}pt={gl*25.4/72:4.2f}mm   "
          f"右邻{c2!r} R={gr and round(gr,2)}pt={gr and round(gr*25.4/72,2)}mm")

# λ 左隙分解：p2 条目2 = at x 277.9..284.5 y 222.9；找其右侧最近的 λ/⃗b 字符
print("\n=== p2 条目2  a=λb 的 = 右侧分解 ===")
page = doc[1]
raw = page.get_text("rawdict")
targets = []
for blk in raw["blocks"]:
    if blk["type"] != 0: continue
    for line in blk["lines"]:
        for span in line["spans"]:
            for ch in span["chars"]:
                r = pymupdf.Rect(ch["bbox"])
                if 219 < r.y0 < 236 and r.x0 > 284.0:
                    targets.append((ch["c"], round(r.x0,2), round(r.x1,2), round(r.y0,1), round(r.y1,1)))
targets.sort(key=lambda t: t[1])
for t in targets[:6]:
    print(t)
