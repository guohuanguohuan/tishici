# -*- coding: utf-8 -*-
"""main.pdf → png/pageN.png（150dpi，pymupdf 渲染）——导学件 render.py 拷贝改造，路径改演示波④章末总结。
模板坑 #8：渲染前先清空 png/（防旧版残留混入目检清单）。"""
import os
import glob
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(BASE, 'main.pdf')
out = os.path.join(BASE, 'png')
os.makedirs(out, exist_ok=True)
n_old = 0
for p in glob.glob(os.path.join(out, 'page*.png')):
    os.remove(p)
    n_old += 1
print(f'cleared {n_old} old page*.png')
doc = pymupdf.open(src)
for i, page in enumerate(doc, 1):
    pix = page.get_pixmap(dpi=150)
    path = os.path.join(out, f'page{i}.png')
    pix.save(path)
    print(path, pix.width, 'x', pix.height)
print('total', len(doc), 'pages')
