# -*- coding: utf-8 -*-
"""品牌0911 目验：测评卷 p2（偶页＝LE 页脚）300dpi 全页＋页脚特写裁图；
文字流抽取验证「羿郭工作室」在位；页脚墨区 bbox 越栏/出页检测。"""
import io
import sys

import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\测评卷\main.pdf'
OUT = r'C:\提示词\工作区\_tmp取证0909c\片I-裁5页码块0911\目验v10'
PT = 72 / 25.4
DPI = 300
PXMM = DPI / 25.4

d = pymupdf.open(SRC)
print('页数', d.page_count)
pg = d[1]  # p2＝偶页，LE 页脚
w = pg.rect.width / PT
h = pg.rect.height / PT
print(f'p2 尺寸 {w:.1f}×{h:.1f}mm')

# ① 全页 300dpi
pm = pg.get_pixmap(dpi=DPI)
full = OUT + r'\测评卷p2-品牌-300dpi.png'
pm.save(full)
print('wrote', full, pm.width, pm.height)

# ② 页脚带特写 300dpi（x 0–160mm，y 264–284mm）
clip = pymupdf.Rect(0 * PT, 264 * PT, 160 * PT, 284 * PT)
pm2 = pg.get_pixmap(dpi=DPI, clip=clip)
crop = OUT + r'\测评卷p2-页脚特写-品牌-300dpi.png'
pm2.save(crop)
print('wrote', crop, pm2.width, pm2.height)

# ③ 文字流：两页页脚区（y>260mm）含字验证
for pno in (0, 1):
    for b in d[pno].get_text('dict')['blocks']:
        for l in b.get('lines', []):
            y = l['bbox'][3] / PT
            if y > 260:
                txt = ''.join(s['text'] for s in l['spans'])
                fonts = {s['font'] for s in l['spans']}
                sizes = {round(s['size'], 2) for s in l['spans']}
                print(f'p{pno+1} 页脚行 y={y:.2f}mm x0={l["bbox"][0]/PT:.2f} '
                      f'x1={l["bbox"][2]/PT:.2f} | {txt!r} | {sorted(fonts)} | {sorted(sizes)}')

# ④ 像素级：页脚带墨区 bbox（阈 128），换算 mm，越栏/出页判定
import numpy as np
arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)[:, :, :3]
band = arr[int(264 * PXMM):int(284 * PXMM), :, :]
gray = band.min(axis=2)
ys, xs = np.where(gray < 128)
x0, x1 = xs.min() / PXMM, xs.max() / PXMM
y0, y1 = ys.min() / PXMM + 264, ys.max() / PXMM + 264
print(f'p2 页脚墨 bbox: x {x0:.2f}–{x1:.2f}mm  y {y0:.2f}–{y1:.2f}mm')
print(f'判定: 左缘≥8.9mm? {x0 >= 8.9 - 0.3}  越栏1右缘128.9mm? {x1 <= 128.9}  '
      f'越页右缘399.8mm? {x1 <= w}  越页底284.2mm? {y1 <= h}')

# ⑤ 「羿郭工作室」五字墨断言：LE 行中定位其像素列段（品牌位＝「卷」后、「高中数学」前）
d.close()
