# -*- coding: utf-8 -*-
import pymupdf, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
doc = pymupdf.open("高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf")
for i in range(18, 37):
    t = doc[i].get_text()
    if "正方体" in t or "如图" in t:
        print("=== PDF page", i + 1, "===")
        for k, seg in enumerate(t.split("\n")):
            if "正方体" in seg or "如图" in seg or "犘" in seg:
                print("  ", seg.strip()[:90])
