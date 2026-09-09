# -*- coding: utf-8 -*-
"""片C：#29 关系号行尾悬挂扫描 v3——'=' 右侧同线还有任何墨（文字/线/图）即非悬挂。
用法：_scan_hang3.py <pdf路径> <标签>"""
import sys
import pymupdf

PT = 72 / 25.4
MARGIN = 17.575 * PT
COLSEP = 9.25 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
RIGHTS = (MARGIN + COLW, 595.276 - MARGIN)

pdf = sys.argv[1]
label = sys.argv[2]
doc = pymupdf.open(pdf)
hits = []
for pno, page in enumerate(doc, 1):
    raw = page.get_text('rawdict')
    # 所有文字 char（含各片段）
    allchars = []
    for blk in raw['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk['lines']:
            for sp in ln['spans']:
                for ch in sp['chars']:
                    allchars.append(ch)
    draws = [pymupdf.Rect(d['rect']) for d in page.get_drawings()]
    imgs = [page.get_image_rects(i[0]) for i in page.get_images(full=True)]
    imgs = [r for sub in imgs for r in sub]
    for ch in allchars:
        if ch['c'] != '=':
            continue
        bb = pymupdf.Rect(ch['bbox'])
        yc = (bb.y0 + bb.y1) / 2
        # 同线右侧是否还有墨
        right_text = [c for c in allchars if c is not ch and c['bbox'][0] > bb.x1 + 0.5
                      and c['bbox'][1] < bb.y1 - 1 and c['bbox'][3] > bb.y0 + 1]
        right_draw = [r for r in draws if r.x0 > bb.x1 + 0.5 and r.y0 < bb.y1 - 1 and r.y1 > bb.y0 + 1]
        right_img = [r for r in imgs if r.x0 > bb.x1 + 0.5 and r.y0 < bb.y1 and r.y1 > bb.y0]
        if not right_text and not right_draw and not right_img:
            hits.append((pno, round(bb.y0, 1), round(bb.x1, 1)))
print(f'== {label}：真悬挂（= 右侧无墨）{len(hits)} 处 ==')
for h in hits:
    print(f'   p{h[0]} y={h[1]} x={h[2]}')
