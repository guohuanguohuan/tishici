# -*- coding: utf-8 -*-
"""片B 裁片 v2：四意见实测标注图（600dpi，红线标墨缘/线缘，注实测 mm 与全品靶值）。"""
import io
import os

import numpy as np
import pymupdf
from PIL import Image, ImageDraw

PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
OUT = os.path.dirname(os.path.abspath(__file__))
PT = 72 / 25.4
MARGIN = 17.575 * PT
PAGE_W = 595.276
COLSEP = 9.25 * PT
COLW = (PAGE_W - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = [MARGIN, MARGIN + COLW + COLSEP]
DPI = 600
S = DPI / 72.0
PXMM = 25.4 / DPI

doc = pymupdf.open(PDF)
lines_of = {}
for pno, page in enumerate(doc, 1):
    ls = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t:
                ls.append({'t': t, 'bb': pymupdf.Rect(ln['bbox']),
                           'base': ln['spans'][0]['origin'][1]})
    lines_of[pno] = ls


def col_rows(pno, cl):
    rows = [r for r in lines_of[pno] if COLL[cl] - 7 <= r['bb'].x0 < COLL[cl] + COLW + 7]
    rows.sort(key=lambda r: (r['base'], r['bb'].x0))
    return rows


def render(pno, x0, y0, x1, y1):
    page = doc[pno - 1]
    pix = page.get_pixmap(dpi=DPI, clip=pymupdf.Rect(x0, y0, x1, y1))
    return Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')


def annotate_pair(fname, pno, cl, up, lo, title, target):
    x0, x1 = COLL[cl], COLL[cl] + COLW
    y0 = up['base'] - 11
    y1 = lo['base'] + 6
    img = render(pno, x0, y0, x1, y1)
    dr = ImageDraw.Draw(img)
    w, h = img.size
    a = np.asarray(img.convert('L'))
    dark = (a < 128).any(axis=1)

    def band_near(base, lo_pt, hi_pt):
        r0 = max(0, int((base + lo_pt - y0) * S))
        r1 = min(h - 1, int((base + hi_pt - y0) * S))
        idx = [r for r in range(r0, r1 + 1) if dark[r]]
        return (idx[0], idx[-1]) if idx else (None, None)

    u0, u1 = band_near(up['base'], -11, 3)
    l0, l1 = band_near(lo['base'], -11, 3)
    if u1 is not None:
        dr.line([(0, u1), (w, u1)], fill=(220, 0, 0), width=2)
    if l0 is not None:
        dr.line([(0, l0), (w, l0)], fill=(220, 0, 0), width=2)
    pitch = (lo['base'] - up['base']) / PT
    gap = (l0 - u1) * PXMM if (u1 is not None and l0 is not None) else -1
    dr.rectangle([0, 0, w - 1, h - 1], outline=(0, 90, 200), width=2)
    dr.text((10, 6), title, fill=(200, 0, 0))
    dr.text((10, 26), f'pitch {pitch:.2f}mm  ink-gap {gap:.2f}mm', fill=(200, 0, 0))
    dr.text((10, 46), target, fill=(0, 110, 0))
    img.save(os.path.join(OUT, fname))
    return round(pitch, 2), round(gap, 2)


res = {}
# B1 条目2 (1)→(2)
rows = col_rows(1, 0)
kn = next(k for k, r in enumerate(rows) if r['t'].startswith('◆知识点'))
r1 = next(r for r in rows[kn:] if '字母表示法' in r['t'])
r2 = next(r for r in rows[kn:] if '几何表示法' in r['t'])
res['B1'] = annotate_pair('B1_条目2拆段缝.png', 1, 0, r1, r2,
                          'B1 条目2 (1)->(2)  F片B #28', '靶: pitch 6.44 / ink 2.7-3.0mm（全品同段连排）')

# B2 条目缝：条目1[注意]末 → 条目2
i2 = next(k for k, r in enumerate(rows[kn:], kn) if r['t'].startswith('2.'))
up2 = rows[i2 - 1]
res['B2'] = annotate_pair('B2_条目缝.png', 1, 0, up2, rows[i2],
                          'B2 条目1[注意]末->条目2  F片B #36', '靶: ink 3.06±0.2mm（全品 p04/p05）')

# B3 判断题缝
rows3 = col_rows(1, 1)
k2 = next(k for k, r in enumerate(rows3) if r['t'].startswith('(2)') and '相等向量' in r['t'])
res['B3'] = annotate_pair('B3_判断题缝.png', 1, 1, rows3[k2 - 1], rows3[k2],
                          'B3 判断(1)[解析]末->(2)题干  F片B #31', '靶: pitch 6.3-6.8 / ink ≈2.9mm（全品 p04/p05）')

def table_crop(pno, cl, fname, title):
    page = doc[pno - 1]
    hrs = []
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c:
            continue
        if tuple(round(x * 255) for x in c) != (122, 122, 122):
            continue   # 表横线＝灰122；黑线系格内挖空下划线，不入规则线集
        if r.width > 15 * PT and r.height < 3 and cl <= (r.x0 + r.x1) / 2 <= cl + COLW:
            hrs.append((r, (d.get('width') or 0)))
    hrs.sort(key=lambda h: h[0].y0)
    rs = [r for r, _ in hrs]
    ws = [w for _, w in hrs]
    x0, x1 = rs[0].x0 - 3, rs[0].x1 + 3
    y0, y1 = rs[0].y0 - 6, rs[-1].y0 + 8
    img = render(pno, x0, y0, x1, y1)
    dr = ImageDraw.Draw(img)
    w, h = img.size
    for r in rs:
        yy = int((r.y0 - y0) * S)
        dr.line([(0, yy), (w, yy)], fill=(220, 0, 0), width=2)
    head_h = (rs[1].y0 - rs[0].y0) / PT
    vlines = [d['rect'] for d in page.get_drawings()
              if (d.get('color') or d.get('fill'))
              and tuple(round(x * 255) for x in (d.get('color') or d.get('fill'))) == (0, 0, 0)
              and d['rect'].height > 5 * PT and d['rect'].width < 3]
    rows_txt = []
    for ri in range(len(rs) - 1):
        a_, b_, wa, wb = rs[ri], rs[ri + 1], ws[ri], ws[ri + 1]
        xs = sorted(set(round(v.x0, 2) for v in vlines
                        if v.y0 - 1 <= a_.y0 <= v.y1 + 1 or v.y0 - 1 <= b_.y0 <= v.y1 + 1))
        if len(xs) < 2:
            continue
        pT = pB = 99.0
        for xa, xb in zip(xs, xs[1:]):
            if xb - xa < 6:
                continue
            ca = np.asarray(render(pno, xa + 2, a_.y0 + 1.6, xb - 2, b_.y0 - 1.6).convert('L'))
            idx = np.flatnonzero((ca < 128).any(axis=1))
            if idx.size == 0:
                continue
            off = 1.6 * 25.4 / 72.0          # 裁片顶到线中心的 1.6pt（折 mm）
            pT = min(pT, off + idx[0] * PXMM - wa / 2 * 25.4 / 72)
            pB = min(pB, off + (ca.shape[0] - 1 - idx[-1]) * PXMM - wb / 2 * 25.4 / 72)
        if pT > 90:
            continue
        rows_txt.append((ri, round((b_.y0 - a_.y0) / PT, 2), round(pT, 2), round(pB, 2)))
    dr.text((10, 6), title, fill=(200, 0, 0))
    dr.text((10, 26), f'表头行高 {head_h:.2f}mm（靶 9.0±0.3，全品 9.03）', fill=(200, 0, 0))
    k = 0
    for ri, rh, pT, pB in rows_txt:
        if rh < 14:
            continue
        dr.text((10, 46 + k * 20), f'行{ri} 高{rh} 净空 顶{pT}/底{pB}mm（靶 3.5±0.3）', fill=(0, 110, 0))
        k += 1
    img.save(os.path.join(OUT, fname))
    return round(head_h, 2), [r for r in rows_txt if r[1] >= 14]


res['B4'] = table_crop(1, COLL[1], 'B4_表格净空.png', 'B4 表1（p1 右栏）F片B #30')
res['B5'] = table_crop(2, COLL[0], 'B5_表2净空_含单行行.png', 'B5 表2（p2 左栏）含 3 折行与单行行 F片B #30')

print('B1', res['B1'])
print('B2', res['B2'])
print('B3', res['B3'])
print('B4 表头', res['B4'][0], '多行行', res['B4'][1])
