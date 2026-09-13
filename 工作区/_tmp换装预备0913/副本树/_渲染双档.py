# -*- coding: utf-8 -*-
"""试迁双档渲染：pdf → 指定 png 目录（150dpi，口径同 render.py）。用法：python _渲染双档.py"""
import os, sys
import fitz

BASE = os.path.dirname(os.path.abspath(__file__))
JOBS = [(os.path.join(BASE, "导学件", "课时01", "main-true.pdf"),
         os.path.join(BASE, "导学件", "课时01", "png-true")),
        (os.path.join(BASE, "导学件", "课时01", "main-pure.pdf"),
         os.path.join(BASE, "导学件", "课时01", "png-pure"))]
for src, out in JOBS:
    os.makedirs(out, exist_ok=True)
    doc = fitz.open(src)
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=150)
        pix.save(os.path.join(out, "page%d.png" % i))
    print(out, "->", len(doc), "pages")
