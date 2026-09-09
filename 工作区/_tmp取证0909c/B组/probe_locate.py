# -*- coding: utf-8 -*-
"""取证B组·定位：main.pdf 中所有 = 字符与 ∥(TikZ双平行四边形矢量路径) 的位置＋上下文。
只读 main.pdf，输出 JSON。不改项目文件。"""
import json, os
import pymupdf

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\main.pdf"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locate.json")

doc = pymupdf.open(SRC)
print("pages:", len(doc), "size:", doc[0].rect)

results = []
for pno, page in enumerate(doc, 1):
    raw = page.get_text("rawdict")
    # 1) 所有 = 字符
    for blk in raw["blocks"]:
        if blk["type"] != 0:
            continue
        for line in blk["lines"]:
            chars = [(ch["c"], pymupdf.Rect(ch["bbox"])) for span in line["spans"] for ch in span["chars"]]
            for i, (c, r) in enumerate(chars):
                if c == "=":
                    lo = max(0, i - 12); hi = min(len(chars), i + 13)
                    ctx = "".join(cc for cc, _ in chars[lo:hi])
                    results.append({
                        "kind": "eq", "page": pno,
                        "bbox": [round(v, 2) for v in r],
                        "idx": i, "ctx": ctx,
                    })
    # 2) ∥ = TikZ 矢量：找页面上所有填充路径，按几何筛选（两组四边形 → 一个 drawing 内多条 path item）
    for d in page.get_drawings():
        r = pymupdf.Rect(d["rect"])
        w, h = r.width, r.height
        # ∥ 图形：宽≈0.82em(2.9mm≈8.3pt)，高≈0.97em(3.5mm≈9.8pt)——10.09/10.5/12pt 字号下宽 8.3–10.3pt
        if 6.0 < w < 12.5 and 7.0 < h < 13.5 and d["fill"] is not None:
            # 数四边形数（fill path items，每 item 一个多边形）
            quads = [it for it in d["items"] if it[0] == "qu" or it[0] == "l"]
            results.append({
                "kind": "par_guess", "page": pno,
                "bbox": [round(v, 2) for v in r],
                "n_items": len(d["items"]),
                "ops": ",".join(sorted(set(it[0] for it in d["items"]))),
            })

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)

# 摘要打印
eqs = [r for r in results if r["kind"] == "eq"]
pars = [r for r in results if r["kind"] == "par_guess"]
print("eq count:", len(eqs), " par_guess count:", len(pars))
for r in results:
    b = r["bbox"]
    print(f'{r["kind"]:9s} p{r["page"]} x={b[0]:7.1f} y={b[1]:7.1f} w={b[2]-b[0]:5.2f} h={b[3]-b[1]:5.2f}  {r.get("ctx","")[:40]}')
