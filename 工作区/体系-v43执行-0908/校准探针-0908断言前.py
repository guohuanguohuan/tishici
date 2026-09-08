# -*- coding: utf-8 -*-
"""v4.3 断言前校准探针（一次性）：把 _测v4断言.py v4.3 版要冻的窗口逐项实测取值。
输出后即弃，数值进断言窗并登记口径。"""
import os
import re
from collections import Counter

import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件"
PT = 72 / 25.4
MARGIN = 15 * PT
COLW = (595.276 - 2 * MARGIN - 7.5 * PT) / 2
MID = MARGIN + COLW + 7.5 * PT / 2
COLL = [MARGIN, MARGIN + COLW + 7.5 * PT]
COLR = 595.276 - MARGIN
BODY_BOT = 842.0 - 20 * PT
mm = lambda v: v / PT
DPI = 150
SC = DPI / 72.0

doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))


def bands(page, x0, x1, y0, y1, thresh=128, dpi=DPI):
    sc = dpi / 72.0
    pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(x0, y0, x1, y1))
    w, h, s = pm.width, pm.height, pm.samples
    rows = []
    for r in range(h):
        base = r * w
        rows.append(any(s[base + c] < thresh for c in range(w)))
    out = []
    st = None
    for i, d in enumerate(rows):
        if d and st is None:
            st = i
        elif not d and st is not None:
            out.append((y0 + st / sc, y0 + i / sc))
            st = None
    if st is not None:
        out.append((y0 + st / sc, y0 + h / sc))
    return out


lines_of = {}
for pno, page in enumerate(doc, 1):
    ls = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t:
                ls.append((t, ln['bbox'], ln['spans']))
    lines_of[pno] = ls

print('=== a) 栏线渲染芯（x=MID 列，dpi150/300） ===')
for dpi in (150, 300):
    sc = dpi / 72.0
    for pno in (1, 3):
        page = doc[pno - 1]
        pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY,
                             clip=pymupdf.Rect(MID - 2, MARGIN + 20, MID + 2, BODY_BOT - 20))
        w, h, s = pm.width, pm.height, pm.samples
        col = min(range(w), key=lambda c: abs((MID - 2) + (c + 0.5) / sc - MID))
        vals = [s[r * w + col] for r in range(h)]
        dark = [v for v in vals if v < 250]
        if dark:
            dark.sort()
            print(f'  dpi{dpi} p{pno} 芯中位 {dark[len(dark)//2]} min {dark[0]} p90 {dark[int(len(dark)*0.9)]} n={len(dark)}')

print('=== b) ◆ span 宽与后隙（12pt 行） ===')
gaps_f, wids = [], []
for pno, ls in lines_of.items():
    for t, bb, sps in ls:
        if ('知识点' in t or '探究点' in t) and sps[0]['text'].strip() == '◆':
            wids.append(mm(sps[0]['bbox'][2] - sps[0]['bbox'][0]))
            if len(sps) > 1:
                gaps_f.append(mm(sps[1]['bbox'][0] - sps[0]['bbox'][2]))
print(f'  ◆ advance 宽 {["%.2f" % w for w in wids]} 后隙 {["%.2f" % g for g in gaps_f]}')

print('=== c) 题侧→题干 advance 隙（8pt 灰 span 后继） ===')
g_td = []
for pno, ls in lines_of.items():
    for t, bb, sps in ls:
        for i, sp in enumerate(sps):
            if 7.5 <= sp['size'] <= 8.5 and sp['text'].strip().startswith('〔') and i + 1 < len(sps):
                g_td.append(mm(sps[i + 1]['bbox'][0] - sp['bbox'][2]))
print('  ' + ' '.join(f'{g:.2f}' for g in sorted(g_td)))

print('=== d) 检测题号→题侧 advance 隙 ===')
g_hao = []
for pno, ls in lines_of.items():
    for t, bb, sps in ls:
        for i, sp in enumerate(sps):
            if abs(sp['size'] - 11.4) < 0.4 and sp['text'].strip().endswith('．') and i + 1 < len(sps):
                g_hao.append(mm(sps[i + 1]['bbox'][0] - sp['bbox'][2]))
print('  ' + ' '.join(f'{g:.2f}' for g in g_hao))

print('=== e) 学习目标条目（楷体）几何 ===')
kt = []
for t, bb, sps in lines_of[1]:
    if sps and ('Kai' in sps[0]['font'] or 'kai' in sps[0]['font'].lower()):
        kt.append((bb[0], bb[1], bb[3], sps[0]['size'], t[:14]))
kt.sort()
for x0, y0, y1, sz, t in kt:
    print(f'  x0={mm(x0):.2f} y={mm(y0):.2f}-{mm(y1):.2f} sz={sz:.1f} {t}')
for a, b in zip(kt, kt[1:]):
    print(f'  行距 {mm(b[1] - a[1]):.2f}mm', end='')

print('\n=== f) 花形前距/后距/行总高（bands 口径） ===')
for pno, page in enumerate(doc, 1):
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c:
            continue
        rgb = tuple(round(x * 255) for x in c)
        if rgb == (77, 77, 77) and r.height <= 3 and r.width > 100:
            cl = COLL[0] if (r.x0 + r.x1) / 2 < MID else COLL[1]
            bs = bands(page, cl, cl + COLW, r.y0 - 40, r.y1 + 40)
            for i, (a, b) in enumerate(bs):
                if a <= r.y0 + 0.6 and b >= r.y0 - 0.6:
                    hua_i = i
            prev_b = bs[hua_i - 1][1] if hua_i > 0 else None
            next_a = bs[hua_i + 1][0] if hua_i + 1 < len(bs) else None
            print(f'  p{pno} 带{hua_i}/{len(bs)} 前距 {(r.y0 - 40 - 0) and mm(bs[hua_i][0] - prev_b) if prev_b else -1:.2f} '
                  f'后距 {mm(next_a - bs[hua_i][1]) if next_a else -1:.2f} 行总高 {mm(bs[hua_i][1] - bs[hua_i][0]):.2f}')

print('=== g) 图上下距（60mm 图 p2?；34mm 居中图） ===')
for pno, page in enumerate(doc, 1):
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            w_ = mm(r.width)
            if 32 < w_ < 36 or 58 < w_ < 62:
                cl = COLL[0] if r.x0 < MID else COLL[1]
                bs = bands(page, cl, cl + COLW, max(MARGIN, r.y0 - 30), min(BODY_BOT, r.y1 + 30))
                idx = [i for i, (a, b) in enumerate(bs) if a <= r.y0 + 1 and b >= r.y1 - 1]
                if not idx:
                    print(f'  p{pno} w={w_:.1f} 图带未并入（图亮）')
                    continue
                i = idx[0]
                pre = mm(bs[i][0] - bs[i - 1][1]) if i > 0 else -1
                nxt = mm(bs[i + 1][0] - bs[i][1]) if i + 1 < len(bs) else -1
                print(f'  p{pno} 图宽 {w_:.1f} 前距 {pre:.2f} 后距 {nxt:.2f}')

print('=== h) 解析→下一题题号 像素墨隙 ===')
gaps_jx = []
for pno, page in enumerate(doc, 1):
    for cl in COLL:
        rows = [(bb[1], bb[3], t) for t, bb, sps in lines_of[pno]
                if cl - 2 <= bb[0] < cl + COLW]
        rows.sort()
        for i in range(len(rows) - 1):
            y0, y1, t = rows[i]
            if not t.startswith('【解析】'):
                continue
            y0n, y1n, tn = rows[i + 1]
            if not (len(tn) > 2 and (tn[0] in '（12345' and (tn[1] in '）．.' or (tn[0] == '（' and tn[2] == '）')))):
                continue
            bs = bands(page, cl, cl + COLW, y1 - 2, y0n + 2)
            if len(bs) >= 2:
                gaps_jx.append((pno, mm(bs[-1][0] - bs[-2][1]), tn[:10]))
vals = [g for _, g, _ in gaps_jx]
print(f'  n={len(vals)} ' + ' '.join(f'{g:.2f}' for g in sorted(vals)))
if vals:
    vals.sort()
    print(f'  中位 {vals[len(vals)//2]:.2f} min {vals[0]:.2f}')

print('=== i) 判断题括号 ink 列位（像素行墨右缘） ===')
for pno, page in enumerate(doc, 1):
    for t, bb, sps in lines_of[pno]:
        if t.endswith('（√）') or t.endswith('（×）'):
            cl = COLL[0] if bb[0] < MID else COLL[1]
            bs = bands(page, cl, cl + COLW, bb[1] - 1, bb[3] + 1)
            pm = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,
                                 clip=pymupdf.Rect(cl, bb[1] - 1, cl + COLW, bb[3] + 1))
            w, h, s = pm.width, pm.height, pm.samples
            cols = [any(s[r_ * w + c] < 128 for r_ in range(h)) for c in range(w)]
            last = w - 1 - cols[::-1].index(True) if True in cols else -1
            ink_r = mm(cl + last / SC)
            print(f'  p{pno} …{t[-4:]} ink 右缘距栏线 {mm(cl + COLW) - ink_r:.2f}（bbox 口径 {mm(cl + COLW) - mm(bb[2]):.2f}）')

print('=== j) 选项 pitch 分档（边界＝首个 11.4pt span） ===')
b_y = b_p = None
for pno, ls in lines_of.items():
    for t, bb, sps in ls:
        if any(abs(sp['size'] - 11.4) < 0.4 for sp in sps):
            b_y = (pno, bb[1])
            break
    if b_y:
        break
print(f'  检测首题号 p{b_y[0]} y={mm(b_y[1]):.1f}')
for pno, page in enumerate(doc, 1):
    for ci, cl in enumerate(COLL):
        opts = []
        for t, bb, sps in lines_of[pno]:
            if len(t) > 1 and t[0] in 'ABCD' and t[1] in '．.' and cl - 2 <= bb[0] < cl + COLW:
                opts.append((t[0], sps[0]['origin'][1]))
        opts.sort(key=lambda x: x[1])
        for (la, ya), (lb, yb) in zip(opts, opts[1:]):
            if ord(lb) == ord(la) + 1:
                d = mm(yb - ya)
                reg = '评' if (pno, ya) >= b_y else '例'
                if 3 < yb - ya < 40:
                    print(f'  p{pno}c{ci} {la}->{lb} {d:.2f}mm {reg}')

print('=== k) 表组（线宽集合/表头行高/首列居中/表顶前距） ===')
for pno, page in enumerate(doc, 1):
    hrs, vrs = [], []
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c:
            continue
        rgb = tuple(round(x * 255) for x in c)
        if rgb != (122, 122, 122):
            continue
        th = d.get('width') if d['type'] == 's' else (r.height if r.width > r.height else r.width)
        if r.width > 15 * PT and r.height < 3:
            hrs.append((r.y0, r.x0, r.x1, th * 1 if d['type'] == 's' else r.height))
        elif r.height > 15 * PT and r.width < 3:
            vrs.append((r.x0, r.y0, r.y1, th * 1 if d['type'] == 's' else r.width))
    if len(hrs) >= 3:
        hrs.sort()
        print(f'  p{pno} 横线 n={len(hrs)} 厚集合 {sorted({round(mm(h[3]), 3) for h in hrs})} '
              f'行高 {["%.2f" % mm(b[0] - a[0]) for a, b in zip(hrs, hrs[1:])]}')
        if vrs:
            vrs.sort()
            print(f'      竖线 x {["%.2f" % mm(v[0]) for v in vrs]} 宽集合 {sorted({round(mm(v[3]), 3) for v in vrs})}')
            c0 = (vrs[0][0] + vrs[1][0]) / 2
            for t, bb, sps in lines_of[pno]:
                if hrs[0][0] - 1 <= bb[1] and bb[3] <= hrs[1][0] + 1 and vrs[0][0] <= bb[0] and bb[2] <= vrs[1][0]:
                    print(f'      首列表头 {t[:10]!r} 中心偏 {mm((bb[0] + bb[2]) / 2 - c0):+.2f}mm')
        bs = bands(page, hrs[0][1] if hrs[0][1] > MARGIN else COLL[0], COLL[0] + COLW, hrs[0][0] - 16, hrs[0][0] + 1)
        if bs:
            print(f'      表顶前距 {mm(hrs[0][0] - bs[-1][1]):.2f}')

print('=== l) 页脚小字字体/字号/数字近缘 ===')
for pno, page in enumerate(doc, 1):
    sps_f = []
    blk_rect = None
    for d in page.get_drawings():
        r = d['rect']
        f = d.get('fill')
        if f and r.y0 > BODY_BOT - 10 and tuple(round(x * 255) for x in f) == (221, 221, 221):
            blk_rect = r
    for t, bb, sps in lines_of[pno]:
        if bb[1] > BODY_BOT - 2:
            sps_f += [(sp['text'], sp['size'], sp['font'], sp['bbox']) for sp in sps if sp['text'].strip()]
    fonts = sorted({f for _, _, f, _ in sps_f})
    szs = sorted({round(sz, 1) for _, sz, _, _ in sps_f})
    num = [b for tx, sz, f, b in sps_f if tx.strip() == str(pno)]
    near = ''
    if blk_rect and num:
        odd = pno % 2 == 1
        inner = blk_rect.x0 if odd else blk_rect.x1
        nb = num[0]
        ne = nb[0] if odd else nb[2]
        near = f' 数字近缘距版心侧缘 {mm(abs(ne - inner)):.2f}'
    print(f'  p{pno} sz{szs} fonts{[f.split("+")[-1][:14] for f in fonts]}{near}')

print('=== m) 例/变式标签 span（12pt）与 ◆探究点独行 ===')
n_lab, n_solo = Counter(), 0
for pno, ls in lines_of.items():
    for t, bb, sps in ls:
        m0 = re.match(r'^(例1|变式1)〔', t)
        if m0:
            n_lab[m0.group(1)] += 1
            if not (11.6 <= sps[0]['size'] <= 12.4):
                print(f'  ! p{pno} {m0.group(1)} size {sps[0]["size"]}')
        if t.startswith('◆探究点'):
            n_solo += 1
            if '〔' in t or '例1' in t.replace('◆探究点', ''):
                print(f'  ! p{pno} 探究点行混排 {t[:20]}')
print(f'  标签 {dict(n_lab)} 探究点独行 {n_solo}')

print('=== n) 素养小结内容行字体 ===')
n_kai = 0
for pno, ls in lines_of.items():
    ls2 = sorted(ls, key=lambda x: x[1][1])
    for i, (t, bb, sps) in enumerate(ls2):
        if t.startswith('【素养小结】'):
            same = i + 1 < len(ls2) and abs(ls2[i + 1][1][1] - bb[1]) < 1
            j = i + 2 if same else i + 1
            if j < len(ls2):
                f0 = ls2[j][2][0]['font']
                n_kai += 1
                print(f'  p{pno} 内容行 font={f0.split("+")[-1][:16]} {ls2[j][0][:16]}')
print(f'  n={n_kai}')

print('=== o) 灰档全集 / p) 行距主峰 ===')
grays = set()
for page in doc:
    for sp in [sp for blk in page.get_text('dict')['blocks'] for ln in blk.get('lines', []) for sp in ln['spans']]:
        col = sp['color']
        r, g, b = (col >> 16) & 255, (col >> 8) & 255, col & 255
        if r == g == b and 0 < r < 255:
            grays.add(r)
    for d in page.get_drawings():
        for key in ('color', 'fill'):
            c = d.get(key)
            if c:
                rgb = tuple(round(x * 255) for x in c)
                if rgb[0] == rgb[1] == rgb[2] and 0 < rgb[0] < 255:
                    grays.add(rgb[0])
print(' ', sorted(grays))
diffs = []
for pno, page in enumerate(doc, 1):
    cols = {0: [], 1: []}
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            if any(10 <= sp['size'] <= 11 for sp in ln['spans']):
                cols[0 if ln['bbox'][0] < MID else 1].append(ln['spans'][0]['origin'][1])
    for c in (0, 1):
        ys = sorted(cols[c])
        diffs += [round((b - a) * 4) / 4 for a, b in zip(ys, ys[1:]) if 3 < b - a < 40]
print(' 主峰:', Counter(diffs).most_common(5))

print('=== q) 章首四档墨间距 + 占地 ===')
p1 = doc[0]
anchors = {}
for t, bb, sps in lines_of[1]:
    for k, pre in (('jie', '1.1 '), ('xj', '1.1.1'), ('ks', '第1课时'), ('mb', '【学习目标】')):
        if k not in anchors and t.startswith(pre):
            anchors[k] = bb
hl = None
for d in p1.get_drawings():
    r = d['rect']
    if r.width > 300 and r.height <= 2 and r.y0 < 40 * PT:
        hl = r
X0, X1 = MARGIN, 595.276 - MARGIN
bs = bands(p1, X0, X1, MARGIN, anchors['mb'][1] + 2)
def band_of(y):
    for i, (a, b) in enumerate(bs):
        if a - 1 <= y <= b + 1:
            return i
    return None
pairs = (('线→节', hl.y1, band_of(anchors['jie'][1])), ('节→小节', None, band_of(anchors['xj'][1])),
         ('小节→课时', None, band_of(anchors['ks'][1])), ('课时→目标', None, band_of(anchors['mb'][1])))
idx = [band_of(a['jie'][1]), band_of(anchors['xj'][1]), band_of(anchors['ks'][1]), band_of(anchors['mb'][1])]
line_i = [i for i, (a, b) in enumerate(bs) if a <= hl.y0 + 1 and b >= hl.y0 - 1]
seq = [line_i[0]] + idx if line_i else idx
for nm, i, j in zip(('线→节', '节→小节', '小节→课时', '课时→目标'), seq, seq[1:]):
    print(f'  {nm} {mm(bs[j][0] - bs[i][1]):.2f}mm')
print(f'  章首占地 版心顶→目标顶 {mm(anchors["mb"][1] - MARGIN):.2f}')
sq = [d['rect'] for d in p1.get_drawings() if d.get('fill') and d['rect'].y0 < 200 and d['rect'].width < 200
      and tuple(round(x * 255) for x in d['fill']) in ((221, 221, 221), (119, 119, 119))]
if sq:
    ux0 = min(r.x0 for r in sq); ux1 = max(r.x1 for r in sq)
    uy0 = min(r.y0 for r in sq); uy1 = max(r.y1 for r in sq)
    print(f'  方块 union {mm(ux1 - ux0):.2f}×{mm(uy1 - uy0):.2f} 横线厚 {mm(hl.height):.3f} 章名距方块 {mm(lines_of[1][0][1][0] - 0):.2f}(查)')

print('=== r) 诊断分析头单行/字号 + ③栏内花形线宽 ===')
zhen = [(t, sps[0]['size']) for ls in lines_of.values() for t, bb, sps in ls if t.startswith('【诊断分析】')]
print(' ', [(t[:18], round(s, 1)) for t, s in zhen])
