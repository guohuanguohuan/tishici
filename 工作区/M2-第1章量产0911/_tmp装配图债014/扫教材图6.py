# -*- coding: utf-8 -*-
import pymupdf, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
doc = pymupdf.open("高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf")
for i in (34,):
    t = doc[i].get_text()
    print("=" * 20, "PDF page", i + 1, "=" * 20)
    print(t)
    print("images:", [ (im[0], im[2], im[3]) for im in doc[i].get_images() ])
