# -*- coding: utf-8 -*-
"""一次性探针：N4 p1 表顶上方 263.76-268.08 带的身份（drawings/文本全查）。"""
import os

import pymupdf

BASE = r'C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件'
PT = 72 / 25.4
doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
page = doc[0]

print('==== p1 y∈[255,281]pt 全部 drawings ====')
for d in page.get_drawings():
    r = d['rect']
    if r.y1 > 255 and r.y0 < 281:
        c = d.get('color') or d.get('fill')
        c255 = tuple(round(x * 255) for x in c) if c else None
        print(f'  type={d["type"]} rect=({r.x0:.2f},{r.y0:.2f},{r.x1:.2f},{r.y1:.2f}) '
              f'w={r.width / PT:.1f}mm h={r.height / PT:.2f}mm color={c255} sw={d.get("width")}')

print('==== p1 y∈[240,281]pt 全部文本行（全宽） ====')
for blk in page.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        bb = ln['bbox']
        if bb[3] > 240 and bb[1] < 281:
            t = ''.join(sp['text'] for sp in ln['spans'])
            fonts = {sp['font'] for sp in ln['spans']}
            print(f'  y[{bb[1]:.2f},{bb[3]:.2f}] x[{bb[0]:.2f},{bb[2]:.2f}] {t[:40]!r} {fonts}')
