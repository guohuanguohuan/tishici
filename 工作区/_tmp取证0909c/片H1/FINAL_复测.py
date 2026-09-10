# -*- coding: utf-8 -*-
r"""片H1 · 终验一表测（FINAL_main.pdf）——E1/E2/E7/③ + 复测全品靶对照数
输出 JSON + 控制台。"""
import json
import statistics as st

import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage

PXMM = 14.176
PTMM = 72 / 25.4
DOC = 'FINAL_main.pdf'
REF = r'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/%s.png'


def render_png(pno, dpi=360):
    doc = pymupdf.open(DOC)
    pg = doc[pno - 1]
    pix = pg.get_pixmap(dpi=dpi)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].mean(axis=2).astype(np.uint8), doc


def load_ref(tag):
    return np.asarray(Image.open(REF % tag).convert('L')).astype(np.uint8)


def ink(g, t=170):
    return g < t


def find_lines(ik, x0, x1, mi=3):
    row = ik[:, x0:x1].sum(axis=1)
    on = row > mi
    runs = []; s = None
    for i, v in enumerate(on):
        if v and s is None: s = i
        elif not v and s is not None: runs.append((s, i)); s = None
    if s is not None: runs.append((s, len(on)))
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] <= 4: merged[-1] = (merged[-1][0], r[1])
        else: merged.append(list(r))
    return [(a, b) for a, b in merged if b - a >= 8]


def segs(ik, y0, y1, x0, x1, mw=4):
    sub = ik[y0:y1, x0:x1]
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    if n == 0: return []
    objs = ndimage.find_objects(lab); comps = []
    for sl in objs:
        ys, xs = sl; comps.append((xs.start, xs.stop, ys.start + y0, ys.stop + y0))
    comps.sort(); groups = []
    for c in comps:
        for g in groups:
            if not (c[1] + 1 < g[0] or c[0] - 1 > g[1]):
                g[0] = min(g[0], c[0]); g[1] = max(g[1], c[1]); g[2] = min(g[2], c[2]); g[3] = max(g[3], c[3]); break
        else: groups.append(list(c))
    ch = True
    while ch:
        ch = False; out = []
        for g in sorted(groups):
            if out and not (g[0] > out[-1][1] + 1):
                out[-1][0] = min(out[-1][0], g[0]); out[-1][1] = max(out[-1][1], g[1])
                out[-1][2] = min(out[-1][2], g[2]); out[-1][3] = max(out[-1][3], g[3]); ch = True
            else: out.append(g)
        groups = out
    return [g for g in groups if g[1] - g[0] >= mw]


res = {}
doc = pymupdf.open(DOC)

# ---- E1 字心距/每行字数（rawdict 逐字 origin；纯 CJK 相邻对） ----
pitches = []
perline = []
for pno in range(1, len(doc) + 1):
    d = doc[pno - 1].get_text('rawdict')
    for b in d['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            cs = sorted([(c['c'], c['origin'][0], round(sp['size'], 2)) for sp in l['spans'] for c in sp['chars']],
                        key=lambda r: r[1])
            ps = []
            for i in range(len(cs) - 1):
                if 0x4E00 <= ord(cs[i][0]) <= 0x9FFF and 0x4E00 <= ord(cs[i + 1][0]) <= 0x9FFF \
                        and abs(cs[i][2] - cs[i + 1][2]) < 0.1 and cs[i][2] > 9.5:
                    g = cs[i + 1][1] - cs[i][1]
                    if 8 < g < 16:
                        ps.append(g)
            if len(ps) >= 8:
                pitches += ps
                perline.append((pno, round(st.median(ps), 2)))
res['E1'] = {
    'n_pairs': len(pitches),
    'pitch_med_pt': round(st.median(pitches), 3),
    'pitch_med_mm': round(st.median(pitches) / PTMM, 3),
    'pitch_med_px360': round(st.median(pitches) / PTMM * 14.176, 2),
    'pitch_p10_p90_px': [round(sorted(pitches)[len(pitches) // 10] / PTMM * 14.176, 1),
                         round(sorted(pitches)[9 * len(pitches) // 10] / PTMM * 14.176, 1)],
    '全品靶_px': 56.5, '全品靶_mm': 3.99,
}
# 每行字数（纯 CJK 行：整行 span 全 CJK 且字号≈10.05）
nchars = []
for pno in range(1, len(doc) + 1):
    d = doc[pno - 1].get_text('rawdict')
    for b in d['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            cs = [(c['c'], round(sp['size'], 2)) for sp in l['spans'] for c in sp['chars']]
            cjk = [c for c, sz in cs if 0x4E00 <= ord(c) <= 0x9FFF]
            if cs and len(cjk) == len(cs) and len(cs) >= 12 and abs(cs[0][1] - 10.05) < 0.15:
                nchars.append((pno, len(cs)))
cjk_counts = [n for _, n in nchars]
res['E1']['per_line_chars_med'] = st.median(cjk_counts) if cjk_counts else None
res['E1']['per_line_chars_mode'] = max(set(cjk_counts), key=cjk_counts.count) if cjk_counts else None
res['E1']['n_lines_sampled'] = len(nchars)

# ---- E7 版面几何（像素，360dpi 渲染） ----
E7 = {}
for pno in range(1, 7):
    g, _ = render_png(pno, 360)
    ik = ink(g)
    H, W = ik.shape
    body = ik[150:3900, :]
    cols = body.sum(axis=0)
    on = np.where(cols > 0)[0]
    x_lo, x_hi = int(on[0]), int(on[-1] + 1)
    # 栏带（分左右）
    mid = cols[1300:1700]
    runs = []; s = None
    for i, v in enumerate(mid):
        if v == 0 and s is None: s = i
        elif v != 0 and s is not None: runs.append((1300 + s, 1300 + i)); s = None
    lg = max(runs, key=lambda r: r[1] - r[0]) if runs else (1449, 1500)
    left_on = np.where(cols[:lg[0]] > 0)[0]; right_on = np.where(cols[lg[1]:] > 0)[0]
    lspan = (int(left_on[0]), int(left_on[-1] + 1)) if len(left_on) else None
    rspan = (int(right_on[0] + lg[1]), int(right_on[-1] + 1 + lg[1])) if len(right_on) else None
    lines = find_lines(ik, lspan[0] - 5, lspan[1] + 5)
    tlines = [(a, b) for a, b in lines if (b - a) < 60]
    ycs = [(a + b) / 2 for a, b in tlines]
    diffs = [b - a for a, b in zip(ycs, ycs[1:]) if 60 < b - a < 140]
    from collections import Counter
    res_pt = Counter([round(dd * 72 / 25.4 / PXMM, 2) for dd in diffs]).most_common(3)
    E7[f'p{pno}'] = dict(
        ink_left_mm=round(x_lo / PXMM, 2), ink_right_mm=round((W - x_hi) / PXMM, 2),
        col_l_mm=(round((lspan[1] - lspan[0]) / PXMM, 2) if lspan else None),
        col_r_mm=(round((rspan[1] - rspan[0]) / PXMM, 2) if rspan else None),
        colgap_mm=(round((rspan[0] - lspan[1]) / PXMM, 2) if lspan and rspan else None),
        first_top_mm=round(tlines[0][0] / PXMM, 2),
        pitch_pt=res_pt)
res['E7'] = E7

# ---- E2 标点像素墨隙（严格过滤：两侧全字 CJK） ----
E2 = []
for pno in range(1, 7):
    g, _ = render_png(pno, 360)
    ik = ink(g)
    for x0, x1 in [(244, 1443), (1540, 2739)]:
        for (a, b) in find_lines(ik, x0, x1):
            if not (24 < b - a < 55): continue
            ss = segs(ik, a, b, x0, x1)
            if len(ss) < 6: continue
            medh = np.median([s[3] - s[2] for s in ss])
            for i in range(1, len(ss) - 1):
                s = ss[i]; h = s[3] - s[2]; w = s[1] - s[0]
                if h < 0.40 * medh and 5 <= w <= 18 and s[3] >= a + 0.6 * (b - a):
                    pv, nx = ss[i - 1], ss[i + 1]
                    if pv[3] - pv[2] > 0.6 * medh and nx[3] - nx[2] > 0.6 * medh:
                        gb = s[0] - pv[1]; ga = nx[0] - s[1]
                        if -5 < gb < 45 and -5 < ga < 45:
                            E2.append((pno, round(gb, 1), round(ga, 1)))
gb = [e[1] for e in E2]; ga = [e[2] for e in E2]
res['E2'] = {
    'n': len(E2),
    'before_px_med': st.median(gb), 'after_px_med': st.median(ga),
    'before_px_p10p90': [sorted(gb)[len(gb) // 10], sorted(gb)[9 * len(gb) // 10]],
    'after_px_p10p90': [sorted(ga)[len(ga) // 10], sorted(ga)[9 * len(ga) // 10]],
    '全品靶_px(同法复测)': {'before': 16.0, 'after': 14.0, 'n': 98},
    'samples3': [e for e in E2[:3]],
}

# ---- ③ 变式标签接缝 + '1'|中（rawdict 逐字） ----
lab = []
for pno in range(1, len(doc) + 1):
    d = doc[pno - 1].get_text('rawdict')
    for b in d['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            cs = sorted([(c['c'], c['bbox'], c['origin'][0]) for sp in l['spans'] for c in sp['chars']],
                        key=lambda r: r[2])
            for i in range(len(cs) - 1):
                a, b2 = cs[i], cs[i + 1]
                if (a[0] == '式' and b2[0].isdigit()) or (a[0] == '1' and b2[0] == '中'):
                    lab.append((pno, round(l['bbox'][1], 1), a[0], b2[0],
                                round(b2[1][0] - a[1][2], 2), round((b2[1][0] - a[1][2]) / PTMM, 2)))
res['③'] = lab
json.dump(res, open('FINAL_复测.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
