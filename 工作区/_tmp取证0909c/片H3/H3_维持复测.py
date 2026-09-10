# -*- coding: utf-8 -*-
"""H3 维持项复测（H1/H2 片成果，逐项抽点；口径同 H1 FINAL_复测.py / H2 _spot_check.py）。
默认跑 variantF/main.pdf；输出 H3_维持.json。"""
import json
import statistics as st
import sys

import numpy as np
import pymupdf
from PIL import Image
import io
from scipy import ndimage

PDF = sys.argv[1] if len(sys.argv) > 1 else r'C:/提示词/工作区/字替对照-0909/variantF/main.pdf'
OUT = sys.argv[2] if len(sys.argv) > 2 else r'C:/提示词/工作区/_tmp取证0909c/片H3/H3_维持.json'
PTMM = 72 / 25.4
doc = pymupdf.open(PDF)
res = {}

# ---- E1 字心距（H1 法：rawdict 纯 CJK 相邻 origin 差） ----
pitches, perline = [], []
for pno in range(1, len(doc) + 1):
    d = doc[pno - 1].get_text('rawdict')
    for b in d['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            cs = sorted([(c['c'], c['origin'][0], round(sp['size'], 2)) for sp in l['spans'] for c in sp['chars']],
                        key=lambda r: r[1])
            ps = []
            for i in range(len(cs) - 1):
                if 0x4E00 <= ord(cs[i][0]) <= 0x9FFF and 0x4E00 <= ord(cs[i+1][0]) <= 0x9FFF \
                        and abs(cs[i][2] - cs[i+1][2]) < 0.1 and cs[i][2] > 9.5:
                    g = cs[i+1][1] - cs[i][1]
                    if 8 < g < 16: ps.append(g)
            if len(ps) >= 8:
                pitches += ps
                perline.append((pno, round(st.median(ps), 2)))
res['E1'] = {
    'pitch_med_pt': round(st.median(pitches), 3),
    'pitch_med_mm': round(st.median(pitches) / PTMM, 3),
    'pitch_med_px360': round(st.median(pitches) / PTMM * 14.176, 2),
    'n_pairs': len(pitches), 'n_lines': len(perline),
    '参考（H2 终版）': '11.118pt=3.922mm=55.6px（n=132 行）',
}

# ---- 栏宽/栏距 ink（H1 E7 法，360dpi） ----
E7 = {}
for pno in (2, 4, 6):   # p3 p5 p7 (1-based)
    pix = doc[pno-1].get_pixmap(dpi=360)
    g = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].mean(axis=2).astype(np.uint8)
    ik = g < 170
    body = ik[400:3700, :]
    cols = body.sum(axis=0)
    on = np.where(cols > 0)[0]
    x_lo, x_hi = int(on[0]), int(on[-1] + 1)
    mid = cols[1400:1650]
    runs, s = [], None
    for i, v in enumerate(mid == 0):
        if v and s is None: s = i
        elif not v and s is not None: runs.append((1400+s, 1400+i)); s = None
    lg = max(runs, key=lambda r: r[1]-r[0]) if runs else None
    lo = np.where(cols[:lg[0]] > 0)[0]; ro = np.where(cols[lg[1]:] > 0)[0]
    E7[f'p{pno+1}'] = dict(
        ink_left_mm=round(x_lo/14.1732, 2), ink_right_mm=round((g.shape[1]-x_hi)/14.1732, 2),
        col_l_mm=round((int(lo[-1]+1)-int(lo[0]))/14.1732, 2) if len(lo) else None,
        col_r_mm=round((int(ro[-1]+1)-int(ro[0]))/14.1732, 2) if len(ro) else None,
        colgap_mm=round((int(ro[0])+lg[1]-int(lo[-1]+1))/14.1732, 2))
res['E7'] = E7

# ---- E2 标点像素墨隙（H1 法） ----
def find_lines(ik, x0, x1, mi=3):
    row = ik[:, x0:x1].sum(axis=1)
    on = row > mi
    runs, s = [], None
    for i, v in enumerate(on):
        if v and s is None: s = i
        elif not v and s is not None: runs.append((s, i)); s = None
    if s is not None: runs.append((s, len(on)))
    merged = []
    for r in runs:
        if merged and r[0]-merged[-1][1] <= 4: merged[-1] = (merged[-1][0], r[1])
        else: merged.append(list(r))
    return [(a, b) for a, b in merged if b-a >= 8]

def segs(ik, y0, y1, x0, x1, mw=4):
    sub = ik[y0:y1, x0:x1]
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    if n == 0: return []
    comps = []
    for sl in ndimage.find_objects(lab):
        ys, xs = sl; comps.append((xs.start, xs.stop, ys.start+y0, ys.stop+y0))
    comps.sort(); groups = []
    for c in comps:
        for g in groups:
            if not (c[1]+1 < g[0] or c[0]-1 > g[1]):
                g[0] = min(g[0], c[0]); g[1] = max(g[1], c[1]); g[2] = min(g[2], c[2]); g[3] = max(g[3], c[3]); break
        else: groups.append(list(c))
    ch = True
    while ch:
        ch = False; out = []
        for g in sorted(groups):
            if out and not (g[0] > out[-1][1]+1):
                out[-1][0] = min(out[-1][0], g[0]); out[-1][1] = max(out[-1][1], g[1])
                out[-1][2] = min(out[-1][2], g[2]); out[-1][3] = max(out[-1][3], g[3]); ch = True
            else: out.append(g)
        groups = out
    return [g for g in groups if g[1]-g[0] >= mw]

E2 = []
for pno in range(1, 7):
    pix = doc[pno-1].get_pixmap(dpi=360)
    g = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].mean(axis=2).astype(np.uint8)
    ik = g < 170
    for x0, x1 in [(244, 1443), (1540, 2739)]:
        for (a, b) in find_lines(ik, x0, x1):
            if not (24 < b-a < 55): continue
            ss = segs(ik, a, b, x0, x1)
            if len(ss) < 6: continue
            medh = np.median([s[3]-s[2] for s in ss])
            for i in range(1, len(ss)-1):
                s = ss[i]; h = s[3]-s[2]; w = s[1]-s[0]
                if h < 0.40*medh and 5 <= w <= 18 and s[3] >= a+0.6*(b-a):
                    pv, nx = ss[i-1], ss[i+1]
                    if pv[3]-pv[2] > 0.6*medh and nx[3]-nx[2] > 0.6*medh:
                        gb = s[0]-pv[1]; ga = nx[0]-s[1]
                        if -5 < gb < 45 and -5 < ga < 45:
                            E2.append((pno, round(gb, 1), round(ga, 1)))
gb = [e[1] for e in E2]; ga = [e[2] for e in E2]
res['E2'] = {'n': len(E2), 'before_px_med': st.median(gb) if gb else None, 'after_px_med': st.median(ga) if ga else None,
             '参考（H1 靶）': 'before 16 / after 14（n=98）'}

# ---- 判断题序号隙 / = 隙 / ∥ 隙（H2 _spot_check 法：600dpi ink） ----
def ink(pno, rect, thr=170, dpi=600):
    px = dpi/72
    pix = doc[pno].get_pixmap(dpi=dpi, clip=pymupdf.Rect(*rect))
    a = np.asarray(Image.open(io.BytesIO(pix.tobytes('png'))).convert('L')).astype(np.uint8) < thr
    ys, xs = np.nonzero(a)
    if not len(xs): return None
    return dict(x0=rect[0]+xs.min()/px, x1=rect[0]+xs.max()/px, y0=rect[1]+ys.min()/px, y1=rect[1]+ys.max()/px)

judge = []
for pno in range(len(doc)):
    d = doc[pno].get_text('rawdict')
    for b in d['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            cs = [c for sp in l['spans'] for c in sp['chars'] if c['c'].strip()]
            if len(cs) > 6 and cs[0]['c'] == '(' and cs[1]['c'].isdigit() and cs[2]['c'] == ')' and 0x4e00 <= ord(cs[3]['c'][0]) <= 0x9fff:
                # bbox 隙（) 右缘→首字左缘）
                bb_gap = (cs[3]['bbox'][0] - cs[2]['bbox'][2]) * 25.4/72
                # ink 隙
                r1 = ink(pno, (cs[2]['bbox'][0]-0.5, cs[2]['bbox'][1]+2, cs[2]['bbox'][2]+0.5, cs[2]['bbox'][3]-1))
                r2 = ink(pno, (cs[3]['bbox'][0]-0.2, cs[3]['bbox'][1]+2, cs[3]['bbox'][0]+2, cs[3]['bbox'][3]-1))
                ik_gap = (r2['x0']-r1['x1'])*25.4/72 if r1 and r2 else None
                judge.append((pno+1, round(bb_gap, 3), round(ik_gap, 3) if ik_gap is not None else None))
res['判断题序号隙'] = {'n': len(judge),
                 'bbox_mm': [j[1] for j in judge], 'ink_mm': [j[2] for j in judge],
                 '参考（H2/F）': 'ink 0.945–1.030（n=6，F 口径）；bbox 0.737–0.963（H2）'}

eq_gaps, par_gaps = [], []
for pno in range(len(doc)):
    d = doc[pno].get_text('rawdict')
    for b in d['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            cs = [c for sp in l['spans'] for c in sp['chars'] if c['c'].strip()]
            for i, c in enumerate(cs):
                if c['c'] == '=' and 0 < i < len(cs)-1 and cs[i-1]['c'] not in '=<>≤≥≠':
                    if not ('a' <= cs[i+1]['c'][0].lower() <= 'z'): continue
                    L = ink(pno, (cs[i-1]['bbox'][0]-0.3, cs[i-1]['bbox'][1]+2, cs[i-1]['bbox'][2], cs[i-1]['bbox'][3]-2))
                    M = ink(pno, (c['bbox'][0]-0.3, c['bbox'][1]+2, c['bbox'][2]+0.3, c['bbox'][3]-2))
                    R = ink(pno, (cs[i+1]['bbox'][0], cs[i+1]['bbox'][1]+2, cs[i+1]['bbox'][2]+0.3, cs[i+1]['bbox'][3]-2))
                    if L and M and R:
                        eq_gaps.append((pno+1, round((M['x0']-L['x1'])*25.4/72, 3), round((R['x0']-M['x1'])*25.4/72, 3)))
                if c['c'] == '∥' and 0 < i < len(cs)-1:
                    L = ink(pno, (cs[i-1]['bbox'][0]-0.3, cs[i-1]['bbox'][1]+2, cs[i-1]['bbox'][2], cs[i-1]['bbox'][3]-2))
                    M = ink(pno, (c['bbox'][0]-0.3, c['bbox'][1]+2, c['bbox'][2]+0.3, c['bbox'][3]-2))
                    R = ink(pno, (cs[i+1]['bbox'][0], cs[i+1]['bbox'][1]+2, cs[i+1]['bbox'][2]+0.3, cs[i+1]['bbox'][3]-2))
                    if L and M and R:
                        par_gaps.append((pno+1, round((M['x0']-L['x1'])*25.4/72, 3), round((R['x0']-M['x1'])*25.4/72, 3)))
res['=隙'] = {'n': len(eq_gaps), '左中位': st.median([e[1] for e in eq_gaps]) if eq_gaps else None,
             '右中位': st.median([e[2] for e in eq_gaps]) if eq_gaps else None,
             '参考（H2）': '左/右 1.594/1.625mm（n=147）'}
res['∥隙'] = {'n': len(par_gaps), '明细': par_gaps[:8], '参考（H1）': '左 0.552–1.046 / 右 0.915–1.128（n=7）'}

# ---- 数学式档：脚本比（span 尺寸）+ 分式总高（细分式杠） ----
sizes = {}
for pno in range(len(doc)):
    d = doc[pno].get_text('rawdict')
    for b in d['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            for sp in l['spans']:
                t = ''.join(c['c'] for c in sp['chars']).strip()
                if 'TeXGyre' in sp['font'] and t:
                    sizes.setdefault(round(sp['size'], 2), 0)
                    sizes[round(sp['size'], 2)] += len(t)
res['数学字体尺寸分布'] = dict(sorted(sizes.items()))
fracs = []
for pno in range(len(doc)):
    for d in doc[pno].get_drawings():
        r = d['rect']
        if r.height <= 1.2 and 8 <= r.width <= 40 and d.get('fill'):
            rgb = tuple(round(v*255) for v in d['fill'])
            if rgb == (0, 0, 0) or max(rgb) < 100:
                fracs.append((pno+1, round(r.x0, 1), round(r.y0, 1), round(r.width, 1), round(r.height, 2)))
res['分式杠候选'] = fracs[:12]
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
