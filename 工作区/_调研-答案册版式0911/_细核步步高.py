# -*- coding: utf-8 -*-
"""看板六十九遗留「步步高缩进 ≈150–170 待细核」。
方法与六十九同构：灰阈<120 → 逐行首墨列 → 10px 分桶；
增强：先按 x 投影分栏（答案页为多栏，绝对 px 受栏位影响，栏内相对量才可比），
每行输出首墨列（栏内相对 / 全图绝对）、右缘、行高，另测行心偏移以判标题居中。
用法:
  python _细核步步高.py bubugao_ans_p14.jpg --y0 60 --y1 1570
  python _细核步步高.py quanpin_ans_p1.jpg --y0 250 --y1 1700   # 复核全品基准70/100
"""
import argparse
import numpy as np
from PIL import Image

THR = 120   # 灰阈
BIN = 10    # 分桶宽


def denoise(ink):
    """去孤立噪点(JPEG蝇斑)：3x3 邻域墨邻居<3 的剔掉。"""
    p = np.pad(ink, 1)
    n = np.zeros_like(p, dtype=np.int16)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                n += np.roll(np.roll(p, dy, 0), dx, 1)
    return ink & (n[1:-1, 1:-1] >= 3)


def split_cols(ink, mingap=18, island=8, minw=60):
    """x 投影找栏：on-段之间空隙>mingap 分栏，栏内 ≤island 的窄岛(竖虚线)并掉。"""
    cnt = ink.sum(axis=0)
    xs = np.where(cnt > 2)[0]
    if len(xs) == 0:
        return []
    runs, s, p = [], xs[0], xs[0]
    for x in xs[1:]:
        if x - p > 1:
            runs.append([s, p]); s = x
        p = x
    runs.append([s, p])
    merged = [runs[0]]
    for a, b in runs[1:]:
        if a - merged[-1][1] <= island:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return [(a, b) for a, b in merged if b - a >= minw]


def lines_of(ink, gap=5, minh=6):
    """逐行：空白行数>gap 断行；行高<minh 丢弃。"""
    rows = ink.any(axis=1)
    ys = np.where(rows)[0]
    if len(ys) == 0:
        return []
    segs, s, p = [], ys[0], ys[0]
    for y in ys[1:]:
        if y - p > gap:
            segs.append((s, p)); s = y
        p = y
    segs.append((s, p))
    out = []
    for y0, y1 in segs:
        sub = ink[y0:y1 + 1]
        xs = np.where(sub.any(axis=0))[0]
        if len(xs) == 0:
            continue
        h = int(sub.any(axis=1).sum())
        if h < minh:
            continue
        out.append(dict(y0=int(y0), y1=int(y1), left=int(xs[0]),
                        right=int(xs[-1]), h=h))
    return out


ap = argparse.ArgumentParser()
ap.add_argument('img')
ap.add_argument('--y0', type=int, default=0)
ap.add_argument('--y1', type=int, default=10 ** 9)
ap.add_argument('--x0', type=int, default=0)
ap.add_argument('--x1', type=int, default=10 ** 9)
a = ap.parse_args()

g = np.asarray(Image.open(a.img).convert('L'))
ink = g < THR
raw = int(ink.sum())
ink = denoise(ink)
H, W = ink.shape
body = ink.copy()
body[:a.y0] = False
body[a.y1:] = False
cols = split_cols(body)
cols = [(max(l, a.x0), min(r, a.x1)) for l, r in cols if min(r, a.x1) - max(l, a.x0) > 60]
print(f'图 {a.img} {W}x{H} | 墨点 灰阈<{THR}: 前{raw} 去噪后{int(ink.sum())} | 正文y[{a.y0},{a.y1}]')
print(f'栏数 {len(cols)}: ' + '  '.join(f'栏{i}:x[{l},{r}]w{r - l}' for i, (l, r) in enumerate(cols, 1)))
for ci, (l, r) in enumerate(cols, 1):
    ls = lines_of(body[:, l:r + 1])
    hist = {}
    for e in ls:
        b = e['left'] // BIN * BIN
        hist[b] = hist.get(b, 0) + 1
    hs = sorted(e['h'] for e in ls)
    medh = hs[len(hs) // 2] if hs else 0
    print(f'\n== 栏{ci} x[{l},{r}] 行数{len(ls)} 行高中位{medh}px ==')
    print('首墨列(栏内相对)10px桶: ' +
          '  '.join(f'{b:3d}-{b + 9:3d}:{n}' for b, n in sorted(hist.items())))
    print('逐行: y范围 | 相对L 绝对L | R h(行高px)')
    for e in ls:
        print(f"y{e['y0']:>4}-{e['y1']:<4} | L{e['left']:>3}/abs{l + e['left']:>4} | R{e['right']:>3} h{e['h']:>2}")
