# -*- coding: utf-8 -*-
"""第9题图 精确裁框：union 矢量路径 bbox＋框外文字标号位，出白底清理版位图。"""
import pymupdf, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
OUT = "工作区/M2-第1章量产0911/_tmp装配图债014"
doc = pymupdf.open("高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf")
page = doc[34]
# 图区候选范围（含标号）
region = pymupdf.Rect(400, 600, 550, 765)
union = None
for d in page.get_drawings():
    r = d["rect"]
    if region.contains(pymupdf.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)):
        union = r if union is None else union | r
print("drawings union:", union)
# 标号文字 bbox 并入（A₁/A/B₁/B/C₁/C/D₁/D/O/x/y/z/P）
labels = pymupdf.Rect()
for needle in ("A", "B", "C", "D", "O", "x", "y", "z", "P", "１"):
    for r in page.search_for(needle):
        if region.contains(pymupdf.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)):
            labels |= r
print("labels union:", labels)
full = union | labels
print("figure bbox:", full)
# 外扩 3pt 出图
box = pymupdf.Rect(full.x0 - 3, full.y0 - 3, full.x1 + 3, full.y1 + 3)
pix = page.get_pixmap(dpi=400, clip=box)
p1 = os.path.join(OUT, "b9_原样.png")
pix.save(p1)
print("saved", p1, pix.width, pix.height)
