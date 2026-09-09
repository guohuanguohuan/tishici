# -*- coding: utf-8 -*-
"""P-B 标定：全品 p07 课堂评价题号真迹竖笔 vs 我方 E 版题号竖笔（同 14.17px/mm 口径）。
全品侧＝导学案页图 p07.png（2977×4176 native）；我方侧＝variantE/main.pdf rawdict 定位 11.4pt 数字后 360dpi 重渲。
输出两侧竖笔中位 → 与 NSC-w500/600/700 探针值（6/7/8px）比对定档。"""
import pymupdf
import numpy as np
from collections import Counter
from scipy import ndimage
from PIL import Image


def pil_open(p):
    return Image.open(p)

QPP = 'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/p07.png'


def stem_mode(band):
    runs = []
    for r in range(band.shape[0]):
        xs = np.flatnonzero(band[r])
        if len(xs) == 0:
            continue
        for s in np.split(xs, np.where(np.diff(xs) > 1)[0] + 1):
            runs.append(len(s))
    if not runs:
        return -1
    return Counter(runs).most_common(1)[0][0]


def measure_crop(band):
    """字形高度带内（25%–90%）竖笔众数。"""
    h = band.shape[0]
    return stem_mode(band[int(h * 0.25): int(h * 0.9)])


# ---- 全品侧 ----
im = np.asarray(pil_open(QPP).convert('L'))
ink = im < 128
# 课堂评价在 p07 下半：找左侧栏（版心左≈249px）附近的数字组件
lab, n = ndimage.label(ink[:, :1200])
comps = []
for i in range(1, n + 1):
    m = lab == i
    ys, xs = np.where(m)
    h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
    if not (30 <= h <= 46 and 8 <= w <= 34):
        continue
    if len(ys) < 0.25 * h * w:      # 墨占比过低（噪声）
        continue
    if ys.min() < 2000:             # 只看下半页（课堂评价区）
        continue
    comps.append((xs.min(), ys.min(), xs.max(), ys.max(), h, w))
comps.sort(key=lambda c: (c[1], c[0]))
print('全品 p07 候选数字组件（下半页，h30-46）：')
qp_stems = []
for x0, y0, x1, y1, h, w in comps[:12]:
    st = measure_crop(ink[y0:y1 + 1, x0:x1 + 1])
    qp_stems.append(st)
    print(f'  x{x0} y{y0} {w}x{h} 竖笔{st}px')
qp_stems = [s for s in qp_stems if s > 0]
qp_med = sorted(qp_stems)[len(qp_stems) // 2] if qp_stems else -1
print(f'全品题号竖笔中位 = {qp_med}px (n={len(qp_stems)})')

# ---- 我方 E 版 ----
doc = pymupdf.open('../variantE/main.pdf')
my_stems = []
for pno, page in enumerate(doc, 1):
    for blk in page.get_text('rawdict')['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                if not (11.0 <= sp['size'] <= 11.8):
                    continue
                for ch in sp.get('chars', []):
                    if ch['c'].isdigit():
                        bb = ch['bbox']
                        pm = page.get_pixmap(dpi=360, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(*bb))
                        arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
                        st = measure_crop(arr < 128)
                        if st > 0:
                            my_stems.append(st)
print(f'我方 E 题号数字竖笔 = {sorted(my_stems)} 中位 {sorted(my_stems)[len(my_stems)//2] if my_stems else -1}px (n={len(my_stems)})')
print()
print('NSC 探针（11.4pt@360dpi）：w500≈6 / w600≈7 / w700≈8')
for w, s in (('w500', 6), ('w600', 7), ('w700', 8)):
    print(f'  {w}: |{s}-{qp_med}| = {abs(s - qp_med)}')
