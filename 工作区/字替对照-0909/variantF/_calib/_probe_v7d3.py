# -*- coding: utf-8 -*-
import re, os
import pymupdf
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PT = 72 / 25.4
MARGIN = 17.575 * PT
PAGE_W = 595.0
COLSEP = 9.25 * PT
COLW = (PAGE_W - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = [MARGIN, MARGIN + COLW + COLSEP]
doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
lines_of = {}
for pno, page in enumerate(doc, 1):
    ls = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t:
                ls.append((t, ln['bbox'], ln['spans']))
    lines_of[pno] = ls

print('==== P. p1 base 545-560 区全部行（判断(1) 题干在哪） ====')
for t, bb, sps in lines_of[1]:
    o = sps[0]['origin'][1]
    if 544 <= o <= 562:
        print(f'base={o:.2f} x0={bb[0]:.1f} x1={bb[2]:.1f} {t!r}')
print('---- p2/p3 变式行（含「变式」任意位置） ----')
for pno in (2, 3):
    for t, bb, sps in lines_of[pno]:
        if '变式' in t:
            print(f'p{pno} y={bb[1]:.0f} x0={bb[0]:.1f} 首span字号={sps[0]["size"]:.2f} {t[:30]!r}')
print('---- p2 y60-140 全行（探二 变式1 区域） ----')
for t, bb, sps in lines_of[2]:
    if 55 <= bb[1] <= 150:
        print(f'y={bb[1]:.1f} x0={bb[0]:.1f} {t[:44]!r}')

print('==== Q. g_tm 复算 v2（_sig_t 排除 [注意]） ====')
def col_rows(pno, cl):
    rows = []
    for t, bb, sps in lines_of[pno]:
        if cl - 7 <= bb[0] < cl + COLW + 7:
            rows.append((bb[1], bb[3], t, sps))
    rows.sort(key=lambda x: x[0])
    return rows
def bandsov(page, x0, x1, y0, y1, thresh=128, dpi=150):
    y0 = max(MARGIN - 3, y0); y1 = min(842.0, y1)
    if y1 - y0 < 1:
        return []
    sc = dpi / 72.0
    pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(x0, y0, x1, y1))
    w, h, s = pm.width, pm.height, pm.samples
    rr = [any(s[r_ * w + c] < thresh for c in range(w)) for r_ in range(h)]
    out, st = [], None
    for i, d in enumerate(rr):
        if d and st is None: st = i
        elif not d and st is not None:
            out.append((y0 + st / sc, y0 + i / sc)); st = None
    if st is not None:
        out.append((y0 + st / sc, y0 + h / sc))
    return out
def merge(bs, gap=0.5):
    out = []
    for a, b in bs:
        if out and a - out[-1][1] < gap: out[-1] = (out[-1][0], b)
        else: out.append((a, b))
    return out
BOT = 842.0 - 48.2
def _sig2(t):
    return bool(re.match(r'^(◆|例1|变式1|\[(?!注意)|【)', t))
def _same_line(m, k, rows):
    a0, a1, b0, b1 = rows[m][0], rows[m][1], rows[k][0], rows[k][1]
    return min(a1, b1) - max(a0, b0) > 0.5 * min(a1 - a0, b1 - b0)
g_tm = []
for pno in range(1, 8):
    for cl in COLL:
        bs = merge(bandsov(doc[pno - 1], cl, cl + COLW, MARGIN, BOT), gap=0.8)
        rows = col_rows(pno, cl)
        if not bs or not rows:
            continue
        kn0 = next((k for k, (_y0, _y1, t, _s) in enumerate(rows) if t.startswith('◆知识点')), -1)
        num_rows = [k for k, (y0_, y1_, t, _sps) in enumerate(rows) if re.match(r'^\d+\.(?!\d)', t)]
        for k1, k2 in zip(num_rows, num_rows[1:]):
            if k1 <= kn0:
                continue
            sigs = [rows[m][2][:8] for m in range(k1 + 1, k2) if _sig2(rows[m][2])]
            if sigs:
                print(f'p{pno} 对({rows[k1][2][:4]!r},{rows[k2][2][:4]!r}) 仍跳: {sigs[:2]}')
                continue
            prev = [m for m in range(k1, k2) if not _same_line(m, k2, rows)]
            last = max(prev, key=lambda m: rows[m][1]) if prev else k1
            def bat(rr_):
                for i, (a, b) in enumerate(bs):
                    if min(b, rr_[1]) - max(a, rr_[0]) > 0:
                        return i
                return -1
            bj, bi = bat(rows[k2]), bat(rows[last])
            if bj > bi >= 0:
                g_tm.append((bs[bj][0] - bs[bi][1]) / PT)
                print(f'p{pno} 入集对({rows[k1][2][:4]!r},{rows[k2][2][:4]!r}) 缝={(bs[bj][0] - bs[bi][1]) / PT:.2f}')
            else:
                print(f'p{pno} 同带/异常对({rows[k1][2][:4]!r},{rows[k2][2][:4]!r}) bj={bj} bi={bi}')
print(f'g_tm n={len(g_tm)} 值={["%.2f" % v for v in g_tm]}')

print('==== R. ④ 复算 v2（去空格归并） ====')
_grp = {}
for pno in range(1, 8):
    for t, bb, sps in lines_of[pno]:
        base = sps[0]['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _grp.setdefault((pno, cl, round(base * 2)), []).append((bb[0], t))
n_hang = n_alone = 0
for k, frs in sorted(_grp.items()):
    frs.sort()
    mt = ''.join(x[1] for x in frs).replace(' ', '')
    n_par = mt.count('(√)') + mt.count('(×)')
    if not n_par:
        continue
    solo = all(x[1].replace(' ', '') in ('(√)', '(×)') for x in frs)
    if solo:
        n_alone += n_par
        print(f'独占组 {k} {[x[1] for x in frs]!r}')
    else:
        n_hang += n_par
print(f'右挂={n_hang} 独占={n_alone}')
print('==== 完 ====')
