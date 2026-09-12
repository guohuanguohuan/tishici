# -*- coding: utf-8 -*-
"""main.pdf → png/pageN.png（150dpi）；口径同 ../variantF/render.py（渲染前清空旧 page*.png）。"""
import os
import glob
import fitz  # pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(BASE, 'main.pdf')
out = os.path.join(BASE, 'png')
os.makedirs(out, exist_ok=True)
for p in glob.glob(os.path.join(out, 'page*.png')):
    os.remove(p)
doc = fitz.open(src)
for i, page in enumerate(doc, 1):
    pix = page.get_pixmap(dpi=150)
    path = os.path.join(out, f'page{i}.png')
    pix.save(path)
    print(path, pix.width, 'x', pix.height)
print('total', len(doc), 'pages')
