# -*- coding: utf-8 -*-
"""p04-p06 目标行连通域明细（供全品靶复测：cap 高/脚本比/分式/减号）。只读。"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

REF = 'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/%s.png'
PXMM = 14.176


def comps(page, x0, x1, y0, y1, thr=170, min_h=3, min_w=2, merge_boxes=True):
    gray = np.asarray(Image.open(REF % page).convert('L')).astype(np.uint8)
    sub = gray[y0:y1, x0:x1] < thr
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    objs = ndimage.find_objects(lab)
    out = []
    for sl in objs:
        ys, xs = sl
        h = ys.stop - ys.start
        w = xs.stop - xs.start
        if h < min_h or w < min_w:
            continue
        out.append([xs.start + x0, xs.stop + x0, ys.start + y0, ys.stop + y0])
    out.sort()
    if merge_boxes:
        # 按 x 重叠合并（同一字符/符号的上下部件）
        prev_change = True
        while prev_change:
            prev_change = False
            merged = []
            for c in out:
                if merged and not (c[0] > merged[-1][1] - 1):
                    merged[-1][0] = min(merged[-1][0], c[0])
                    merged[-1][1] = max(merged[-1][1], c[1])
                    merged[-1][2] = min(merged[-1][2], c[2])
                    merged[-1][3] = max(merged[-1][3], c[3])
                    prev_change = True
                else:
                    merged.append(list(c))
            out = merged
    return out


def report(page, x0, x1, y0, y1, **kw):
    cs = comps(page, x0, x1, y0, y1, **kw)
    print(f'== {page} x[{x0},{x1}] y[{y0},{y1}] : {len(cs)} comps')
    for c in cs:
        w = c[1] - c[0]; h = c[3] - c[2]
        print(f'  x{c[0]:>5}-{c[1]:<5} y{c[2]:>5}-{c[3]:<5} w{w:>4} h{h:>4}')
    return cs


if __name__ == '__main__':
    a = sys.argv[1:]
    if a:
        report(a[0], int(a[1]), int(a[2]), int(a[3]), int(a[4]))
    else:
        # 目标行：先用粗窗看行带位置
        for page, x0, x1, y0, y1 in (
            ('p06', 240, 1490, 1590, 1700),   # 例2 行 ABCDEF-A1B1...
            ('p05', 1540, 2790, 3300, 3600),  # 例1(2) 长方体行
            ('p06', 1540, 2790, 3440, 3600),  # 例3 题干行
            ('p06', 1540, 2790, 3700, 3870),  # 例3 选项行
        ):
            report(page, x0, x1, y0, y1)
