# -*- coding: utf-8 -*-
"""目验修红0913 复验：①六件「如图」删语后文本层核对 ②课时03 选项几何核对 ③课时05 断行核对"""
import pymupdf, re, os

ROOT = r"C:/提示词/工作区/M2-第1章量产0911/成卷"
P = {
    "导学件/课时03": 3, "导学件/课时05": 3, "导学件/课时06": 4,
    "导学件/课时07": 4, "导学件/衔接节-1.2.1前": 4, "练习件/课时10": 2,
}

def norm(s):
    return re.sub(r"\s+", "", s)

# ---------- ① 删语核对：目标串在成品全文中应 0 命中 ----------
targets = {
    "衔接5":   "如图，四边形ABCD的对角线相交于点O",
    "课06ZSD": "直线的方向向量：如图，",
    "课07ZSD": "平面的法向量：如图，",
    "课10题4": "如图所示，已知正三角形ABC的中心为O",
    "课10题13": "如图所示，已知四棱锥P-ABCD中，ABCD为矩形",
    "课10题14": "如图所示，直三棱柱ABC-A1B1C1中，AC⊥BC",
}
print("=== ① 删语核对（成品 PDF 文本层，去空白后匹配）===")
for d in P:
    doc = pymupdf.open(os.path.join(ROOT, d, "main.pdf"))
    full = norm("".join(pg.get_text() for pg in doc))
    for name, t in targets.items():
        hit = norm(t).replace("1B1C1", "1𝐵1𝐶1") in full or norm(t) in full
        if hit:
            print(f"  [残留] {d} :: {name}")
    print(f"  {d}: 全文「如图」出现 {full.count('如图')} 次")

# ---------- ② 课时03 课堂评价 Q1 选项几何 ----------
print("\n=== ② 课时03 p3 课堂评价Q1 选项盒位 ===")
doc = pymupdf.open(os.path.join(ROOT, "导学件/课时03", "main.pdf"))
pg = doc[2]
CW = 238.11  # \linewidth pt
words = []
for b in pg.get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        t = norm("".join(s["text"] for s in l["spans"]))
        if any(k in t for k in ("必共线", "必共面", "必不共面", "必为单位向量")):
            words.append((round(l["bbox"][0], 1), round(l["bbox"][2], 1), t))
for x0, x1, t in sorted(words):
    over = "  <-- 超栏宽!" if x1 > 308.41 + CW + 0.6 and x0 > 300 else ""
    print(f"  x {x0:7.2f} -> {x1:7.2f} | {t}{over}")

# ---------- ③ 课时05 知识点二〔注意〕断行 ----------
print("\n=== ③ 课时05 p1 〔注意〕夹角范围行 ===")
doc = pymupdf.open(os.path.join(ROOT, "导学件/课时05", "main.pdf"))
pg = doc[0]
for b in pg.get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        t = "".join(s["text"] for s in l["spans"])
        if "夹角范围" in t or re.match(r"^\s*[；;]", t) or re.match(r"^\s*0\s*,\s*𝜋", t):
            print(f"  y{l['bbox'][1]:7.1f} | {t!r}")
