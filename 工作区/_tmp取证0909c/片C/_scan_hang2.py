# -*- coding: utf-8 -*-
"""片C：#29 关系号行尾悬挂扫描 v2——只认真正行尾（行片段右缘贴栏右 284.5/545.5±2pt）。
用法：_scan_hang2.py <pdf路径> <标签>"""
import sys
import pymupdf

PT = 72 / 25.4
MARGIN = 17.575 * PT
COLSEP = 9.25 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
RIGHTS = (MARGIN + COLW, 595.276 - MARGIN)   # 284.5 / 545.5

pdf = sys.argv[1]
label = sys.argv[2]
doc = pymupdf.open(pdf)
hits = []
for pno, page in enumerate(doc, 1):
    raw = page.get_text('rawdict')
    lines = []
    for blk in raw['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk['lines']:
            chars = [ch for sp in ln['spans'] for ch in sp['chars']]
            if not chars:
                continue
            chars.sort(key=lambda ch: ch['bbox'][0])
            lines.append((pymupdf.Rect(ln['bbox']), chars))
    pars = []
    for d in page.get_drawings():
        if d['fill'] is None:
            continue
        r = pymupdf.Rect(d['rect'])
        if 7.5 < r.width < 9.5 and 8.0 < r.height < 12.0:
            pars.append(r)
    for bb, chars in lines:
        right = min(RIGHTS, key=lambda c: abs(bb.x0 + COLW / 2 - c))  # 该行所属栏右缘
        if bb.x1 < right - 2.5:      # 行片段未到行尾，弃
            continue
        last = chars[-1]
        if last['c'] == '=' and last['bbox'][2] >= right - 2.5:
            hits.append((pno, round(bb.y0, 1), '=', round(last['bbox'][2], 1)))
        for r in pars:
            if abs(r.y0 - bb.y0) < 8 and r.x1 >= right - 2.5:
                hits.append((pno, round(bb.y0, 1), '∥', round(r.x1, 1)))
print(f'== {label}：真行尾关系号悬挂 {len(hits)} 处 ==')
for h in hits:
    print(f'   p{h[0]} y={h[1]} 末符号={h[2]} x={h[3]}')
