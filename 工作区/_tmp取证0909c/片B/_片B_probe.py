# -*- coding: utf-8 -*-
"""片B 测量探针 v2（只读；临时产物仅本目录）：四类量——
  A. 条目缝（条目号行对：基线 pitch mm + 600dpi 墨隙 mm）
  B. 条目2 (1)->(2) 拆段缝（同 A 口径）
  C. 判断题缝（[解析]末行 -> 下一题题干：pitch + 墨隙；仅诊断分析块内）
  D. 表组逐格净空（padT/padB/padL/padR，600dpi；行高=线顶-线顶；表头行高）
用法: python _片B_probe.py <main.pdf> [tag]
"""
import json
import os
import re
import sys

import numpy as np
import pymupdf

PT = 72 / 25.4
MARGIN = 17.575 * PT
PAGE_W = 595.276
COLSEP = 9.25 * PT
COLW = (PAGE_W - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = [MARGIN, MARGIN + COLW + COLSEP]
DPI = 600
PXMM = 25.4 / DPI
THR = 128

PDF = sys.argv[1] if len(sys.argv) > 1 else r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
TAG = sys.argv[2] if len(sys.argv) > 2 else 'run'
OUT = os.path.dirname(os.path.abspath(__file__))

doc = pymupdf.open(PDF)
n_pages = len(doc)

lines_of = {}
for pno, page in enumerate(doc, 1):
    ls = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t:
                ls.append({'t': t, 'bb': pymupdf.Rect(ln['bbox']),
                           'base': ln['spans'][0]['origin'][1], 'sps': ln['spans']})
    lines_of[pno] = ls

def col_rows(pno, cl):
    rows = [r for r in lines_of[pno]
            if COLL[cl] - 7 <= r['bb'].x0 < COLL[cl] + COLW + 7]
    rows.sort(key=lambda r: (r['base'], r['bb'].x0))
    return rows

def ink_bands(pno, cl, y0, y1, x0=None, x1=None):
    page = doc[pno - 1]
    x0 = COLL[cl] if x0 is None else x0
    x1 = COLL[cl] + COLW if x1 is None else x1
    clip = pymupdf.Rect(x0, y0, x1, y1)
    pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY, clip=clip)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    has = (a < THR).any(axis=1)
    idx = np.flatnonzero(has)
    if idx.size == 0:
        return []
    bands, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - p > 1:
            bands.append((s, p))
            s = i
        p = i
    bands.append((s, p))
    return [(clip.y0 + a0 * PXMM, clip.y0 + b0 * PXMM) for a0, b0 in bands]

def ink_gap(pno, cl, y_up_base, y_lo_base):
    bs = ink_bands(pno, cl, y_up_base - 1.0, y_lo_base + 1.0)
    best = (-1.0, None)
    for (a0, a1), (b0, b1) in zip(bs, bs[1:]):
        g = b0 - a1
        if g > best[0]:
            best = (g, (a0, a1, b0, b1))
    return max(best[0], 0.0), bs

def pair(pno, cl, up, lo):
    pitch = (lo['base'] - up['base']) / PT
    gap, _ = ink_gap(pno, cl, up['base'], lo['base'])
    return {'p': pno, 'col': cl, 'up': up['t'][:26], 'lo': lo['t'][:26],
            'pitch': round(pitch, 3), 'gap': round(gap, 3)}

# ---------- A 条目缝 ----------
SIG = re.compile(r'^(◆|例1|变式1|\[(?!注意)|【)')
tm_pairs, tm_all = [], []
for pno in range(1, n_pages + 1):
    for cl in (0, 1):
        rows = col_rows(pno, cl)
        kn0 = next((k for k, r in enumerate(rows) if r['t'].startswith('◆知识点')), -1)
        num_idx = [k for k, r in enumerate(rows) if re.match(r'^\d+\.(?!\d)', r['t'])]
        for k1, k2 in zip(num_idx, num_idx[1:]):
            if k1 <= kn0:
                continue
            between = [rows[m]['t'] for m in range(k1 + 1, k2)]
            if any(SIG.match(t) for t in between):
                tm_all.append({'p': pno, 'col': cl, 'from': rows[k1]['t'][:14],
                               'to': rows[k2]['t'][:14], 'skip': 'sig',
                               'between': [t[:18] for t in between]})
                continue
            # 末行：k2 之前最后一条与 k2 不同线（号行碎片同线）
            def same_line(m, k):
                a0, a1, b0, b1 = rows[m]['bb'].y0, rows[m]['bb'].y1, rows[k]['bb'].y0, rows[k]['bb'].y1
                return min(a1, b1) - max(a0, b0) > 0.5 * min(a1 - a0, b1 - b0)
            prev = [m for m in range(k1, k2) if not same_line(m, k2)]
            up = rows[max(prev, key=lambda m: rows[m]['bb'].y1)] if prev else rows[k1]
            rec = pair(pno, cl, up, rows[k2])
            rec['from'] = rows[k1]['t'][:14]
            rec['to'] = rows[k2]['t'][:14]
            rec['between'] = [t[:18] for t in between]
            rec['up'] = up['t'][:26]
            tm_all.append(rec)
            tm_pairs.append(rec)

# ---------- B 条目2 (1)->(2) ----------
split_rec = []
for pno in range(1, n_pages + 1):
    for cl in (0, 1):
        rows = col_rows(pno, cl)
        for k, r in enumerate(rows):
            if '几何表示法' in r['t'] and r['t'].lstrip('（(').startswith('2'):
                up = rows[k - 1] if k else None
                if up:
                    rec = pair(pno, cl, up, r)
                    split_rec.append(rec)

# ---------- C 判断题缝（诊断分析块内：题干 (N) 行对） ----------
zt_pairs = []
for pno in range(1, n_pages + 1):
    for cl in (0, 1):
        rows = col_rows(pno, cl)
        zt_idx = [k for k, r in enumerate(rows) if re.match(r'^\(\d+\)', r['t'])]
        for k1, k2 in zip(zt_idx, zt_idx[1:]):
            between = [rows[m]['t'] for m in range(k1 + 1, k2)]
            if not any(t.startswith('[解析]') for t in between):
                continue
            if any(SIG.match(t) for t in between if not t.startswith('[解析]')):
                continue
            up = rows[k2 - 1]
            if up['bb'].y0 == rows[k2]['bb'].y0:   # 同线碎片
                continue
            rec = pair(pno, cl, up, rows[k2])
            rec['between'] = [t[:18] for t in between]
            zt_pairs.append(rec)

# ---------- D 表组逐格净空 ----------
def rgb255(c):
    return tuple(round(x * 255) for x in c)

def is_rule_color(c):
    return c and (rgb255(c) == (122, 122, 122) or rgb255(c) == (0, 0, 0))

tables = []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    hrs, vrs = [], []
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not is_rule_color(c):
            continue
        if r.width > 15 * PT and r.height < 3:
            hrs.append(r)
        elif r.height > 5 * PT and r.width < 3:
            vrs.append(r)
    # 表横线判据：该线跨越 ≥2 条竖线（竖线 y 范围覆盖线 y）
    def is_table_rule(r):
        n = 0
        for v in vrs:
            if v.y0 - 1 <= r.y0 <= v.y1 + 1 and r.x0 - 1.5 <= v.x0 <= r.x1 + 1.5:
                n += 1
        return n >= 2
    trs = [r for r in hrs if is_table_rule(r)]
    bycol = {}
    for r in trs:
        cl = 0 if (r.x0 + r.x1) / 2 < MID else 1
        bycol.setdefault(cl, []).append(r)
    for cl, lst in bycol.items():
        lst.sort(key=lambda r: r.y0)
        cur = [lst[0]]
        for rd in lst[1:]:
            if rd.y0 - cur[-1].y0 > 60:
                if len(cur) >= 3:
                    tables.append((pno, cl, cur, [v for v in vrs if COLL[cl] - 3 <= v.x0 <= COLL[cl] + COLW + 3]))
                cur = [rd]
            else:
                cur.append(rd)
        if len(cur) >= 3:
            tables.append((pno, cl, cur, [v for v in vrs if COLL[cl] - 3 <= v.x0 <= COLL[cl] + COLW + 3]))

tab_out = []
for pno, cl, rs, vrs in tables:
    page = doc[pno - 1]
    xs = sorted(set(round(v.x0, 2) for v in vrs))
    if len(xs) < 2:
        xs = [rs[0].x0, rs[0].x1]
    xcols = [xs[0]] + xs + [xs[-1]] if len(xs) == 2 else xs
    rec = {'p': pno, 'col': cl,
           'row_heights': [round((b.y0 - a.y0) / PT, 3) for a, b in zip(rs, rs[1:])],
           'head_h': round((rs[1].y0 - rs[0].y0) / PT, 3), 'cells': []}
    for ri in range(len(rs) - 1):
        yy0, yy1 = rs[ri].y0 + 1.6, rs[ri + 1].y0 - 1.6
        if yy1 - yy0 < 3:
            continue
        for ci in range(len(xcols) - 1):
            xx0, xx1 = xcols[ci] + 2.0, xcols[ci + 1] - 2.0
            if xx1 - xx0 < 6:
                continue
            clip = pymupdf.Rect(xx0, yy0, xx1, yy1)
            pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY, clip=clip)
            a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
            dark = a < THR
            if dark.sum() < 30:
                continue
            ys, xs2 = np.where(dark)
            inked = dark.any(axis=1)
            idx = np.flatnonzero(inked)
            nline, prev = 1, idx[0]
            for v in idx[1:]:
                if (v - prev) * PXMM > 0.6:
                    nline += 1
                prev = v
            rec['cells'].append({'r': ri, 'c': ci, 'nline': nline,
                                 'T': round(ys.min() * PXMM, 2),
                                 'B': round((pix.height - 1 - ys.max()) * PXMM, 2),
                                 'L': round(xs2.min() * PXMM, 2),
                                 'R': round((pix.width - 1 - xs2.max()) * PXMM, 2)})
    tab_out.append(rec)

def stat(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return {'n': len(vals), 'min': round(min(vals), 2), 'max': round(max(vals), 2),
            'mean': round(sum(vals) / len(vals), 2)}

summary = {
    'pdf': PDF, 'tag': TAG, 'pages': n_pages,
    'tm': {'pairs': tm_pairs, 'all': tm_all,
           'gap': stat([r['gap'] for r in tm_pairs]),
           'pitch': stat([r['pitch'] for r in tm_pairs])},
    'split12': split_rec,
    'zt': {'pairs': zt_pairs, 'gap': stat([r['gap'] for r in zt_pairs]),
           'pitch': stat([r['pitch'] for r in zt_pairs])},
    'tables': tab_out,
}
with open(os.path.join(OUT, f'probe_{TAG}.json'), 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=1)

print(f'== probe {TAG}  {PDF}  pages={n_pages}')
print('-- 条目缝（条目号行对）--')
for r in tm_pairs:
    print(f"  p{r['p']}c{r['col']} {r['from']:12s}->{r['to']:12s} pitch {r['pitch']:6.2f}mm 墨隙 {r['gap']:5.2f}mm"
          f"  上行={r['up'][:20]}")
if summary['tm']['gap']:
    g = summary['tm']['gap']
    print(f"  条目缝墨隙 n={g['n']} 范围 {g['min']}–{g['max']} 均值 {g['mean']}mm")
print('-- 条目2 (1)->(2) --')
for r in split_rec:
    print(f"  p{r['p']}c{r['col']} pitch {r['pitch']:.2f}mm 墨隙 {r['gap']:.2f}mm")
print('-- 判断题缝 --')
for r in zt_pairs:
    print(f"  p{r['p']}c{r['col']} {r['up'][:20]:20s}->{r['lo'][:20]:20s} pitch {r['pitch']:.2f}mm 墨隙 {r['gap']:.2f}mm")
if summary['zt']['gap']:
    g = summary['zt']['gap']
    print(f"  判断题缝墨隙 n={g['n']} 范围 {g['min']}–{g['max']} 均值 {g['mean']}mm")
print('-- 表组 --')
for t in tab_out:
    print(f"  p{t['p']}c{t['col']} 表头行高 {t['head_h']:.2f}mm 行高 {t['row_heights']}")
    for c in t['cells']:
        print(f"    r{c['r']}c{c['c']} {c['nline']}行 T{c['T']:5.2f} B{c['B']:5.2f} L{c['L']:5.2f} R{c['R']:5.2f}mm")
