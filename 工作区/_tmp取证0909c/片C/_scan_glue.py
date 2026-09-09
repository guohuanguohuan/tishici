# -*- coding: utf-8 -*-
"""片C #29 验证：全书 = / ∥ 两侧 advance 胶宽统计（拉伸实例＝单侧 >1.2mm，B组同口径）。
用法：_scan_glue.py <pdf> <标签>"""
import sys
import pymupdf

PTMM = 72 / 25.4
pdf, label = sys.argv[1], sys.argv[2]
doc = pymupdf.open(pdf)
eq_all, eq_stretch = [], []
par_all, par_stretch = [], []
for pno, page in enumerate(doc, 1):
    raw = page.get_text('rawdict')
    chars = []
    for blk in raw['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk['lines']:
            for sp in ln['spans']:
                for ch in sp['chars']:
                    chars.append(ch)
    # = 的左右相邻 char（按同一行：y 重叠 >60%）
    for i, ch in enumerate(chars):
        if ch['c'] != '=':
            continue
        r = pymupdf.Rect(ch['bbox'])
        yc = (r.y0 + r.y1) / 2
        same = [c for c in chars if c is not ch and c['bbox'][1] < yc < c['bbox'][3]]
        lefts = [c for c in same if c['bbox'][2] <= r.x0 + 0.5]
        rights = [c for c in same if c['bbox'][0] >= r.x1 - 0.5]
        gl = (r.x0 - max(lefts, key=lambda c: c['bbox'][2])['bbox'][2]) / PTMM if lefts else None
        gr = (min(rights, key=lambda c: c['bbox'][0])['bbox'][0] - r.x1) / PTMM if rights else None
        if gl is None or gr is None:
            continue
        eq_all.append((gl, gr))
        if max(gl, gr) > 1.2:
            eq_stretch.append((pno, round(r.y0, 1), round(gl, 3), round(gr, 3)))
    # ∥ 矢量（TikZ 双平行四边形合并）
    strokes = []
    for d in page.get_drawings():
        if d['fill'] is None:
            continue
        rr = pymupdf.Rect(d['rect'])
        if 7.5 < rr.width < 9.5 and 8.0 < rr.height < 12.0:
            strokes.append(rr)
    used = [False] * len(strokes)
    pairs = []
    for i, a in enumerate(strokes):
        if used[i]:
            continue
        for j in range(i + 1, len(strokes)):
            b = strokes[j]
            if used[j]:
                continue
            if abs(a.y0 - b.y0) < 1 and 2 < b.x0 - a.x0 < 5.5:
                pairs.append(pymupdf.Rect(min(a.x0, b.x0), a.y0, max(a.x1, b.x1), a.y1))
                used[i] = used[j] = True
                break
    for pr in pairs:
        yc = (pr.y0 + pr.y1) / 2
        cand = [c for c in chars if c['bbox'][1] < yc + 7 and c['bbox'][3] > yc - 7]
        lefts = [c for c in cand if c['bbox'][2] <= pr.x0 + 1 and c['bbox'][0] >= pr.x0 - 30]
        rights = [c for c in cand if c['bbox'][0] >= pr.x1 - 1 and c['bbox'][0] <= pr.x1 + 30]
        gl = (pr.x0 - max(lefts, key=lambda c: c['bbox'][2])['bbox'][2]) / PTMM if lefts else None
        gr = (min(rights, key=lambda c: c['bbox'][0])['bbox'][0] - pr.x1) / PTMM if rights else None
        if gl is None or gr is None:
            continue
        par_all.append((gl, gr))
        if max(gl, gr) > 1.2:
            par_stretch.append((pno, round(pr.y0, 1), round(gl, 3), round(gr, 3)))
print(f'== {label} ==')
print(f'= 实例 {len(eq_all)}，拉伸 {len(eq_stretch)}；∥ 实例 {len(par_all)}，拉伸 {len(par_stretch)}')
for tag, arr in (('=', eq_all), ('∥', par_all)):
    if arr:
        vals = sorted(v for g in arr for v in g)
        print(f'  {tag} 单侧胶宽 min {vals[0]:.3f} 中位 {vals[len(vals)//2]:.3f} max {vals[-1]:.3f} mm')
for h in eq_stretch:
    print(f'  = 拉伸 p{h[0]} y={h[1]} L={h[2]} R={h[3]}')
for h in par_stretch:
    print(f'  ∥ 拉伸 p{h[0]} y={h[1]} L={h[2]} R={h[3]}')
