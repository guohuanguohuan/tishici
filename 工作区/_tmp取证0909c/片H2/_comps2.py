# -*- coding: utf-8 -*-
"""连通域测量（通用路径版）：给 360dpi 图与窗口，列组件 bbox。"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage


def comps_path(path, x0, x1, y0, y1, thr=170, min_h=2, min_w=2, merge=False):
    gray = np.asarray(Image.open(path).convert('L')).astype(np.uint8)
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
    if merge:
        changed = True
        while changed:
            changed = False
            merged = []
            for c in out:
                if merged and not (c[0] > merged[-1][1] - 1):
                    merged[-1][0] = min(merged[-1][0], c[0])
                    merged[-1][1] = max(merged[-1][1], c[1])
                    merged[-1][2] = min(merged[-1][2], c[2])
                    merged[-1][3] = max(merged[-1][3], c[3])
                    changed = True
                else:
                    merged.append(list(c))
            out = merged
    return out


def report(path, x0, x1, y0, y1, **kw):
    cs = comps_path(path, x0, x1, y0, y1, **kw)
    print(f'== {path.split("/")[-1]} x[{x0},{x1}] y[{y0},{y1}] : {len(cs)} comps')
    for c in cs:
        print(f'  x{c[0]:>5}-{c[1]:<5} y{c[2]:>5}-{c[3]:<5} w{c[1]-c[0]:>4} h{c[3]-c[2]:>4}')


if __name__ == '__main__':
    a = sys.argv
    report(a[1], int(a[2]), int(a[3]), int(a[4]), int(a[5]),
           merge=('--merge' in a), min_h=2, min_w=2)
