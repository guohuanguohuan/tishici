# -*- coding: utf-8 -*-
"""main.pdf → png/pNN.png（150dpi，pymupdf 渲染）——测评卷 v4 render.py 拷贝改造，路径改演示波④滚动小卷。
模板坑 #8：调用前先清空 png/（本脚本自带清空逻辑）。"""
import os
import glob
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\演示\滚动小卷"
for old in glob.glob(BASE + r"\png\p*.png"):
    os.remove(old)
os.makedirs(BASE + r"\png", exist_ok=True)
doc = pymupdf.open(BASE + r"\main.pdf")
for i, page in enumerate(doc, 1):
    pix = page.get_pixmap(dpi=150)
    pix.save(BASE + rf"\png\p{i:02d}.png")
print(f'{len(doc)} pages rendered to png/ at 150dpi')
