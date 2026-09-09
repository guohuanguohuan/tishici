# -*- coding: utf-8 -*-
r"""复审计·片D 独立重测：变/式 笔画宽（360dpi 页图尺）
方法（双法互证，均自写）：
  A. run-mode：逐行水平暗游程长度直方图取众数（二值 gray<128）
  B. EDT：骨架点距离变换中位 ×2（skimage.skeletonize + scipy EDT）
对象：
  ① 我方 variantF/main.pdf 全部 9 处「变式」标签（rawdict 取字符 bbox 定位）
  ② 全品 5557 导学案 p06（书页 141）两处「变式」标签（矢量页，360dpi 渲染后按列投影切字）
输出：m_片D_笔画_result.json + 标注裁片
"""
import json
import os

import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_OURS = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
PDF_QP = r'C:\提示词\工作区\电子样书寻源-0909\【5557】2025-2026（上）全品学练考 高中数学 选择性必修第一册 RJB（导学案）.pdf'
DPI = 360
SC = DPI / 72.0  # pt -> px


def render(page, dpi=DPI):
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)


def stroke_mode(mask):
    """二值掩码：逐行水平暗游程众数 / 均值 / 中位（px）"""
    runs = []
    for row in mask:
        d = np.diff(np.concatenate(([0], row.view(np.int8), [0])))
        starts = np.flatnonzero(d == 1)
        ends = np.flatnonzero(d == -1)
        runs.extend((ends - starts).tolist())
    if not runs:
        return None
    runs = np.array(runs)
    vals, cnts = np.unique(runs, return_counts=True)
    mode = int(vals[np.argmax(cnts)])
    return dict(mode=mode, median=float(np.median(runs)), mean=float(runs.mean()), n=len(runs))


def stroke_edt(mask):
    """EDT 法：2×骨架点距离中位（px）"""
    if not mask.any():
        return None
    edt = ndimage.distance_transform_edt(mask)
    sk = skeletonize(mask)
    vals = edt[sk]
    if vals.size == 0:
        return None
    return dict(edt_2x_median=float(2 * np.median(vals)), edt_2x_mean=float(2 * vals.mean()), n=int(vals.size))


def measure(mask):
    ink = mask.astype(bool)
    ys, xs = np.where(ink)
    bbox = dict(x0=int(xs.min()), y0=int(ys.min()), x1=int(xs.max()) + 1, y1=int(ys.max()) + 1)
    return dict(
        bbox=bbox,
        w_px=bbox['x1'] - bbox['x0'], h_px=bbox['y1'] - bbox['y0'],
        w_mm=(bbox['x1'] - bbox['x0']) / (DPI / 25.4), h_mm=(bbox['y1'] - bbox['y0']) / (DPI / 25.4),
        mode=stroke_mode(ink), edt=stroke_edt(ink),
    )


def annotate(img, bbox, path, pad=4):
    x0, y0, x1, y1 = bbox['x0'], bbox['y0'], bbox['x1'], bbox['y1']
    h, w = img.shape
    ya, yb = max(0, y0 - pad), min(h, y1 + pad)
    xa, xb = max(0, x0 - pad), min(w, x1 + pad)
    crop = img[ya:yb, xa:xb].copy()
    rgb = np.stack([crop] * 3, axis=-1)
    # 红框（相对裁剪后坐标）
    ry0, ry1 = y0 - ya, y1 - ya - 1
    rx0, rx1 = x0 - xa, x1 - xa - 1
    rgb[ry0:ry1 + 1, rx0] = [255, 0, 0]
    rgb[ry0:ry1 + 1, rx1] = [255, 0, 0]
    rgb[ry0, rx0:rx1 + 1] = [255, 0, 0]
    rgb[ry1, rx0:rx1 + 1] = [255, 0, 0]
    big = np.kron(rgb, np.ones((4, 4, 1), dtype=np.uint8))
    Image.fromarray(big).save(path)


# ================= ① 我方 9 处「变式」 =================
ours = pymupdf.open(PDF_OURS)
results_ours = []
for pno, page in enumerate(ours, 1):
    img = render(page)
    td = page.get_text('rawdict')
    for b in td['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            for s in l['spans']:
                txt = ''.join(c['c'] for c in s['chars'])
                if '变' not in txt:
                    continue
                chars = s['chars']
                for ci, c in enumerate(chars):
                    if c['c'] not in ('变', '式'):
                        continue
                    bb = c['bbox']
                    x0 = int(np.floor(bb[0] * SC)) - 2
                    x1 = int(np.ceil(bb[2] * SC)) + 2
                    y0 = int(np.floor(bb[1] * SC)) - 2
                    y1 = int(np.ceil(bb[3] * SC)) + 2
                    reg = img[max(0, y0):y1, max(0, x0):x1]
                    mask = reg < 128
                    if not mask.any():
                        continue
                    m = measure(mask)
                    m.update(page=pno, char=c['c'], origin=[round(v, 2) for v in c['origin']])
                    results_ours.append(m)
                    tag = f"ours_p{pno}_{c['c']}_{len(results_ours)}"
                    annotate(reg, m['bbox'], os.path.join(BASE, f'_D_{tag}.png'))

print('=== 我方 变式 标签 ===')
for m in results_ours:
    print(f"p{m['page']} {m['char']} mode={m['mode']['mode']}px median={m['mode']['median']}px "
          f"EDT2x={m['edt']['edt_2x_median']:.2f}px 墨高={m['h_mm']:.2f}mm 墨宽={m['w_mm']:.2f}mm")

# ================= ② 全品 p06 两处「变式」 =================
qp = pymupdf.open(PDF_QP)
page = qp[5]
img = render(page)
# 由人工目检定位的两处标签区域（360dpi px）：上左 y 250-370 / 下左 y 3450-3580，x 230-430
regions = {'qp_p06_上左': (240, 250, 440, 380), 'qp_p06_下左': (240, 3450, 440, 3580)}
results_qp = []
for name, (x0, y0, x1, y1) in regions.items():
    reg = img[y0:y1, x0:x1]
    mask = reg < 128
    # 列投影切字
    colsum = mask.sum(axis=0)
    cols = colsum > 0
    segs = []
    in_seg = False
    for i, v in enumerate(cols):
        if v and not in_seg:
            st = i; in_seg = True
        elif not v and in_seg:
            segs.append((st, i)); in_seg = False
    if in_seg:
        segs.append((st, len(cols)))
    # 合并相邻过近片段（笔画间隙 < 4px 属同字）
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < 5:
            merged[-1] = (merged[-1][0], s[1])
        else:
            merged.append(list(s))
    print(f'{name}: 列投影切出 {len(merged)} 段 -> {merged}')
    for si, (cx0, cx1) in enumerate(merged[:2]):
        sub = mask[:, cx0:cx1]
        m = measure(sub)
        m.update(region=name, seg=si, x_abs=int(x0 + cx0), y_abs=int(y0))
        results_qp.append(m)
        annotate((sub * 255).astype(np.uint8), m['bbox'], os.path.join(BASE, f'_D_{name}_seg{si}.png'))

print('=== 全品 p06 变式 标签 ===')
for m in results_qp:
    print(f"{m['region']} seg{m['seg']} mode={m['mode']['mode']}px median={m['mode']['median']}px "
          f"EDT2x={m['edt']['edt_2x_median']:.2f}px 墨高={m['h_mm']:.2f}mm 墨宽={m['w_mm']:.2f}mm")

out = dict(ours=results_ours, qp=results_qp)
with open(os.path.join(BASE, 'm_片D_笔画_result.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('saved m_片D_笔画_result.json')
