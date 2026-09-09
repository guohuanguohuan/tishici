# -*- coding: utf-8 -*-
r"""复审计·片A 独立重测：五组图文并排几何（600dpi 墨级）
三项：①图文墨缝（文字墨右缘→图墨左缘）②图墨顶差（图墨顶−首行文墨顶）③图墨右缘距栏右缘
方法：PDF 图位（get_image_info）定分割与行带；600dpi 灰度渲染取暗像素（<128）墨带。
文字区 x∈[栏左, 图位左−0.05mm]、y∈[图位y0−0.6mm, 图位y1+0.6mm]；图墨区＝图位框内暗像素。
另：image1 剪透明垫核验（PIL 读 alpha/墨 bbox 与画布比）。
"""
import json
import os

import numpy as np
import pymupdf
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
DPI = 600
SC = DPI / 72.0
PT = 72 / 25.4
# 版心几何（qp-layout：margin 17.575mm、columnsep 9.25mm、版心 174.85mm→栏宽 82.8mm）
MARGIN = 17.575
COLW = 82.8
COLSEP = 9.25
COLL = {'L': MARGIN, 'R': MARGIN + COLW + COLSEP}
COLR = {'L': MARGIN + COLW, 'R': MARGIN + COLW + COLSEP + COLW}


def render(page, dpi=DPI):
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)


def ink_bbox(mask):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return xs.min(), ys.min(), xs.max(), ys.max()


doc = pymupdf.open(PDF)
results = []
for pno, page in enumerate(doc, 1):
    infos = page.get_image_info()
    if not infos:
        continue
    img = render(page)
    for im in infos:
        bx0, by0, bx1, by1 = [v / PT for v in im['bbox']]  # mm
        if (bx1 - bx0) > 50:      # 60mm 居中三联图（非并排组）跳过
            continue
        col = 'L' if bx0 < 100 else 'R'
        # ---- 图墨 bbox：图位框内 ----
        x0 = int(np.floor(bx0 * DPI / 25.4)) - 1
        x1 = int(np.ceil(bx1 * DPI / 25.4)) + 1
        y0 = int(np.floor(by0 * DPI / 25.4)) - 1
        y1 = int(np.ceil(by1 * DPI / 25.4)) + 1
        reg = img[max(0, y0):y1, max(0, x0):x1]
        mimg = reg < 128
        ib = ink_bbox(mimg)
        if ib is None:
            continue
        # ---- 文字墨 bbox：同栏、图位左侧、行带内 ----
        tx0 = int(COLL[col] * DPI / 25.4)
        tx1 = int((bx0 - 0.05) * DPI / 25.4)
        ty0 = int((by0 - 0.6) * DPI / 25.4)
        ty1 = int((by1 + 0.6) * DPI / 25.4)
        treg = img[max(0, ty0):ty1, tx0:tx1]
        mtxt = treg < 128
        tb = ink_bbox(mtxt)
        if tb is None:
            continue
        # 过滤：文字墨带只保留「行带顶落在 [图位y0−0.5mm, 图位y1) 内」者
        # （排除图上方前段落行与图下方续行——两者行带顶均在图位 y0 以上或 y1 以下）
        rowproj = mtxt.any(axis=1)
        bands = []
        in_b = False
        for i, v in enumerate(rowproj):
            if v and not in_b:
                st = i; in_b = True
            elif not v and in_b:
                bands.append((st, i - 1)); in_b = False
        if in_b:
            bands.append((st, len(rowproj) - 1))
        gy0 = (by0 - 0.6) * DPI / 25.4   # 行带相对区域顶的偏移（mm→px）
        y0px = by0 * DPI / 25.4
        y1px = by1 * DPI / 25.4
        keep = [b for b in bands if y0px - 0.5 * DPI / 25.4 <= (b[0] + gy0) < y1px]
        if keep:
            mtxt2 = np.zeros_like(mtxt)
            for st, en in keep:
                mtxt2[st:en + 1] = mtxt[st:en + 1]
            tb2 = ink_bbox(mtxt2)
        else:
            tb2 = tb
        # ---- 三项指标（px→mm） ----
        gap = (x0 + ib[0]) - (tx0 + tb2[2])
        topdiff = (y0 + ib[1]) - (max(0, ty0) + tb2[1])
        redge = COLR[col] - (x0 + ib[2]) / DPI * 25.4
        results.append(dict(
            page=pno, col=col, img_box=[round(v, 2) for v in (bx0, by0, bx1, by1)],
            img_ink=[round(v / DPI * 25.4, 3) for v in (x0 + ib[0], y0 + ib[1], x0 + ib[2], y0 + ib[3])],
            txt_ink=[round(v / DPI * 25.4, 3) for v in (tx0 + tb2[0], max(0, ty0) + tb2[1], tx0 + tb2[2], max(0, ty0) + tb2[3])],
            gap_mm=round(gap / DPI * 25.4, 2),
            topdiff_mm=round(topdiff / DPI * 25.4, 3),
            redge_mm=round(redge, 2),
        ))
        # 证据裁片：标注图墨 bbox（红）与文字墨 bbox（绿）
        ax0 = int(COLL[col] * DPI / 25.4)
        ax1 = int((bx1 + 1) * DPI / 25.4)
        ay0 = int((by0 - 1) * DPI / 25.4)
        ay1 = int((by1 + 1) * DPI / 25.4)
        crop = img[max(0, ay0):ay1, ax0:ax1].copy()
        rgb = np.stack([crop] * 3, axis=-1)
        for (bx, by, bx2, by2), color in [((x0 + ib[0], y0 + ib[1], x0 + ib[2], y0 + ib[3]), [255, 0, 0]),
                                          ((tx0 + tb2[0], max(0, ty0) + tb2[1], tx0 + tb2[2], max(0, ty0) + tb2[3]), [0, 160, 0])]:
            rx0, ry0 = bx - ax0, by - max(0, ay0)
            rx1, ry1 = bx2 - ax0, by2 - max(0, ay0)
            for yy in (ry0, ry1):
                if 0 <= yy < rgb.shape[0]:
                    rgb[yy, max(0, rx0):rx1 + 1] = color
            for xx in (rx0, rx1):
                if 0 <= xx < rgb.shape[1]:
                    rgb[max(0, ry0):ry1 + 1, xx] = color
        Image.fromarray(rgb).save(os.path.join(BASE, f'_A_p{pno}_{col}_标注.png'))

print('=== 片A 五组图文并排（600dpi 墨级）===')
print(f"{'页':>2} {'栏':>2} {'墨缝mm':>7} {'顶差mm':>7} {'右缘距栏mm':>9}")
for r in results:
    print(f"{r['page']:>2} {r['col']:>2} {r['gap_mm']:>7.2f} {r['topdiff_mm']:>7.3f} {r['redge_mm']:>9.2f}")

# ---- image1 剪垫核验 ----
img1 = Image.open(r'C:\提示词\工作区\字替对照-0909\variantF\media\media\image1.png').convert('RGBA')
a = np.array(img1)
alpha = a[..., 3]
ink = alpha > 8
ys, xs = np.where(ink)
print(f"\nimage1 画布 {img1.size}，alpha>8 墨 bbox=({xs.min()},{ys.min()},{xs.max()},{ys.max()}) "
      f"→ 四周垫：左{xs.min()} 上{ys.min()} 右{img1.size[0]-1-xs.max()} 下{img1.size[1]-1-ys.max()} px")
nonwhite = (a[..., :3] < 250).any(axis=2) & ink
ys2, xs2 = np.where(nonwhite)
print(f"image1 非白墨 bbox=({xs2.min()},{ys2.min()},{xs2.max()},{ys2.max()})")
try:
    bak = Image.open(r'C:\提示词\工作区\_tmp取证0909c\片A\image1_未剪垫备份.png')
    print(f"对照：未剪垫备份画布 {bak.size}")
except Exception as e:
    print('备份读取失败', e)

with open(os.path.join(BASE, 'm_片A_图文_result.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print('saved m_片A_图文_result.json')
