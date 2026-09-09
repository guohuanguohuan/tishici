# -*- coding: utf-8 -*-
"""P-B 标定 v3：比值法定档。
全品 p07（360dpi 扫描）：课堂评价题号 1.-5. 竖笔 vs 同版正文汉字竖笔（同阈值，比值消扫描阈值偏差）
  × 我方正文（variantE FZShuSong 10.09pt @360dpi）竖笔 = 我方题号目标 px → 对 w500/600/700(6/7/8) 取残差小者，平手偏重。
题号位置：右栏悬挂，x∈[1450,1620]，y 中心约 500/1100/1700/2355/2870（目检 _p07_nums_col.png 定出）。"""
import pymupdf
import numpy as np
from collections import Counter
from scipy import ndimage
from PIL import Image

QPP = 'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/p07.png'
EPDF = '../variantE/main.pdf'
NUM_Y = [500, 1100, 1700, 2355, 2870]


def stem_runs(band):
    runs = []
    for r in range(band.shape[0]):
        xs = np.flatnonzero(band[r])
        if len(xs) == 0:
            continue
        for s in np.split(xs, np.where(np.diff(xs) > 1)[0] + 1):
            runs.append(len(s))
    return runs


def stem_mode(band, cap=9):
    runs = [x for x in stem_runs(band) if 1 <= x <= cap]
    if not runs:
        return -1
    return Counter(runs).most_common(1)[0][0]


def glyph_stem(band_full):
    h = band_full.shape[0]
    return stem_mode(band_full[int(h * 0.25): int(h * 0.9)])


# ---------- 全品侧 ----------
im = np.asarray(Image.open(QPP).convert('L'))
print(f'全品 p07 {im.shape[1]}x{im.shape[0]}')
num_stems = {}
for thr in (128, 170):
    ink = im < thr
    lab, n = ndimage.label(ink[:, :1700])
    stems = []
    boxes = []
    for i in range(1, n + 1):
        m = lab == i
        ys, xs = np.where(m)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        h, w = y1 - y0 + 1, x1 - x0 + 1
        if not (30 <= h <= 60 and 8 <= w <= 50):
            continue
        yc = (y0 + y1) / 2
        if not (1450 <= x0 <= 1620):
            continue
        for c in NUM_Y:
            if abs(yc - c) <= 60:
                st = glyph_stem(m)
                if st > 0:
                    stems.append(st)
                    boxes.append((int(y0), x0, w, h, st))
                break
    num_stems[thr] = stems
    print(f'全品题号 t{thr}: 逐字 {stems} 中位 {sorted(stems)[len(stems)//2] if stems else -1}'
          f'  (n={len(stems)})')
    for b in boxes:
        print(f'    y{b[0]} x{b[1]} {b[2]}x{b[3]} 竖笔{b[4]}px')

# 正文汉字：两个对照区（左栏素养小络段落 / 右栏第5题题干），逐行带内众数
BODY_REGIONS = [('左栏素养段', 250, 1432, 3280, 3620), ('右栏第5题干', 1545, 2728, 2940, 3160)]
body_stems = {}
for thr in (128, 170):
    ink = im < thr
    all_modes = []
    for nm, x0, x1, y0, y1 in BODY_REGIONS:
        reg = ink[y0:y1, x0:x1]
        row_has = reg.any(axis=1)
        lines, st = [], None
        for i, d in enumerate(row_has):
            if d and st is None:
                st = i
            elif not d and st is not None:
                lines.append((st, i)); st = None
        if st is not None:
            lines.append((st, len(row_has)))
        modes = []
        for a, b in lines:
            if b - a < 25:
                continue
            h = b - a
            mm = stem_mode(reg[a + int(h * 0.25): a + int(h * 0.9)])
            if mm > 0:
                modes.append(mm)
        med = sorted(modes)[len(modes) // 2] if modes else -1
        print(f'全品正文[{nm}] t{thr}: 逐行众数 {modes} 中位 {med}px (n={len(modes)})')
        all_modes += modes
    body_stems[thr] = sorted(all_modes)[len(all_modes) // 2]
print(f'全品正文合并中位: t128={body_stems[128]}px t170={body_stems[170]}px')

# ---------- 我方侧 ----------
doc = pymupdf.open(EPDF)
my_body, my_num = [], []
for page in doc:
    for blk in page.get_text('rawdict')['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                sz = sp['size']
                for ch in sp.get('chars', []):
                    c = ch['c']
                    bb = ch['bbox']
                    is_body = 10.0 <= sz <= 10.2 and '\u4e00' <= c <= '\u9fff'
                    is_num = 11.0 <= sz <= 11.8 and c.isdigit()
                    if not (is_body or is_num):
                        continue
                    pm = page.get_pixmap(dpi=360, colorspace=pymupdf.csGRAY,
                                         clip=pymupdf.Rect(*bb))
                    arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
                    st = glyph_stem(arr < 128)
                    if st > 0:
                        (my_body if is_body else my_num).append(st)

mb = sorted(my_body); mn = sorted(my_num)
my_body_med = mb[len(mb) // 2]
my_num_med = mn[len(mn) // 2]
print(f'我方正文(FZShuSong 10.09pt) 逐字 {my_body} 中位 {my_body_med}px (n={len(mb)})')
print(f'我方E现役题号 逐字 {my_num} 中位 {my_num_med}px (n={len(mn)})')

print()
print('==== 比值法 ====')
for thr in (128, 170):
    qn = sorted(num_stems[thr])[len(num_stems[thr]) // 2]
    r = qn / body_stems[thr]
    tgt = r * my_body_med
    print(f't{thr}: 全品题号{qn}/正文{body_stems[thr]} = {r:.3f} × 我方正文{my_body_med}px → 目标 {tgt:.2f}px')
    for w, s in ((500, 6), (600, 7), (700, 8)):
        print(f'   NSC-w{w} {s}px 残差 {abs(s - tgt):.2f}')
