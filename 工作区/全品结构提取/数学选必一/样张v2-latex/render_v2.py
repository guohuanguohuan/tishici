# -*- coding: utf-8 -*-
"""main_v2.pdf → png_v2/pNN.png（150dpi，pymupdf 渲染）"""
import os
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v2-latex"
os.makedirs(BASE + r"\png_v2", exist_ok=True)
doc = pymupdf.open(BASE + r"\main_v2.pdf")
for i, page in enumerate(doc, 1):
    pix = page.get_pixmap(dpi=150)
    pix.save(BASE + rf"\png_v2\p{i:02d}.png")
print(f'{len(doc)} pages rendered to png_v2/ at 150dpi')
