# -*- coding: utf-8 -*-
"""片C：#29 关系号行尾悬挂扫描——正文行末字符 = '='（或 ∥ 矢量）即记一处。
用法：_scan_hang.py <pdf路径> <标签>"""
import sys
import pymupdf

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
            lines.append((ln['bbox'], chars))
    # ∥ 矢量（TikZ 双平行四边形，墨宽 ~8.3pt）
    pars = []
    for d in page.get_drawings():
        if d['fill'] is None:
            continue
        r = pymupdf.Rect(d['rect'])
        if 7.5 < r.width < 9.5 and 8.0 < r.height < 12.0:
            pars.append(r)
    for bb, chars in lines:
        last = chars[-1]
        txt = last['c']
        x1 = last['bbox'][2]
        y0, y1 = bb[1], bb[3]
        if txt == '=':
            hits.append((pno, round(y0, 1), '=', round(x1, 1)))
        # 行末是 ∥ 矢量：∥ 矩形右缘接近行右缘且与行 y 重叠
        for r in pars:
            if abs(r.y0 - y0) < 8 and r.x1 > x1 - 2 and r.x1 <= bb[2] + 3:
                hits.append((pno, round(y0, 1), '∥', round(r.x1, 1)))
print(f'== {label}：关系号行尾悬挂 {len(hits)} 处 ==')
for h in hits:
    print(f'   p{h[0]} y={h[1]} 末符号={h[2]} x={h[3]}')
