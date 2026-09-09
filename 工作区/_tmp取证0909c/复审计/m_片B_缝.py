# -*- coding: utf-8 -*-
r"""复审计·片B 独立重测（一）：竖向缝隙（600dpi 墨隙 + 基线 pitch）
对象：
  ① 条目2 (1)→(2) 拆段缝（p1 左栏，「字母表示法/几何表示法」行对）
  ② 条目→条目缝 6 对（知识点一 1→2/2→3；知识点二 1→2；知识点三 1→2/2→3/3→4）
  ③ 相邻判断题缝 3 处（诊断块①②③：(1)解析末行→(2)题干行）
口径：pitch＝两行基线距（span origin y 差）；墨隙＝上行墨底→下行墨顶（600dpi gray<128，
      x 取两行 bbox 并集 ±0.5mm；上/下行墨带以两行 bbox 中点为界）。
"""
import json
import os

import numpy as np
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
DPI = 600
PT = 72 / 25.4

doc = pymupdf.open(PDF)


def render(page):
    pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)


def lines_of(page):
    out = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            t = ''.join(s['text'] for s in l['spans'])
            sp = l['spans'][0] if l['spans'] else None
            out.append(dict(text=t, bbox=l['bbox'], base=(sp['origin'][1] if sp else None)))
    return out


def ink_gap(img, up, lo):
    """up/lo＝两行 dict（bbox pt）。返回 (pitch_mm, gap_mm, up_ink_bottom_mm, lo_ink_top_mm)"""
    ux0, uy0, ux1, uy1 = [v / PT for v in up['bbox']]
    lx0, ly0, lx1, ly1 = [v / PT for v in lo['bbox']]
    x_lo = min(ux0, lx0) - 0.5
    x_hi = max(ux1, lx1) + 0.5
    mid = (uy1 + ly0) / 2
    y_top = uy1 - 1.0     # 上行墨底下缘之上 1mm
    y_bot = ly0 + 1.0     # 下行墨顶上缘之下 1mm
    px = lambda mm, d: int(round(mm * d / 25.4))
    reg = img[px(y_top, DPI):px(y_bot, DPI), px(x_lo, DPI):px(x_hi, DPI)]
    mask = reg < 128
    rows = np.where(mask.any(axis=1))[0]
    if len(rows) == 0:
        return None
    y_top_abs = y_top + rows.min() * 25.4 / DPI
    y_bot_abs = y_top + rows.max() * 25.4 / DPI
    up_rows = rows[(y_top + rows * 25.4 / DPI) < mid]
    lo_rows = rows[(y_top + rows * 25.4 / DPI) >= mid]
    if len(up_rows) == 0 or len(lo_rows) == 0:
        return None
    up_bot = y_top + up_rows.max() * 25.4 / DPI
    lo_top = y_top + lo_rows.min() * 25.4 / DPI
    pitch = (lo['base'] - up['base']) / PT
    return dict(pitch_mm=round(pitch, 2), gap_mm=round(lo_top - up_bot, 2),
                up_ink_bottom=round(up_bot, 3), lo_ink_top=round(lo_top, 3))


results = {'条目2_1to2': [], '条目to条目': [], '判断题': []}

# ---------- ① 条目2 (1)→(2) ----------
p1 = doc[0]
img1 = render(p1)
L1 = lines_of(p1)
for i, l in enumerate(L1):
    if l['text'].startswith('(1)') and '字母表示法' in l['text']:
        # 下行 (2)
        for j in range(i + 1, len(L1)):
            if L1[j]['text'].startswith('(2)'):
                r = ink_gap(img1, l, L1[j])
                r.update(page=1, up=l['text'][:20], lo=L1[j]['text'][:20])
                results['条目2_1to2'].append(r)
                break
        break

# ---------- ② 条目→条目 6 对 ----------
# 条目号行＝纯 "N." 行；按页/栏聚合，取相邻两条目号行之间的最后一行内容
def find_tiaomu(L):
    return [l for l in L if l['text'].strip() in ('1.', '2.', '3.', '4.')]


for pno in (1, 2):
    page = doc[pno - 1]
    img = render(page)
    L = lines_of(page)
    heads = find_tiaomu(L)
    # 分栏
    for col, xlo, xhi in (('L', 0, 297), ('R', 297, 595)):
        colh = [h for h in heads if xlo <= h['bbox'][0] < xhi]
        colh.sort(key=lambda h: h['bbox'][1])
        for k in range(len(colh) - 1):
            hi = colh[k + 1]
            # 上一行＝紧邻 hi 上方的非条目号行
            above = [l for l in L if l['bbox'][3] <= hi['bbox'][1] + 1 and xlo <= l['bbox'][0] < xhi
                     and l['text'].strip() not in ('1.', '2.', '3.', '4.')]
            above.sort(key=lambda l: l['bbox'][3])
            if not above:
                continue
            up = above[-1]
            r = ink_gap(img, up, hi)
            if r:
                r.update(page=pno, col=col, up=up['text'][:16], lo=hi['text'].strip())
                results['条目to条目'].append(r)

# ---------- ③ 相邻判断题缝 ----------
for pno in (1, 2, 3):
    page = doc[pno - 1]
    img = render(page)
    L = lines_of(page)
    # 每个【诊断分析】块内找 (1) 与 (2) 行
    zhen_idx = [i for i, l in enumerate(L) if '【诊断分析】' in l['text']]
    for zi in zhen_idx:
        xlo, xhi = L[zi]['bbox'][0], L[zi]['bbox'][2]
        seg = [(i, l) for i, l in enumerate(L) if l['bbox'][1] >= L[zi]['bbox'][1] - 2
               and xlo - 2 <= l['bbox'][0] and l['bbox'][0] < xhi + 2]
        l2 = None
        for i, l in seg:
            if l['text'].startswith('(2)'):
                l2 = (i, l)
                break
        if not l2:
            continue
        i2, lo = l2
        above = [(i, l) for i, l in seg if i < i2]
        if not above:
            continue
        _, up = above[-1]
        r = ink_gap(img, up, lo)
        if r:
            r.update(page=pno, up=up['text'][:20], lo=lo['text'][:20])
            results['判断题'].append(r)

print('=== ① 条目2 (1)→(2) ===')
for r in results['条目2_1to2']:
    print(f"p{r['page']} pitch={r['pitch_mm']} 墨隙={r['gap_mm']} ｜ {r['up']} → {r['lo']}")
print('=== ② 条目→条目 6 对 ===')
for r in results['条目to条目']:
    print(f"p{r['page']}{r['col']} pitch={r['pitch_mm']} 墨隙={r['gap_mm']} ｜ …{r['up']} → {r['lo']}")
print('=== ③ 相邻判断题缝 ===')
for r in results['判断题']:
    print(f"p{r['page']} pitch={r['pitch_mm']} 墨隙={r['gap_mm']} ｜ …{r['up']} → {r['lo']}")

with open(os.path.join(BASE, 'm_片B_缝_result.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print('saved m_片B_缝_result.json')
