# -*- coding: utf-8 -*-
"""片C #34/#37 验证：×（TikZ）墨尺寸/笔画/括号带居中/基线；√ 字体归属。"""
import numpy as np
import pymupdf
from PIL import Image

PTMM = 72 / 25.4
DPI = 600
PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
doc = pymupdf.open(PDF)

print('== #37 √ 字体归属 ==')
sqrt_fonts = {}
for pno, page in enumerate(doc, 1):
    for blk in page.get_text('dict')['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk['lines']:
            for sp in ln['spans']:
                if '√' in sp['text']:
                    sqrt_fonts.setdefault(sp['font'], []).append((pno, sp['text'][:18]))
for f, arr in sqrt_fonts.items():
    print(f'  {f}: {len(arr)} 处 例：{arr[0]}')
print('  → FZSSJW 承载 √:', any('FZSSJW' in f for f in sqrt_fonts))

print()
print('== #34 × TikZ 墨几何 ==')
xs = []
for pno, page in enumerate(doc, 1):
    seen = set()
    for d in page.get_drawings():
        if d['fill'] is None:
            continue
        r = pymupdf.Rect(d['rect'])
        w, h = r.width / PTMM, r.height / PTMM
        if 2.2 < w < 2.6 and 2.2 < h < 2.6:
            key = (round(r.x0, 1), round(r.y0, 1), round(w, 2), round(h, 2))
            if key in seen:
                continue
            seen.add(key)
            xs.append((pno, r, w, h))
print(f'  × 墨盒实例 {len(xs)} 个')
for pno, r, w, h in xs:
    print(f'   p{pno} 墨 {w:.3f}×{h:.3f}mm  y[{r.y0:.2f},{r.y1:.2f}]')
if xs:
    ws = [w for _, _, w, _ in xs]; hs = [h for _, _, _, h in xs]
    print(f'  墨宽中位 {sorted(ws)[len(ws)//2]:.3f}mm 墨高中位 {sorted(hs)[len(hs)//2]:.3f}mm')

# 笔画宽：取第一个 × 的 600dpi 裁片，量水平 run 宽（45° 线：水平 run = 线宽×√2）
if xs:
    pno, r, w, h = xs[0]
    page = doc[pno - 1]
    clip = pymupdf.Rect(r.x0 - 2, r.y0 - 2, r.x1 + 2, r.y1 + 2)
    pix = page.get_pixmap(dpi=DPI, clip=clip)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')
    a = np.array(im) < 128
    hh = a.shape[0]
    runs = []
    for yy in range(int(hh * 0.3), int(hh * 0.7)):
        xs_ = np.where(a[yy])[0]
        if len(xs_) == 0:
            continue
        segs = []; s = xs_[0]; p = xs_[0]
        for x in xs_[1:]:
            if x == p + 1:
                p = x
            else:
                segs.append(p - s + 1); s = p = x
        segs.append(p - s + 1)
        runs.extend(segs)
    med_run_px = sorted(runs)[len(runs) // 2]
    stroke_mm = med_run_px / DPI * 25.4 / (2 ** 0.5)
    print(f'  首个 × 水平 run 中位 {med_run_px}px → 笔画 {stroke_mm:.3f}mm（0.4pt=0.141mm）')

# 括号带居中＋基线：找答案位 ×（在括号之间）与同行括号、√ 的 y 关系
print()
print('== #34 括号带居中与基线（p1 判断块1 (1)/(2) 答案位）==')
for pno in (1, 2, 3):
    page = doc[pno - 1]
    raw = page.get_text('rawdict')
    # 收集括号对与 × 墨盒
    for d in page.get_drawings():
        if d['fill'] is None:
            continue
        r = pymupdf.Rect(d['rect'])
        if 2.2 < r.width / PTMM < 2.6 and 2.2 < r.height / PTMM < 2.6:
            yc = (r.y0 + r.y1) / 2
            # 同行括号（半角 '(' ')'）
            parens = []
            for blk in raw['blocks']:
                if blk['type'] != 0:
                    continue
                for ln in blk['lines']:
                    for sp in ln['spans']:
                        for ch in sp['chars']:
                            if ch['c'] in '()' and abs((ch['bbox'][1] + ch['bbox'][3]) / 2 - yc) < 8:
                                parens.append(pymupdf.Rect(ch['bbox']))
            left = [q for q in parens if q.x1 <= r.x0 + 2]
            right = [q for q in parens if q.x0 >= r.x1 - 2]
            if left and right:
                lp = max(left, key=lambda q: q.x1); rp = min(right, key=lambda q: q.x0)
                band_top = min(lp.y0, rp.y0); band_bot = max(lp.y1, rp.y1)
                band_c = (band_top + band_bot) / 2
                print(f'  p{pno} × y[{r.y0:.2f},{r.y1:.2f}] 中心{yc:.2f}；括号带 y[{band_top:.2f},{band_bot:.2f}] 中心{band_c:.2f}'
                      f' → 偏差 {(yc - band_c) / PTMM:+.3f}mm')
            break
