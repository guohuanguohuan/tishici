# -*- coding: utf-8 -*-
"""main.pdf → png/（150dpi），供逐页目检与断言。渲染前先清空 png/（防旧版残留混入目检清单）。"""
import os
import glob
import fitz  # pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(BASE, 'main.pdf')
out = os.path.join(BASE, 'png')
os.makedirs(out, exist_ok=True)
n_old = 0
for p in glob.glob(os.path.join(out, 'page*.png')):
    os.remove(p)
    n_old += 1
print(f'cleared {n_old} old page*.png')
doc = fitz.open(src)
for i, page in enumerate(doc, 1):
    pix = page.get_pixmap(dpi=150)
    path = os.path.join(out, f'page{i}.png')
    pix.save(path)
    print(path, pix.width, 'x', pix.height)
print('total', len(doc), 'pages')
