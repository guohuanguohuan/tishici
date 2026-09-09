# -*- coding: utf-8 -*-
"""P-B 终标定：全品题号五数字真迹 vs NSC w500/600/700 同字形（1-5）对比。
全品侧＝p07 五题号 bbox（组件定位+目检双确认）；我方侧＝pb_stem_probe2.pdf 360dpi。
指标：①竖笔众数（字形高 25%-90% 带内水平墨行程众数）②墨密度（ink/bbox）。
定档规则（用户拍板）：对全品侧目标残差取小者；平手偏重档。"""
import subprocess
import pymupdf
import numpy as np
from collections import Counter
from PIL import Image

QPP = 'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/p07.png'
QP_DIG = {'1': (1547, 491, 1562, 527), '2': (1545, 1113, 1569, 1150),
          '3': (1545, 1789, 1569, 1826), '4': (1545, 2448, 1569, 2484),
          '5': (1545, 2982, 1569, 3018)}


def runs_of(band, cap=12):
    out = []
    for r in range(band.shape[0]):
        xs = np.flatnonzero(band[r])
        if len(xs) == 0:
            continue
        for s in np.split(xs, np.where(np.diff(xs) > 1)[0] + 1):
            if 1 <= len(s) <= cap:
                out.append(len(s))
    return out


def metrics(band):
    """band＝tight 字形二值图 → (竖笔众数, 密度)"""
    h, w = band.shape
    rr = runs_of(band[int(h * 0.25): int(h * 0.9)])
    stroke = Counter(rr).most_common(1)[0][0] if rr else -1
    return stroke, band.sum() / (h * w)


def render_pdf_pages(pdf, dpi=360):
    doc = pymupdf.open(pdf)
    out = []
    for page in doc:
        pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
        arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
        out.append(arr)
    return out


# ---- 我方探针：编译＋逐字形测量 ----
subprocess.run(['xelatex', '-interaction=nonstopmode', 'pb_stem_probe2.tex'],
               cwd='.', capture_output=True, timeout=120)
pages = render_pdf_pages('pb_stem_probe2.pdf')
arr = pages[0]
ink0 = arr < 128
row_has = ink0.any(axis=1)
rows, st = [], None
for i, d in enumerate(row_has):
    if d and st is None:
        st = i
    elif not d and st is not None:
        rows.append((st, i)); st = None
if st is not None:
    rows.append((st, len(row_has)))
rows = [r for r in rows if r[1] - r[0] >= 30]   # 去掉碎点
assert len(rows) in (15, 16), f'probe rows={len(rows)}'
if len(rows) == 16:      # 末行＝article 页码（页面底部），丢弃
    assert rows[15][0] - rows[14][1] > 50
    rows = rows[:15]

names = [f'w{w}-{d}' for w in (500, 600, 700) for d in '12345']
my = {}
for (a, b), nm in zip(rows, names):
    sub = ink0[a:b]
    ys, xs = np.where(sub)
    tight = sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s, d = metrics(tight)
    my[nm] = (s, d, tight.shape[1], tight.shape[0])
    print(f'我方 {nm}: {tight.shape[1]}x{tight.shape[0]} 竖笔{s}px 密度{d:.3f}')

# ---- 全品侧 ----
im = np.asarray(Image.open(QPP).convert('L'))
qp = {}
for dgt, (x0, y0, x1, y1) in QP_DIG.items():
    for thr in (128, 155, 170, 185):
        reg = im[y0 - 2:y1 + 3, x0 - 2:x1 + 3] < thr
        ys, xs = np.where(reg)
        tight = reg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        s, d = metrics(tight)
        qp[(dgt, thr)] = (s, d)
        print(f'全品 {dgt} t{thr}: {tight.shape[1]}x{tight.shape[0]} 竖笔{s}px 密度{d:.3f}')

print()
print('==== 对比（密度差 / 竖笔差，逐字求和）====')
best = None
for w in (500, 600, 700):
    for thr in (128, 155, 170, 185):
        dd = sum(abs(my[f'w{w}-{g}'][1] - qp[(g, thr)][1]) for g in '12345')
        ds = sum(abs(my[f'w{w}-{g}'][0] - qp[(g, thr)][0]) for g in '12345')
        print(f'w{w} vs 全品t{thr}: Σ密度差 {dd:.3f}  Σ竖笔差 {ds}')
        if best is None or dd < best[0]:
            best = (dd, w, thr, ds)
print(f'密度最优: w{best[1]} (对全品 t{best[2]}, Σ密度差 {best[0]:.3f}, Σ竖笔差 {best[3]})')
