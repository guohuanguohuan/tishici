# -*- coding: utf-8 -*-
"""P-B 标定测量 v2：逐行＝单字形。字形高度带内取水平墨行程众数＝竖笔粗（360dpi＝14.17px/mm 全品 px 口径）。
目标：全品题号竖笔 6px；残差取小者定档。"""
import pymupdf
import numpy as np
from collections import Counter

doc = pymupdf.open('_calib/pb_stem_probe.pdf')
page = doc[0]
pm = page.get_pixmap(dpi=360, colorspace=pymupdf.csGRAY)
arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
ink = arr < 128

row_has = ink.any(axis=1)
rows, st = [], None
for i, d in enumerate(row_has):
    if d and st is None:
        st = i
    elif not d and st is not None:
        rows.append((st, i)); st = None
if st is not None:
    rows.append((st, len(row_has)))

names = ['w500-1', 'w500-4', 'w500-5', 'w600-1', 'w600-4', 'w600-5',
         'w700-1', 'w700-4', 'w700-5']
print(f'rows={len(rows)}')
res = {}
for (a, b), nm in zip(rows, names):
    h = b - a
    band = ink[a + int(h * 0.25): a + int(h * 0.9)]   # 中下部：避开旗/横笔
    runs = []
    for r in range(band.shape[0]):
        xs = np.flatnonzero(band[r])
        if len(xs) == 0:
            continue
        for s in np.split(xs, np.where(np.diff(xs) > 1)[0] + 1):
            runs.append(len(s))
    cnt = Counter(runs)
    mode, freq = cnt.most_common(1)[0]
    res[nm] = mode
    print(f'{nm:8s} h={h:3d}px 竖笔众数={mode}px(×{freq}/{len(runs)}) 分布{sorted(cnt.items())[:6]}')

print()
for w in ('500', '600', '700'):
    stems = [res[f'w{w}-{d}'] for d in '145']
    med = sorted(stems)[1]
    print(f'NSC-w{w}: 竖笔中位 {med}px  对 6px 目标残差 {abs(med - 6)}')
