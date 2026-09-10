# -*- coding: utf-8 -*-
"""H3 任务1：我方 main.pdf 页码块现状实测（360dpi 像素＋rawdict）。
输出：块 bbox/宽高/四缘、数字 ink bbox/高/宽/灰度/竖笔 run/距块内缘、数字 span 字体字号色。"""
import numpy as np
import pymupdf
from PIL import Image
import io
from collections import Counter

PDF = r'C:/提示词/工作区/字替对照-0909/variantF/main.pdf'
PXMM = 14.1732  # 360dpi

doc = pymupdf.open(PDF)
print('pages', doc.page_count)
for pno in range(doc.page_count):
    page = doc[pno]
    Wpt, Hpt = page.rect.width, page.rect.height
    pix = page.get_pixmap(dpi=360)
    g = np.asarray(Image.open(io.BytesIO(pix.tobytes('png'))).convert('L')).astype(np.int16)
    H, W = g.shape
    sub = g[H * 4 // 5:, :]
    from scipy import ndimage
    lab, n = ndimage.label((np.abs(sub - 221) <= 14), structure=np.ones((3, 3)))
    for sl in ndimage.find_objects(lab):
        ys, xs = sl
        h = ys.stop - ys.start; w = xs.stop - xs.start
        if w < 200 or h < 60:
            continue
        y0, y1, x0, x1 = ys.start + H * 4 // 5, ys.stop + H * 4 // 5, xs.start, xs.stop
        seg = g[y0:y1, x0:x1]
        dark = seg < 128
        if not dark.any():
            continue
        dys, dxs = np.nonzero(dark)
        nx0, nx1, ny0, ny1 = dxs.min(), dxs.max() + 1, dys.min(), dys.max() + 1
        num = seg[ny0:ny1, nx0:nx1]
        vals = num[num < 200]
        runs = []
        for r in range(num.shape[0]):
            row = num[r] < 128
            c = 0
            for v in row:
                if v: c += 1
                elif c: runs.append(c); c = 0
            if c: runs.append(c)
        rc = Counter(runs).most_common(3)
        odd = pno % 2 == 0
        inner = '左' if odd else '右'
        print(f'p{pno+1} 块 x[{x0},{x1}) y[{y0},{y1}) {w/PXMM:.2f}×{h/PXMM:.2f}mm '
              f'左缘{x0/PXMM:.2f} 右缘距纸右{(W-x1)/PXMM:.2f} 底距纸底{(H-y1)/PXMM:.2f}mm；'
              f'数字 ink高{ny1-ny0}px={ (ny1-ny0)/PXMM:.2f}mm 宽{nx1-nx0}px 灰min{vals.min()} 中位{int(np.median(vals))} '
              f'距块{inner}{ (nx0 if odd else x1-(x0+nx1))/PXMM:.2f}mm runs{rc}')
    # rawdict: 页码 span
    for b in page.get_text('rawdict')['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            for sp in l['spans']:
                t = sp['text'].strip()
                if t == str(pno + 1) and sp['bbox'][1] > Hpt * 0.9:
                    print(f'    页码 span 字体={sp["font"]} size={sp["size"]:.2f} 色={sp["color"]:#08x} bbox={[round(v,2) for v in sp["bbox"]]}')
