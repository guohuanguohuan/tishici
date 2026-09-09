# -*- coding: utf-8 -*-
"""取证B组·胶宽实测：用 PyMuPDF 字符 advance bbox 直接量 = 两侧的排版胶宽（＝与侧边距无关），
并区分 自然5mu / 被拉伸。覆盖 p1–p3 全部 = ，按正文/表格分类。∥ 用左右相邻字母 advance 框差分。"""
import json, os
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\提示词\工作区\字替对照-0909\variantF\main.pdf"
doc = pymupdf.open(SRC)

# 表格 y 带（pt）：p1 特殊向量表 ≈ 400–492；p2 运算律表 ≈ 330–476；p2 投影表 ≈ 560–720?（先粗分，后按 ctx 复核）
TABLE_BAND = {1: [(395, 495)], 2: [(330, 478)]}

def classify(pno, y):
    for (a, b) in TABLE_BAND.get(pno, []):
        if a <= y <= b:
            return "table"
    return "body"

rows = []
for pno in (1, 2, 3):
    page = doc[pno - 1]
    raw = page.get_text("rawdict")
    for blk in raw["blocks"]:
        if blk["type"] != 0:
            continue
        for line in blk["lines"]:
            chars = [(ch["c"], pymupdf.Rect(ch["bbox"])) for span in line["spans"] for ch in span["chars"]]
            for i, (c, r) in enumerate(chars):
                if c != "=":
                    continue
                prev = chars[i-1] if i > 0 else None
                nxt = chars[i+1] if i+1 < len(chars) else None
                gl = r.x0 - prev[1].x1 if prev else None
                gr = nxt[1].x0 - r.x1 if nxt else None
                rows.append({
                    "page": pno, "y": round(r.y0, 1), "x": round(r.x0, 1),
                    "cls": classify(pno, r.y0),
                    "prev": prev[0] if prev else "¶", "next": nxt[0] if nxt else "¶",
                    "glueL_pt": round(gl, 2) if gl is not None else None,
                    "glueR_pt": round(gr, 2) if gr is not None else None,
                })

print(f"{'pg':>2} {'y':>6} {'x':>6}  {'cls':5} {'prev':>3}{'next':>4}  L_pt     R_pt    L_mm   R_mm")
for r in rows:
    L = r["glueL_pt"]; R = r["glueR_pt"]
    print(f'{r["page"]:>2} {r["y"]:>6} {r["x"]:>6}  {r["cls"]:5} {r["prev"]:>3}{r["next"]:>4}  '
          f'{L if L is not None else "":>7} {R if R is not None else "":>7}  '
          f'{L and round(L*25.4/72,2)}   {R and round(R*25.4/72,2)}')

json.dump(rows, open(os.path.join(HERE, "glue_eq.json"), "w"), ensure_ascii=False, indent=1)

# ∥：取 p1/p2 的 ∥ 矩形（两组笔画合并），在其 x 带内找同一文本行的左右字母 advance 框
PARS = {
    1: [(228.61, 565.79, 236.88, 575.56, "body"), (498.59, 432.15, 507.20, 442.32, "table")],
    2: [(79.53, 221.19, 87.80, 230.96, "body"), (96.51, 458.74, 105.11, 468.90, "table"),
        (84.48, 506.55, 92.75, 516.32, "body"), (118.44, 506.55, 126.71, 516.32, "body"),
        (162.02, 506.55, 170.30, 516.32, "body"), (84.48, 568.07, 92.75, 577.84, "body")],
}
print("\n=== ∥ 胶宽（相邻字母 advance 差）===")
for pno, lst in PARS.items():
    page = doc[pno - 1]
    raw = page.get_text("rawdict")
    for (x0, y0, x1, y1, cls) in lst:
        # 找与 ∥ 垂直重叠的行
        for blk in raw["blocks"]:
            if blk["type"] != 0: continue
            for line in blk["lines"]:
                chars = [(ch["c"], pymupdf.Rect(ch["bbox"])) for span in line["spans"] for ch in span["chars"]]
                # ∥ 左邻 = 行内 x1 ≤ x0 的最右字符；右邻 = x0_ ≥ x1 的最左字符（同线 y 带内）
                same = [(c, r) for c, r in chars if r.y0 < (y0+y1)/2 + 6 and r.y1 > (y0+y1)/2 - 6]
                lefts = [(c, r) for c, r in same if r.x1 <= x0 + 0.5]
                rights = [(c, r) for c, r in same if r.x0 >= x1 - 0.5]
                if not lefts or not rights: continue
                lp = max(lefts, key=lambda t: t[1].x1)
                rp = min(rights, key=lambda t: t[1].x0)
                gl = x0 - lp[1].x1; gr = rp[1].x0 - x1
                print(f'p{pno} y={y0:6.1f} {cls:5} ∥ 左邻{lp[0]!r} L={gl:5.2f}pt={gl*25.4/72:4.2f}mm   右邻{rp[0]!r} R={gr:5.2f}pt={gr*25.4/72:4.2f}mm')
