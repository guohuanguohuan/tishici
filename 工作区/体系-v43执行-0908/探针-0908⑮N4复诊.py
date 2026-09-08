# -*- coding: utf-8 -*-
"""一次性探针：⑮ 诊断头整行文本形态 ＋ N4 p1/p2 表顶前距带谱（何带为末带、上邻文本是谁）。"""
import os

import pymupdf

BASE = r'C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件'
PT = 72 / 25.4
MARGIN = 15 * PT
PAGE_W = 595.276
COLSEP = 7.5 * PT
COLW = (PAGE_W - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = [MARGIN, MARGIN + COLW + COLSEP]

doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))

print('==== ⑮ 诊断头整行文本 ====')
for pno in (1, 2, 3):
    for blk in doc[pno - 1].get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t.startswith('【诊断分析】'):
                print(f'p{pno}', repr(t), '尾3字:', repr(t[-3:]), '尾括号:', t.endswith('）'), t.endswith(')'))


def bands(page, x0, x1, y0, y1, thresh=128, dpi=150):
    sc = dpi / 72.0
    pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY,
                         clip=pymupdf.Rect(x0, y0, x1, y1))
    w, h, s = pm.width, pm.height, pm.samples
    rows = [any(s[r * w + c] < thresh for c in range(w)) for r in range(h)]
    out, st = [], None
    for i, d in enumerate(rows):
        if d and st is None:
            st = i
        elif not d and st is not None:
            out.append((y0 + st / sc, y0 + i / sc))
            st = None
    if st is not None:
        out.append((y0 + st / sc, y0 + h / sc))
    return out


def merge(bs, gap=0.5):
    out = []
    for a, b in bs:
        if out and a - out[-1][1] < gap:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


print('==== N4 表顶前距带谱 ====')
for pno in (1, 2):
    page = doc[pno - 1]
    hrs = []
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if c and tuple(round(x * 255) for x in c) == (122, 122, 122) \
                and r.width > 15 * PT and r.height < 3:
            hrs.append(r)
    hrs.sort(key=lambda r: r.y0)
    r0 = hrs[0]
    cl = COLL[0] if (r0.x0 + r0.x1) / 2 < MID else COLL[1]
    side = 'L' if cl == COLL[0] else 'R'
    print(f'--- p{pno} 表顶 y0={r0.y0:.2f}pt 列{side} 横线{len(hrs)}条')
    for tail in (0.3, 1.2):
        bs = merge(bands(page, cl, cl + COLW, r0.y0 - 16, r0.y0 - tail))
        tpre = (r0.y0 - bs[-1][1]) / PT if bs else None
        print(f'  clip尾−{tail}pt: 带谱{[(round(a, 2), round(b, 2)) for a, b in bs]} 前距{tpre}')
    print('  上邻文本行（表顶上方16mm内、同列）:')
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            bb = ln['bbox']
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t and bb[3] > r0.y0 - 16 * PT and bb[3] < r0.y0 and cl - 7 <= bb[0] < cl + COLW + 7:
                print(f'    y[{bb[1]:.2f},{bb[3]:.2f}] x0={bb[0]:.2f} {t[:30]!r}')
