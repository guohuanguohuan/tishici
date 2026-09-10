# -*- coding: utf-8 -*-
"""H3 任务1：全品导学案 p04-p07 页码块复测定档（14.176 px/mm 水平，垂直同假定，验块高7.8反证）。
输出：块宽/块高/块四缘距纸边/数字 ink bbox/数字墨高/竖笔宽/灰度/数字距块左右缘。"""
import numpy as np
from PIL import Image
from scipy import ndimage

PXMM = 14.176
REF = r'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/%s.png'

for tag in ('p04', 'p05', 'p06', 'p07'):
    g = np.asarray(Image.open(REF % tag).convert('L')).astype(np.int16)
    H, W = g.shape
    # 灰块：像素灰 221±12（DDDDDD），限定下 1/4 页
    sub = g[H * 3 // 4:, :]
    lab, n = ndimage.label((np.abs(sub - 221) <= 12), structure=np.ones((3, 3)))
    print(f'== {tag} size={W}x{H} ({W/PXMM:.1f}x{H/PXMM:.1f}mm) 灰块候选 n={n}')
    for sl in ndimage.find_objects(lab):
        ys, xs = sl
        h = ys.stop - ys.start
        w = xs.stop - xs.start
        if w < 100 or h < 40:
            continue
        y0, y1, x0, x1 = ys.start + H * 3 // 4, ys.stop + H * 3 // 4, xs.start, xs.stop
        print(f'   块 px x[{x0},{x1}) y[{y0},{y1})  → {w/PXMM:.2f}×{h/PXMM:.2f}mm '
              f'左缘{x0/PXMM:.2f} 右缘距纸右{(W-x1)/PXMM:.2f} 顶距纸顶{y0/PXMM:.2f} 底距纸底{(H-y1)/PXMM:.2f}')
        # 数字：块内深墨
        seg = g[y0:y1, x0:x1]
        dark = seg < 128
        if not dark.any():
            print('     (块内无深墨)'); continue
        dys, dxs = np.nonzero(dark)
        nx0, nx1 = dxs.min(), dxs.max() + 1
        ny0, ny1 = dys.min(), dys.max() + 1
        num = seg[ny0:ny1, nx0:nx1]
        vals = num[num < 200]
        # 竖笔宽：数字区域每行的水平连通 run 宽度众数
        from collections import Counter
        runs = []
        for r in range(num.shape[0]):
            row = num[r] < 128
            c = 0
            for v in row:
                if v: c += 1
                elif c: runs.append(c); c = 0
            if c: runs.append(c)
        rc = Counter(runs).most_common(4)
        print(f'    数字 ink x[{x0+nx0},{x0+nx1}) y[{y0+ny0},{y0+ny1}) 高{ny1-ny0}px={ (ny1-ny0)/PXMM:.2f}mm '
              f'宽{nx1-nx0}px 墨灰min{vals.min()} 中位{int(np.median(vals))} 距块左{nx0/PXMM:.2f} 距块右{(x1-x0-nx1)/PXMM:.2f}')
        print(f'    竖笔run众数 {rc}')
