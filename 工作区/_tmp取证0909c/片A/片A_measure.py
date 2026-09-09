# -*- coding: utf-8 -*-
"""片A 改后几何实测（600dpi 墨级）：5 组并排——图文最小缝／图墨顶差／图墨右缘距栏右。
口径：
  主口径 seam = 图墨左缘 − 图竖向范围内各行文墨右缘的最大值（= 最小缝）；
  逐行 seam_line = min over 文字行（图墨在该行 y 带内的最左墨 − 行墨右缘）；
  topdiff = 图墨顶 − 首行文墨顶（负＝图更高）；right_edge = 栏右 − 图墨右缘。
输出：片A_result.json + 5 组标注裁片 片A_g{i}_*_标注.png（2 倍放大）。
"""
import os, json, sys
import pymupdf as fitz
import numpy as np
from PIL import Image, ImageDraw

BASE = r'C:\提示词\工作区\字替对照-0909\variantF'
OUT = r'C:\提示词\工作区\_tmp取证0909c\片A'
DPI = 600
PT = 72 / 25.4
COLW = 82.8 * PT
MARGIN = 17.575 * PT
COLSEP = 9.25 * PT
COLL = (MARGIN, MARGIN + COLW + COLSEP)
IMG_PX = {
    (691, 1159): 'image1.png',
    (764, 764): 'image2.png',
    (521, 496): 'image3.png',
    (788, 424): 'image4.png',
    (1798, 1350): 'image5.png',
}
doc = fitz.open(os.path.join(BASE, 'main.pdf'))
res = []

for pno in range(doc.page_count):
    page = doc[pno]
    for info in page.get_image_info(xrefs=True):
        key = (info['width'], info['height'])
        if key not in IMG_PX:
            continue
        name = IMG_PX[key]
        box = fitz.Rect(info['bbox'])
        cl = COLL[0] if box.x0 < (COLL[0] + COLW + COLSEP / 2) else COLL[1]
        col_right = cl + COLW
        clip = fitz.Rect(cl - 2, box.y0 - 8, col_right + 2, box.y1 + 8)
        pix = page.get_pixmap(dpi=DPI, clip=clip)
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')
        a = np.array(im) < 128
        sc = im.width / clip.width
        # 图墨 bbox（图盒内侧找墨）
        ix0, iy0 = (box.x0 + 0.6 - clip.x0) * sc, (box.y0 + 0.6 - clip.y0) * sc
        ix1, iy1 = (box.x1 - 0.6 - clip.x0) * sc, (box.y1 - 0.6 - clip.y0) * sc
        sub = a[int(iy0):int(iy1), int(ix0):int(ix1)]
        ys, xs = np.nonzero(sub)
        ink = [clip.x0 + (int(ix0) + xs.min()) / sc, clip.y0 + (int(iy0) + ys.min()) / sc,
               clip.x0 + (int(ix0) + xs.max()) / sc, clip.y0 + (int(iy0) + ys.max()) / sc]
        # 文字行（图左、竖向与图盒重叠）
        d = page.get_text('dict', clip=fitz.Rect(cl - 2, box.y0 - 10, box.x0, box.y1 + 10))
        lines = []
        for blk in d['blocks']:
            if blk['type'] != 0:
                continue
            for ln in blk['lines']:
                lr = fitz.Rect(ln['bbox'])
                txt = ''.join(sp['text'] for sp in ln['spans'])
                if lr.x1 <= box.x0 + 3 and lr.y1 > box.y0 + 2 and lr.y0 < box.y1 - 2 and txt.strip():
                    lines.append((lr, txt))
        lines.sort(key=lambda L: L[0].y0)
        first = lines[0][0]
        # 首行墨顶
        fx0, fy0 = (first.x0 - clip.x0) * sc, (first.y0 - 2 - clip.y0) * sc
        fx1, fy1 = (first.x1 + 1 - clip.x0) * sc, (first.y1 + 1 - clip.y0) * sc
        fsub = a[int(fy0):int(fy1), int(fx0):int(fx1)]
        fys, fxs = np.nonzero(fsub)
        first_ink_top = clip.y0 + (int(fy0) + fys.min()) / sc
        # 主口径：图竖向范围内逐行文墨右缘最大
        y0p, y1p = int((ink[1] - clip.y0) * sc), int((ink[3] - clip.y0) * sc)
        x_stop = int((box.x0 - clip.x0) * sc) - 1
        x_start = int((cl - clip.x0) * sc)
        best = None
        for yy in range(max(0, y0p), min(a.shape[0], y1p)):
            nz = np.nonzero(a[yy, x_start:x_stop])[0]
            if len(nz):
                xr = clip.x0 + (x_start + nz.max()) / sc
                if best is None or xr > best:
                    best = xr
        seam = ink[0] - best
        # 逐行口径：每行 y 带内图最左墨 − 行墨右缘（逐行取 min）
        per_line = []
        xa, xb = int((box.x0 - clip.x0) * sc), int((box.x1 - clip.x0) * sc)
        for lr, txt in lines:
            ly0, ly1 = int((lr.y0 - clip.y0) * sc), int((lr.y1 - clip.y0) * sc)
            fmin = None
            for yy in range(max(0, ly0), min(a.shape[0], ly1)):
                nz = np.nonzero(a[yy, xa:xb])[0]
                if len(nz):
                    cand = clip.x0 + (xa + nz.min()) / sc
                    if fmin is None or cand < fmin:
                        fmin = cand
            if fmin is not None:
                per_line.append((fmin - lr.x1, txt[:24]))
        e = dict(name=name, page=pno + 1, col='L' if cl == COLL[0] else 'R',
                 imgbox_mm=[round(v / PT, 2) for v in box],
                 ink_mm=[round(v / PT, 2) for v in ink],
                 ink_w_mm=round((ink[2] - ink[0]) / PT, 2),
                 ink_h_mm=round((ink[3] - ink[1]) / PT, 2),
                 first_line=lines[0][1][:36],
                 first_ink_top_mm=round(first_ink_top / PT, 2),
                 img_ink_top_mm=round(ink[1] / PT, 2),
                 topdiff_mm=round((ink[1] - first_ink_top) / PT, 2),
                 seam_mm=round(seam / PT, 2),
                 seam_line_mm=round(min(p[0] for p in per_line) / PT, 2) if per_line else None,
                 right_edge_mm=round((col_right - ink[2]) / PT, 2),
                 per_line_mm=[round(p[0] / PT, 2) for p in per_line],
                 lines_n=len(lines))
        res.append(e)
        # 标注裁片
        im2 = im.convert('RGB').resize((im.width * 2, im.height * 2), Image.LANCZOS)
        dr = ImageDraw.Draw(im2)
        ib = [(ink[0] - clip.x0) * sc * 2, (ink[1] - clip.y0) * sc * 2,
              (ink[2] - clip.x0) * sc * 2, (ink[3] - clip.y0) * sc * 2]
        dr.rectangle(ib, outline=(255, 0, 0), width=3)
        ymid = (ink[1] + ink[3]) / 2
        dr.line([(best - clip.x0) * sc * 2, (ymid - clip.y0) * sc * 2,
                 (ink[0] - clip.x0) * sc * 2, (ymid - clip.y0) * sc * 2], fill=(0, 160, 0), width=3)
        dr.line([(ink[0] - clip.x0) * sc * 2, (ink[1] - clip.y0) * sc * 2,
                 (ink[2] - clip.x0) * sc * 2, (ink[1] - clip.y0) * sc * 2], fill=(0, 0, 255), width=3)
        dr.line([(first.x0 - clip.x0) * sc * 2, (first_ink_top - clip.y0) * sc * 2,
                 (first.x1 - clip.x0) * sc * 2, (first_ink_top - clip.y0) * sc * 2], fill=(255, 140, 0), width=3)
        tag = (f'{name.replace(".png","")} p{pno+1} 缝{e["seam_mm"]:.2f}mm 逐行{e["seam_line_mm"]:.2f} '
               f'顶差{e["topdiff_mm"]:+.2f}mm 右缘{e["right_edge_mm"]:.2f}mm')
        dr.text((10, 10), tag, fill=(0, 0, 0))
        im2.save(os.path.join(OUT, f'片A_g{len(res)}_{name.replace(".png","")}_标注.png'))
        print(tag)

json.dump(res, open(os.path.join(OUT, '片A_result.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('---')
for e in res:
    print(f"{e['name']} p{e['page']}{e['col']} 缝={e['seam_mm']:.2f} 逐行min={e['seam_line_mm']} "
          f"顶差={e['topdiff_mm']:+.2f} 右缘={e['right_edge_mm']:.2f} 墨={e['ink_w_mm']}x{e['ink_h_mm']} 行数={e['lines_n']}")
