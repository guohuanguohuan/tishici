# -*- coding: utf-8 -*-
import pymupdf, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
PDF = "高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf"
doc = pymupdf.open(PDF)
for i in range(5, 40):
    t = doc[i].get_text()
    has = "习题" in t
    head = t[:30].replace("\n", " ")
    print(i + 1, has, repr(head))
