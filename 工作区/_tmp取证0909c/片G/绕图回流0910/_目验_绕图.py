# -*- coding: utf-8 -*-
"""400dpi 裁片目验器（绕图回流0911）：p3 右栏 g1 带／g2 带各出一张 400dpi 裁片。
用法：_目验_绕图.py <输出目录前缀>（产出 目验_g1带.png／目验_g2带.png）"""
import os
import sys

import pymupdf

BASE = r'C:/提示词/工作区/字替对照-0909/variantF'
OUT = sys.argv[1]
PT = 72 / 25.4
COLL1 = 108.8                       # 右栏左缘（mm，实测）
COLW = 84.0                         # 栏宽 mm
ZONES = {'目验_g1带.png': (58.0, 128.0), '目验_g2带.png': (206.0, 262.0)}
doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
pg = doc[2]                          # p3
os.makedirs(OUT, exist_ok=True)
for name, (y0, y1) in ZONES.items():
    clip = pymupdf.Rect((COLL1 - 2) * PT, y0 * PT, (COLL1 + COLW + 2) * PT, y1 * PT)
    pm = pg.get_pixmap(dpi=400, clip=clip)
    pm.save(os.path.join(OUT, name))
    print(name, pm.width, 'x', pm.height, '->', os.path.join(OUT, name))
