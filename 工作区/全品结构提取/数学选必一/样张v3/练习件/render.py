# -*- coding: utf-8 -*-
"""main.pdf → png/（150dpi），供逐页目检与断言。"""
import os
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(BASE, 'main.pdf')
out = os.path.join(BASE, 'png')
os.makedirs(out, exist_ok=True)
doc = pymupdf.open(src)
for i, page in enumerate(doc, 1):
    pix = page.get_pixmap(dpi=150)
    path = os.path.join(out, f'page{i}.png')
    pix.save(path)
    print(path, pix.width, 'x', pix.height)
print('total', len(doc), 'pages')
