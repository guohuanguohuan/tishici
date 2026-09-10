# -*- coding: utf-8 -*-
"""参考页（全品 PNG）文本度量工具：行检测 / 字切分 / 间距统计。
只读参考图；输出数字与裁片到 _tmp审美审计0909。"""
import numpy as np
from PIL import Image
from scipy import ndimage

PXMM = 14.176  # px per mm

def load_gray(path):
    return np.asarray(Image.open(path).convert('L')).astype(np.uint8)

def ink(gray, thr=170):
    return (gray < thr)

def find_columns(gray, thr=170):
    """返回 [(x0,x1), ...] 栏区（按纵向墨投影的空白分隔）。"""
    ik = ink(gray, thr)
    col = ik.sum(axis=0)
    # 平滑
    k = 9
    cs = np.convolve(col, np.ones(k) / k, mode='same')
    on = cs > 1.0
    # 找 run
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
    # 合并间距<20px 的 run，丢弃宽度<30px 的
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < 20:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(list(r))
    return [(a, b) for a, b in merged if b - a > 30]

def find_lines(ik, x0, x1, min_ink=3, min_h=8):
    """在栏内按行墨投影找文本行 band（y0,y1）。"""
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
    # 合并间距 <= 4px 的 band（同一行的上下部件）
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] <= 4:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(list(r))
    return [(a, b) for a, b in merged if b - a >= min_h]

def segment_chars(ik, y0, y1, x0, x1, min_w=4):
    """行带内按连通域 x 投影切字。返回 [(cx0,cx1,cy0,cy1)]。"""
    sub = ik[y0:y1, x0:x1]
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    if n == 0:
        return []
    objs = ndimage.find_objects(lab)
    comps = []
    for sl in objs:
        ys, xs = sl
        comps.append((xs.start, xs.stop, ys.start + y0, ys.stop + y0))
    # 按 x 重叠合并（同一字符的偏旁/部件）
    comps.sort()
    groups = []
    for c in comps:
        placed = False
        for g in groups:
            # x 区间重叠或距离 <=1px 视为同字
            if not (c[1] + 1 < g[0] or c[0] - 1 > g[1]):
                g[0] = min(g[0], c[0]); g[1] = max(g[1], c[1])
                g[2] = min(g[2], c[2]); g[3] = max(g[3], c[3])
                placed = True
                break
        if not placed:
            groups.append([c[0], c[1], c[2], c[3]])
    # 合并迭代至稳定
    changed = True
    while changed:
        changed = False
        out = []
        for g in sorted(groups):
            if out and not (g[0] > out[-1][1] + 1):
                out[-1][0] = min(out[-1][0], g[0]); out[-1][1] = max(out[-1][1], g[1])
                out[-1][2] = min(out[-1][2], g[2]); out[-1][3] = max(out[-1][3], g[3])
                changed = True
            else:
                out.append(g)
        groups = out
    return [g for g in groups if g[1] - g[0] >= min_w]

def line_metrics(img_path, x0, x1, y0=0, y1=None, thr=170, verbose=True, tag=''):
    gray = load_gray(img_path)
    if y1 is None:
        y1 = gray.shape[0]
    ik = ink(gray, thr)
    lines = find_lines(ik, x0, x1)
    lines = [(a, b) for a, b in lines if b > y0 and a < y1]
    res = dict(tag=tag, x0=x0, x1=x1, n_lines=len(lines), lines=[])
    heights = []
    for (a, b) in lines:
        segs = segment_chars(ik, a, b, x0, x1)
        if not segs:
            continue
        widths = [s[1] - s[0] for s in segs]
        hts = [s[3] - s[2] for s in segs]
        medw = np.median(widths)
        gaps = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]
        centers = [(segs[i][0] + segs[i][1]) / 2 for i in range(len(segs))]
        pitches = [centers[i + 1] - centers[i] for i in range(len(centers) - 1)]
        res['lines'].append(dict(y0=int(a), y1=int(b), n=len(segs),
                                 x_first=int(segs[0][0]), x_last=int(segs[-1][1]),
                                 medw=float(medw), medh=float(np.median(hts)),
                                 gaps=[float(g) for g in gaps], pitches=[float(p) for p in pitches],
                                 segs=[(int(s[0]), int(s[1]), int(s[2]), int(s[3])) for s in segs]))
        heights.append(np.median(hts))
    if verbose and len(res['lines']) > 1:
        yc = [(l['y0'] + l['y1']) / 2 for l in res['lines']]
        diffs = [round(b - a, 1) for a, b in zip(yc, yc[1:]) if 20 < b - a < 120]
        print(f'[{tag}] 行数={len(res["lines"])} 行距众数={sorted(set(diffs), key=diffs.count, reverse=True)[:5]}')
        print(f'  字高中位={np.median(heights):.1f}px = {np.median(heights)/PXMM:.2f}mm')
        allw = [s[1] - s[0] for l in res['lines'] for s in l['segs']]
        print(f'  字宽中位={np.median(allw):.1f}px = {np.median(allw)/PXMM:.2f}mm')
        allg = [g for l in res['lines'] for g in l['gaps']]
        allp = [p for l in res['lines'] for p in l['pitches']]
        print(f'  ink 间隙: 中位={np.median(allg):.1f}px p10={np.percentile(allg,10):.1f} p90={np.percentile(allg,90):.1f}')
        print(f'  字心距: 中位={np.median(allp):.1f}px = {np.median(allp)/PXMM:.2f}mm')
    return res

if __name__ == '__main__':
    import sys
    p = r'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/p05.png'
    gray = load_gray(p)
    print('page size', gray.shape)
    cols = find_columns(gray)
    print('columns:', cols)
