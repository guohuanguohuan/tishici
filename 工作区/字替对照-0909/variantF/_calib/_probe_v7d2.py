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
DPI = 150
SC = DPI / 72.0
doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
lines_of, chars_of = {}, {}
for pno, page in enumerate(doc, 1):
    ls, cs = [], []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t:
                ls.append((t, ln['bbox'], ln['spans']))
    for blk in page.get_text('rawdict')['blocks']:
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                for ch in sp['chars']:
                    cs.append((ch['c'], ch['bbox'], sp['size'], sp['font']))
    lines_of[pno] = ls
    chars_of[pno] = cs

print('==== K. 全 7 页 判断括号行 + 同基线组 ====')
n_all = 0
for pno in range(1, 8):
    for t, bb, sps in lines_of[pno]:
        if re.search(r'\(\s*[√×]\s*\)$', t):
            n_all += 1
            base = sps[0]['origin'][1]
            cl = COLL[0] if bb[0] < MID else COLL[1]
            mates = [(x['bbox'][0], ''.join(s['text'] for s in l['spans']))
                     for tt, lbb, lsp in lines_of[pno] if lsp
                     for x in [lsp[0]] if abs(lsp[0]['origin'][1] - base) < 0.3
                     for l in [{'spans': lsp}]]
            print(f'p{pno} {t!r} base={base:.2f} x0={bb[0]:.1f}')
print(f'括号答案行总数={n_all}')
print('---- 同基线共行 mates（判断行所在视觉行的全部片段） ----')
for pno in range(1, 8):
    for t, bb, sps in lines_of[pno]:
        if re.search(r'\(\s*[√×]\s*\)$', t):
            base = sps[0]['origin'][1]
            cl = COLL[0] if bb[0] < MID else COLL[1]
            same = [(x0, tt) for tt, lbb, lsp in lines_of[pno]
                    if abs(lsp[0]['origin'][1] - base) < 0.6
                    and (COLL[0] if lbb[0] < MID else COLL[1]) == cl
                    for x0 in [lbb[0]]]
            print(f'p{pno} base{base:.1f}: {[tt for _, tt in sorted(same)]}')

print('==== L. 条目缝 g_tm 复算（带跳过原因） ====')
def col_rows(pno, cl):
    rows = []
    for t, bb, sps in lines_of[pno]:
        if cl - 7 <= bb[0] < cl + COLW + 7:
            rows.append((bb[1], bb[3], t, sps))
    rows.sort(key=lambda x: x[0])
    return rows
def bandsov(page, x0, x1, y0, y1, thresh=128, dpi=DPI):
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
def _sig_t(t):
    return bool(re.match(r'^(◆|例1|变式1|\[|【)', t))
def _same_line(m, k, rows):
    a0, a1, b0, b1 = rows[m][0], rows[m][1], rows[k][0], rows[k][1]
    return min(a1, b1) - max(a0, b0) > 0.5 * min(a1 - a0, b1 - b0)
for pno in range(1, 8):
    for cl in COLL:
        bs = merge(bandsov(doc[pno - 1], cl, cl + COLW, MARGIN, 842.0 - 48.2), gap=0.8)
        rows = col_rows(pno, cl)
        if not bs or not rows:
            continue
        kn0 = next((k for k, (_y0, _y1, t, _s) in enumerate(rows) if t.startswith('◆知识点')), -1)
        num_rows = [k for k, (y0_, y1_, t, _sps) in enumerate(rows) if re.match(r'^\d+\.(?!\d)', t)]
        for k1, k2 in zip(num_rows, num_rows[1:]):
            why = []
            if k1 <= kn0:
                why.append('k1<=kn0(学习目标域)')
            sigs = [rows[m][2][:10] for m in range(k1 + 1, k2) if _sig_t(rows[m][2])]
            if sigs:
                why.append(f'跨段签名{sigs[:2]}')
            if not why:
                prev = [m for m in range(k1, k2) if not _same_line(m, k2, rows)]
                last = max(prev, key=lambda m: rows[m][1]) if prev else k1
                bj = next((i for i, (a, b) in enumerate(bs) if min(b, rows[k2][1]) - max(a, rows[k2][0]) > 0), -1)
                bi = next((i for i, (a, b) in enumerate(bs) if min(b, rows[last][1]) - max(a, rows[last][0]) > 0), -1)
                g = (bs[bj][0] - bs[bi][1]) / PT if bj > bi >= 0 else -9
                print(f'p{pno} cl{cl:.0f} 对({rows[k1][2][:6]!r}@y{rows[k1][0]:.0f},{rows[k2][2][:6]!r}@y{rows[k2][0]:.0f}) 缝={g:.2f} bj={bj} bi={bi}')
            else:
                print(f'p{pno} cl{cl:.0f} 对({rows[k1][2][:6]!r},{rows[k2][2][:6]!r}) 跳过: {why[0]}')

print('==== M. 正文 CJK 密度基值（10-11pt FZSSJW） ====')
def dens(pno, bb):
    pm = doc[pno - 1].get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,
                                 clip=pymupdf.Rect(bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1))
    w, h, s = pm.width, pm.height, pm.samples
    dk = sum(255 - v for v in s if v < 200)
    return dk / max(1, (bb[2] - bb[0]) * (bb[3] - bb[1])) * 1000
cd = [dens(pno, bb) for pno in range(1, 8) for c, bb, sz, fn in chars_of[pno]
      if 0x4E00 <= ord(c) <= 0x9FFF and 10 <= sz <= 11 and 'FZSSJW' in fn]
cd.sort()
print(f'n={len(cd)} 中位={cd[len(cd) // 2]:.0f} 变式比={279673.3 / cd[len(cd) // 2]:.2f} 例比={439186.9 / cd[len(cd) // 2]:.2f}')

print('==== N. 变式1 标签行全列（找 8/9 缺口） ====')
cnt = 0
for pno in range(1, 8):
    for t, bb, sps in lines_of[pno]:
        if '变式1' in t:
            cnt += 1
            sz0 = sps[0]['size']
            print(f'p{pno} y={bb[1]:.0f} 首span={sps[0]["size"]:.2f}pt {t[:26]!r}')
print(f'含变式1行数={cnt}')

print('==== O. ⑲ 题号 tex 正则试配 ====')
body = open(os.path.join(BASE, 'body.tex'), encoding='utf-8').read()
p_old = r'\{\fontsize\{11\.4pt\}\{14pt\}\selectfont\heihao \textbf\{\d\}．\}'
p_new = r'\{\fontsize\{11\.4pt\}\{14pt\}\selectfont\heihao \{\numboldjian \d\}．\}'
print(f'旧式={len(re.findall(p_old, body))} 新式={len(re.findall(p_new, body))}')
print('==== 完 ====')
