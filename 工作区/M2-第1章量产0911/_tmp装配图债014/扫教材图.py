# -*- coding: utf-8 -*-
"""拓-020 图债处置：教材 习题1—1B·9 原图回源提取（装配轮 2026-09-12）
扫描 人教B选择性必修1.pdf 找 习题1—1B·9 页与图块，裁位图存 成卷/装配/图债回源/。
"""
import pymupdf, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
PDF = "高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf"
doc = pymupdf.open(PDF)
print("pages:", len(doc))
for i in range(5, 40):
    t = doc[i].get_text()
    if "习题" in t:
        j = t.find("习题")
        print("=== PDF page", i + 1, "===")
        print(t[max(0, j - 30):j + 150].replace("\n", " | "))
