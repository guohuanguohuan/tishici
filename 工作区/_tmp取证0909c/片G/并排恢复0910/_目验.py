# -*- coding: utf-8 -*-
"""并排恢复0910 目验片：p3 两条并排带（g1/g2）＋各自下邻通栏行，400dpi 裁图存证。"""
import os
import pymupdf

BASE = r'C:\提示词\工作区\字替对照-0909\variantF'
OUT = os.path.dirname(os.path.abspath(__file__))
doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
pg = doc[2]
ZONES = {'g1带': (300, 175, 552, 345), 'g2带': (300, 600, 552, 730)}
for nm, (x0, y0, x1, y1) in ZONES.items():
    pm = pg.get_pixmap(dpi=400, clip=pymupdf.Rect(x0, y0, x1, y1))
    p = os.path.join(OUT, f'目验_{nm}.png')
    pm.save(p)
    print(p, pm.width, pm.height)
