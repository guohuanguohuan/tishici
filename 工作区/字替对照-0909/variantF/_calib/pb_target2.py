# -*- coding: utf-8 -*-
"""P-B 标定 v2：全品 p07 右栏课堂评价题号 1.–5. 真迹竖笔（native px 口径）。
题号区：x≈1090–1180、y≈300–2300（目检定位）。"""
import numpy as np
from PIL import Image
from scipy import ndimage
from collections import Counter

im = np.asarray(Image.open('C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/p07.png').convert('L'))
ink = im < 128

# 只取题号列窄带（题号数字右邻「．」在 x≈1150；题干汉字从 x≈1180 起）
band = ink[280:2320, 1080:1170]
lab, n = ndimage.label(band)
comps = []
for i in range(1, n + 1):
    m = lab == i
    ys, xs = np.where(m)
    h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
    if h < 25:
        continue
    comps.append((xs.min() + 1080, ys.min() + 280, w, h, m, ys.min(), xs.min()))
comps.sort(key=lambda c: c[1])
print('候选组件：')
stems = []
for x0, y0, w, h, m, ry, rx in comps:
    sub = band[ry:ry + h, rx:rx + w]
    runs = []
    for r in range(sub.shape[0]):
        xs2 = np.flatnonzero(sub[r])
        if len(xs2) == 0:
            continue
        for s in np.split(xs2, np.where(np.diff(xs2) > 1)[0] + 1):
            runs.append(len(s))
    cnt = Counter(runs)
    med = sorted(runs)[len(runs) // 2]
    mode = cnt.most_common(1)[0]
    print(f'  x{x0} y{y0} {w}x{h} 竖笔中位{med} 众数{mode}')
    stems.append(med)
stems = [s for s in stems if 1 <= s <= 12]
print(f'全品题号竖笔中位 = {sorted(stems)[len(stems)//2] if stems else -1}px (n={len(stems)}) 值分布 {Counter(stems)}')
