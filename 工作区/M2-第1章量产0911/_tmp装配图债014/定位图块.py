# -*- coding: utf-8 -*-
"""定位 教材 printed p28（PDF p35）第9题图块 bbox，整页与裁图各出一张供目验。"""
import pymupdf, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
doc = pymupdf.open("高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf")
page = doc[34]
print("page rect:", page.rect)
# 找关键文字块位置
for needle in ("（第９题）", "（第9题）", "O", "x", "y", "z", "P"):
    hits = page.search_for(needle)
    print(needle, "->", [tuple(round(v, 1) for v in r) for r in hits][:6])
