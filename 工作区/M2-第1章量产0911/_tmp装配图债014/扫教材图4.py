# -*- coding: utf-8 -*-
import pymupdf, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
doc = pymupdf.open("高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf")
# 打印 PDF 页 30、31 全文（printed 23/24：1.1.3 练习/习题1—1 区），找 B·9
for i in (29, 30, 31, 32):
    t = doc[i].get_text()
    print("=" * 20, "PDF page", i + 1, "=" * 20)
    print(t[:1800])
