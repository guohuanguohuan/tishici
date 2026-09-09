# -*- coding: utf-8 -*-
"""片C #29 抽点 v3：600dpi ink 两侧墨隙（墨列 run 法：取与目标盒重叠的墨 run 为核心，
左右隙＝到相邻 run 的空白宽）。用法：_spot_ink3.py <pdf> <标签> <page> <y0> <y1> <x0> <x1> <name>"""
import sys
import numpy as np
import pymupdf
from PIL import Image

DPI = 600


def runs_of(cols):
    out = []
    s = None
    for i, v in enumerate(cols):
        if v and s is None:
            s = i
        if not v and s is not None:
            out.append((s, i - 1))
            s = None
    if s is not None:
        out.append((s, len(cols) - 1))
    return out


def measure(doc, pno, y0, y1, x0, x1, name):
    page = doc[pno - 1]
    clip = pymupdf.Rect(x0 - 40, y0 - 1.5, x1 + 40, y1 + 1.5)
    pix = page.get_pixmap(dpi=DPI, clip=clip)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')
    a = np.array(im) < 128
    cols = a.any(axis=0)
    rs = runs_of(cols)
    px0 = (x0 - clip.x0) / 72 * DPI
    px1 = (x1 - clip.x0) / 72 * DPI
    # 合并相邻 run（≤3px 缝）
    merged = []
    for s, e in rs:
        if merged and s - merged[-1][1] <= 3:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    idx = [i for i, (s, e) in enumerate(merged) if e >= px0 - 2 and s <= px1 + 2]
    if not idx:
        print(f'{name}: 核心 run 未找到')
        return
    i0, i1 = idx[0], idx[-1]
    core = (merged[i0][0], merged[i1][1])
    gl = (core[0] - merged[i0 - 1][1]) / DPI * 25.4 if i0 > 0 else None
    gr = (merged[i1 + 1][0] - core[1]) / DPI * 25.4 if i1 + 1 < len(merged) else None
    wmm = (core[1] - core[0] + 1) / DPI * 25.4
    print(f'{name}: 核心墨宽 {wmm:.2f}mm  左墨隙 {gl and round(gl, 2)}mm  右墨隙 {gr and round(gr, 2)}mm')


if __name__ == '__main__':
    pdf, label = sys.argv[1], sys.argv[2]
    doc = pymupdf.open(pdf)
    print(f'== {label} ==')
    args = sys.argv[3:]
    for i in range(0, len(args), 6):
        measure(doc, int(args[i]), float(args[i + 1]), float(args[i + 2]),
                float(args[i + 3]), float(args[i + 4]), args[i + 5])
