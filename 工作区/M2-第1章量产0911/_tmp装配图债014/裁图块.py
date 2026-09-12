# -*- coding: utf-8 -*-
"""裁 第9题图：先出整页缩览＋粗裁图两件供目验，再定最终裁框。"""
import pymupdf, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
OUT = "工作区/M2-第1章量产0911/_tmp装配图债014"
os.makedirs(OUT, exist_ok=True)
doc = pymupdf.open("高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf")
page = doc[34]
# 整页右下区粗裁（含全部顶点标号）
clip = pymupdf.Rect(395, 545, 560, 770)
pix = page.get_pixmap(dpi=300, clip=clip)
pix.save(os.path.join(OUT, "b9_粗裁.png"))
print("saved 粗裁", pix.width, pix.height)
# 高位细看：全页
pix2 = page.get_pixmap(dpi=110)
pix2.save(os.path.join(OUT, "p28_整页.png"))
print("saved 整页", pix2.width, pix2.height)
