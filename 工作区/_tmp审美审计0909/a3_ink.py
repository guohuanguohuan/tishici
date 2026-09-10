# -*- coding: utf-8 -*-
"""字重/墨密度专项：对给定图 + 栏区，逐字符量 竖笔宽(横切 run 众数)、墨覆盖率、字面 W×H。
用于「同字号同字」对比：我方 FZSSJW 10.09pt vs 全品 p05。"""
import numpy as np
from scipy import ndimage
import ref_tools as R

def char_stats(gray, ik, x0, x1, y0, y1):
    """单个字符区域（页面坐标）的墨统计。"""
    sub = ik[y0:y1, x0:x1]
    g = gray[y0:y1, x0:x1]
    n = sub.sum()
    if n == 0:
        return None
    h, w = sub.shape
    # 竖笔宽：每行取连续 ink run 长度，统计众数（去端帽行）
    runs = []
    for r in range(1, h - 1):
        row = sub[r]
        d = np.diff(np.concatenate(([0], row.view(np.int8), [0])))
        starts = np.where(d == 1)[0]; ends = np.where(d == -1)[0]
        for s, e in zip(starts, ends):
            runs.append(e - s)
    runs = np.array(runs)
    # 竖笔 run 长度分布众数（限制 2..15px）
    rr = runs[(runs >= 2) & (runs <= 18)]
    mode_v = float(np.bincount(rr).argmax()) if len(rr) else 0.0
    ink_gray = float(g[sub].mean())
    return dict(w=int(w), h=int(h), inkpx=int(n), cover=round(n / (w * h), 3),
                stroke_mode=mode_v, stroke_med=float(np.median(rr)) if len(rr) else 0.0,
                ink_gray=round(ink_gray, 1))

def scan_line(gray, ik, x0, x1, ya, yb, tag):
    segs = R.segment_chars(ik, ya, yb, x0, x1)
    segs = [(s[0] + x0, s[1] + x0, s[2], s[3]) for s in segs]
    print(f'-- {tag} 行 y=({ya},{yb}) 段数={len(segs)}')
    for s in segs:
        st = char_stats(gray, ik, s[0], s[1], s[2], s[3])
        print(f'   x=({s[0]},{s[1]}) y=({s[2]},{s[3]}) {st}')

def char_at(gray, ik, x, y, half=40, tag=''):
    st = char_stats(gray, ik, x - half, x + half, y - half, y + half)
    print(f'{tag} @({x},{y}) {st}')
    return st

if __name__ == '__main__':
    import sys
    # 参考 p05 左栏第一行（无标点纯汉字行）
    p = r'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/p05.png'
    gray = R.load_gray(p); ik = R.ink(gray)
    scan_line(gray, ik, 243, 1433, 278, 326, 'ref-p05-L-line1')
