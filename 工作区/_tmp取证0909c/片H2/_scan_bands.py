# -*- coding: utf-8 -*-
"""p04-p06 行带扫描：找 '高带'（含分式/上下标的行）与 'v2 目标串'（ABCD-A1B1C1D1）供裁片目检。
只读；输出 探/ 下 montage。"""
import numpy as np
from PIL import Image, ImageDraw

REF = 'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/%s.png'
PXMM = 14.176


def load_gray(p):
    return np.asarray(Image.open(p).convert('L')).astype(np.uint8)


def ink(gray, thr=170):
    return gray < thr


def find_lines(ik, x0, x1, min_ink=3, min_h=8):
    sub = ik[:, x0:x1]
    row = sub.sum(axis=1)
    on = row > min_ink
    runs = []
    s = None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        elif not v and s is not None:
            runs.append((s, i))
            s = None
    if s is not None:
        runs.append((s, len(on)))
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] <= 4:
            merged[-1] = [merged[-1][0], r[1]]
        else:
            merged.append(list(r))
    return [(a, b) for a, b in merged if b - a >= min_h]


def scan(pages, out_png):
    rows = []
    for tag in pages:
        gray = load_gray(REF % tag)
        ik = ink(gray)
        for x0, x1, col in ((243, 1433, 'L'), (1540, 2730, 'R')):
            lines = find_lines(ik, x0, x1)
            for (a, b) in lines:
                h = b - a
                if h < 50:
                    continue
                if 150 < a < 3900:
                    rows.append((tag, col, a, b, h))
    print('candidate high bands:', len(rows))
    for r in rows:
        print(r)
    # montage: crop each band full column width
    crops = []
    for tag, col, a, b, h in rows:
        im = Image.open(REF % tag).crop((240 if col == 'L' else 1537, max(0, a - 8), 1490 if col == 'L' else 2790, min(4176, b + 8)))
        crops.append((f'{tag} {col} y{a}-{b} h={h}', im))
    W = max(c.width for _, c in crops) + 8
    H = sum(c.height + 26 for _, c in crops) + 8
    canvas = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(canvas)
    y = 4
    for lab, c in crops:
        d.text((4, y), lab, fill=(200, 0, 0))
        y += 22
        canvas.paste(c, (4, y))
        y += c.height + 4
    canvas.save(out_png)
    print('saved', out_png, canvas.size)


if __name__ == '__main__':
    scan(('p04', 'p05', 'p06'), '探/high_bands.png')
