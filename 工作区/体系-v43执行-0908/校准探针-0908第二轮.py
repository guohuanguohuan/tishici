# -*- coding: utf-8 -*-
"""v4.3 断言前校准探针·第二轮（一次性）：修补一轮缺陷项，取剩余窗口值＋括号统一后复测。"""
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


def merge(bs, gap=0.35):
    """相邻带墨隙 <gap mm 并带。"""
    out = []
    for a, b in bs:
        if out and a - out[-1][1] < gap:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
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

print('=== i) 括号统一后复测 ===')
for pno, page in enumerate(doc, 1):
    for t, bb, sps in lines_of[pno]:
        if t.endswith('（√）') or t.endswith('（×）'):
            cl = COLL[0] if bb[0] < MID else COLL[1]
            pm = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,
                                 clip=pymupdf.Rect(cl, bb[1] - 1, cl + COLW, bb[3] + 1))
            w, h, s = pm.width, pm.height, pm.samples
            cols = [any(s[r_ * w + c] < 128 for r_ in range(h)) for c in range(w)]
            last = w - 1 - cols[::-1].index(True)
            print(f'  p{pno} …{t[-4:]} ink {mm(cl + COLW - cl - last / SC):.2f}（bbox {mm(cl + COLW) - mm(bb[2]):.2f}）')

print('=== f2) 花形 前距/后距/行总高（merge 并带） ===')
for pno, page in enumerate(doc, 1):
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c:
            continue
        rgb = tuple(round(x * 255) for x in c)
        if rgb == (77, 77, 77) and r.height <= 3 and r.width > 100:
            cl = COLL[0] if (r.x0 + r.x1) / 2 < MID else COLL[1]
            bs = merge(bands(page, cl, cl + COLW, r.y0 - 45, r.y1 + 45))
            hua = [i for i, (a, b) in enumerate(bs) if a <= r.y0 + 1 and b >= r.y0 - 1]
            if not hua:
                print(f'  p{pno} 线带未命中'); continue
            i = hua[0]
            pre = mm(bs[i][0] - bs[i - 1][1]) if i > 0 else -9
            nxt = mm(bs[i + 1][0] - bs[i][1]) if i + 1 < len(bs) else -9
            print(f'  p{pno} 前距 {pre:.2f} 后距 {nxt:.2f} 行总高 {mm(bs[i][1] - bs[i][0]):.2f}（并带 {len(bs)} 段）')

print('=== g2) 独立图上下距（60mm / 34mm 居中图） ===')
for pno, page in enumerate(doc, 1):
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            w_ = mm(r.width)
            if not (58 < w_ < 62 or 33 < w_ < 35.2):
                continue
            cl = COLL[0] if r.x0 < MID else COLL[1]
            if mm(r.x0 + r.x1 - 2 * cl - COLW) > 3:
                continue   # 仅居中独立图
            bs = bands(page, cl, cl + COLW, max(MARGIN, r.y0 - 30), min(BODY_BOT, r.y1 + 30))
            inside = [(a, b) for a, b in bs if b > r.y0 + 0.5 and a < r.y1 - 0.5]
            if not inside:
                print(f'  p{pno} w={w_:.1f} 图内无墨带'); continue
            pre = mm(inside[0][0] - bs[bs.index(inside[0]) - 1][1]) if bs.index(inside[0]) > 0 else -9
            li = bs.index(inside[-1])
            nxt = mm(bs[li + 1][0] - inside[-1][1]) if li + 1 < len(bs) else -9
            print(f'  p{pno} 图宽 {w_:.1f} 前距 {pre:.2f} 后距 {nxt:.2f}（图内带 {len(inside)}）')

print('=== h2) 解析→下一题题号 像素墨隙（debug） ===')
gaps_jx = []
for pno, page in enumerate(doc, 1):
    for cl in COLL:
        rows = sorted([(bb[1], bb[3], t) for t, bb, sps in lines_of[pno] if cl - 2 <= bb[0] < cl + COLW])
        for i in range(len(rows) - 1):
            y0, y1, t = rows[i]
            if not t.startswith('【解析】'):
                continue
            y0n, y1n, tn = rows[i + 1]
            isnum = re.match(r'^（?\d+[）．.．]', tn)
            if not isnum:
                print(f'  [skip] p{pno} 解析后继非题号：{tn[:18]!r}')
                continue
            bs = bands(page, cl, cl + COLW, y1 - 2, y0n + 2)
            if len(bs) >= 2:
                gaps_jx.append((pno, mm(bs[-1][0] - bs[-2][1]), tn[:8]))
vals = sorted(g for _, g, _ in gaps_jx)
print(f'  n={len(vals)} ' + ' '.join(f'{g:.2f}' for g in vals))
if vals:
    print(f'  中位 {vals[len(vals) // 2]:.2f} min {vals[0]:.2f}')

print('=== j2) 选项 pitch 分档（相邻行约束） ===')
b_y = None
for pno in range(1, len(doc) + 1):
    for t, bb, sps in lines_of[pno]:
        if any(abs(sp['size'] - 11.4) < 0.4 for sp in sps):
            b_y = (pno, bb[1]); break
    if b_y:
        break
print(f'  边界：检测首题号 p{b_y[0]} y={mm(b_y[1]):.1f}')
npitch = Counter()
for pno, page in enumerate(doc, 1):
    for ci, cl in enumerate(COLL):
        rows = sorted([(bb[1], t, sps[0]['origin'][1]) for t, bb, sps in lines_of[pno]
                       if len(t) > 1 and t[0] in 'ABCD' and t[1] in '．.' and cl - 2 <= bb[0] < cl + COLW])
        allr = sorted([(bb[1], bb[3]) for t, bb, sps in lines_of[pno] if cl - 2 <= bb[0] < cl + COLW])
        for (ya, ta, oya), (yb, tb, oyb) in zip(rows, rows[1:]):
            if ord(tb[0]) != ord(ta[0]) + 1:
                continue
            # 相邻行约束：两选项行之间无其他文本行
            if any(yb - 0.5 > c and d > ya + 0.5 for c, d in allr if not (abs(c - ya) < 0.5 or abs(c - yb) < 0.5)):
                continue
            d_ = mm(oyb - oya)
            reg = '评' if (pno, oya) >= (b_y[0], b_y[1]) else '例'
            if 3 < oyb - oya < 40:
                npitch[(reg, round(d_, 2))] += 1
print(' ', dict(npitch))

print('=== k2) 表组补测（表顶前距排除线自身/竖线放宽） ===')
for pno, page in enumerate(doc, 1):
    hrs, vrs = [], []
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c or tuple(round(x * 255) for x in c) != (122, 122, 122):
            continue
        if r.width > 15 * PT and r.height < 3:
            hrs.append(r)
        elif r.height > 5 * PT and r.width < 3:
            vrs.append(r)
    if len(hrs) < 3:
        continue
    hrs.sort(); vrs.sort()
    cl = COLL[0] if (hrs[0].x0 + hrs[0].x1) / 2 < MID else COLL[1]
    bs = bands(page, cl, cl + COLW, hrs[0].y0 - 16, hrs[0].y0 + 0.5)
    above = [b for b in bs if b[1] < hrs[0].y0 - 0.1]
    pre = mm(hrs[0].y0 - above[-1][1]) if above else -9
    print(f'  p{pno} 表顶前距 {pre:.2f} 竖线 n={len(vrs)} x0={mm(vrs[0].x0) if vrs else -1:.2f}')
    if len(vrs) >= 2:
        c0 = (vrs[0].x0 + vrs[1].x0) / 2
        for t, bb, sps in lines_of[pno]:
            if hrs[0].y0 - 1 <= bb[1] and bb[3] <= hrs[1].y0 + 1 and vrs[0].x0 <= bb[0] and bb[2] <= vrs[1].x0:
                print(f'      首列表头 {t[:10]!r} 中心偏 {mm((bb[0] + bb[2]) / 2 - c0):+.2f}mm')

print('=== q2) 章首锚点与四档 ===')
p1 = doc[0]
for t, bb, sps in lines_of[1][:14]:
    print(f'  [{t[:26]!r}] y={mm(bb[1]):.2f}')
anchors = {}
for t, bb, sps in lines_of[1]:
    for k, pre in (('zh', '第一章'), ('jie', '1.1 '), ('xj', '1.1.1'), ('ks', '第1课时'), ('mb', '【学习目标】')):
        if k not in anchors and t.replace(' ', '').startswith(pre):
            anchors[k] = bb
print('  锚点命中:', sorted(anchors))
hl = None
for d in p1.get_drawings():
    r = d['rect']
    if r.width > 300 and r.height <= 2 and r.y0 < 40 * PT:
        hl = r
X0, X1 = MARGIN, 595.276 - MARGIN
if 'mb' in anchors and hl is not None:
    bs = merge(bands(p1, X0, X1, MARGIN, anchors['mb'][1] + 2))
    def band_of(y):
        for i, (a, b) in enumerate(bs):
            if a - 1 <= y <= b + 1:
                return i
        return None
    line_i = band_of(hl.y0)
    seq = [band_of(anchors[k][1]) for k in ('jie', 'xj', 'ks', 'mb')]
    names = ('线→节', '节→小节', '小节→课时', '课时→目标')
    chain = [line_i] + seq
    for nm, i, j in zip(names, chain, chain[1:]):
        print(f'  {nm} {mm(bs[j][0] - bs[i][1]):.2f}mm' if i is not None and j is not None else f'  {nm} 缺带')
    print(f'  占地 {mm(anchors["mb"][1] - MARGIN):.2f} 横线厚 {mm(hl.height):.3f}mm')
    sq = [d['rect'] for d in p1.get_drawings() if d.get('fill') and d['rect'].y0 < 200 and d['rect'].width < 200
          and tuple(round(x * 255) for x in d['fill']) in ((221, 221, 221), (119, 119, 119))]
    ux0 = min(r.x0 for r in sq); ux1 = max(r.x1 for r in sq)
    uy0 = min(r.y0 for r in sq); uy1 = max(r.y1 for r in sq)
    zh_bb = anchors['zh']
    print(f'  union {mm(ux1 - ux0):.2f}×{mm(uy1 - uy0):.2f} 章名ink左-union右 {mm(zh_bb[0] - ux1):.2f}')
