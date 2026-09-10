# -*- coding: utf-8 -*-
r"""片G 0910b 取证：六图「终版裁片 vs 源位图同尺」并排对照 ＋ 上下文裁片。

口径：
- 整页图＝variantF/png/page{1..7}.png（render.py 口径 150dpi 重渲版），裁片一律从这些 png 上取，
  与整页同 dpi；定位矩形在 PDF pt 坐标算好后 ×(150/72) 换算成像素。
- 图区定位复用 终版实测.py 的种子簇（非轴对齐矢量墨聚簇）＋带内 150dpi 连通域做「标签链」：
  裁片框 U＝种子簇矩形 ∪（与之相交的线框连通域）∪（标签样连通域：宽≤14mm、高 1.2–12mm、
  不完全落在任一「≥3字文字行」bbox（外扩0.5mm）内——图内标签行文本≤2字不受影响，
  选项短行「A．√3；」被排除；与线框/已收并集距离 ≤8mm 迭代链入）。
  诊断对照：B＝600dpi fig_bbox（线框∪4mm 标签链，实测会裁掉外缘标签）；
  R＝带内全墨（会混入同栏填空线/选项短行尾墨）。U 用于裁片，B/R 仅落日志。
- 源位图缩放：按当前 \resizebox 置宽 mm 等比缩放到 150dpi 像素宽，与终版同尺。
  image1/image5 墨在 α 通道（RGB 恒黑），先 alpha 压白底再缩放。
产物（对照/ 下，每图 4 件）：终版-gX.*.png / 源-gX.*.png / 对照-gX.*.png / 上下文-gX.*.png
"""
import importlib.util
import os

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
VF = 'C:/提示词/工作区/字替对照-0909/variantF'
MAIN = VF + '/main.pdf'
PNG = VF + '/png'
MEDIA = VF + '/media/media'
OUT = os.path.join(HERE, '对照')
os.makedirs(OUT, exist_ok=True)

_spec = importlib.util.spec_from_file_location('pg_measure', os.path.join(HERE, '终版实测.py'))
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

PT = mod.PT                    # pt per mm
PXS = 150.0 / 72.0             # px per pt（整页 png 150dpi）
MARGIN, COLSEP, COLW, MID, BOT = mod.MARGIN, mod.COLSEP, mod.COLW, mod.MID, mod.BOT
PAD = 1.5 * PT                 # 终版裁片外扩 1.5mm
GROW = 8.0 * PT                # 标签链半径（对齐 片G实测 8mm 口径）
LBL_W, LBL_H, LBL_HMIN = 14 * PT, 12 * PT, 1.2 * PT

FIGS = [
    ('g6-triple',   2, 2, 'sub3_B_4.png', 84.0),
    ('g1-prism',    3, 2, 'image1.png',   41.1),
    ('g2-cubeE',    4, 1, 'image2.png',   42.0),
    ('g3-cube6',    5, 1, 'image3.png',   84.0),
    ('g4-dihedral', 6, 1, 'image4.png',   66.3),
    ('g5-fold',     6, 2, 'image5.png',   54.7),
]

doc = pymupdf.open(MAIN)
log = []


def L(s):
    log.append(s)
    print(s)


def locate():
    out = []
    for pno, page in enumerate(doc, 1):
        H = page.rect.height
        for r, nlong in mod.merge_rows(mod.cluster(mod.diag_items(page.get_drawings()), 8 / 25.4 * PT)):
            if r.width / PT < 15 or r.height / PT < 10 or nlong < mod.MINLONG:
                continue
            col = 1 if r.x0 < MID else 2
            cl = MARGIN if col == 1 else MARGIN + COLW + COLSEP
            ls = mod.col_lines(page, cl)
            up = max([lr.y1 for t, lr in ls if lr.y1 <= r.y0 + 1], default=MARGIN - 1)
            dn = min([lr.y0 for t, lr in ls if lr.y0 >= r.y1 - 1], default=H - BOT + 1)
            out.append(dict(pno=pno, col=col, seed=r, up=up, dn=dn, cl=cl))
    return out


SEEDS = locate()
L('main.pdf open ok, pages=%d; seeds found: %d' % (doc.page_count, len(SEEDS)))

page_imgs = {}


def page_img(pno):
    if pno not in page_imgs:
        page_imgs[pno] = Image.open(os.path.join(PNG, 'page%d.png' % pno)).convert('RGB')
    return page_imgs[pno]


def flat_white(im):
    if im.mode == 'RGBA':
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        return Image.alpha_composite(bg, im).convert('RGB')
    return im.convert('RGB')


def band_components(img, band):
    """带内 150dpi 二值墨 → 8 邻连通域（膨胀2桥缝，bbox 取真墨）。返回 pt 矩形列表。"""
    g = np.asarray(img.convert('L'))
    bx = (int(band.x0 * PXS), int(band.y0 * PXS), int(np.ceil(band.x1 * PXS)), int(np.ceil(band.y1 * PXS)))
    mask = g[bx[1]:bx[3], bx[0]:bx[2]] < 200
    lab, cnt = ndimage.label(ndimage.binary_dilation(mask, np.ones((3, 3), bool), iterations=2),
                             structure=np.ones((3, 3), bool))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        sub = mask[sl] & (lab[sl] == i)
        ys, xs = np.nonzero(sub)
        if not len(xs):
            continue
        out.append(pymupdf.Rect(band.x0 + (sl[1].start + xs.min()) / PXS,
                                band.y0 + (sl[0].start + ys.min()) / PXS,
                                band.x0 + (sl[1].start + xs.max() + 1) / PXS,
                                band.y0 + (sl[0].start + ys.max() + 1) / PXS))
    return out, mask, bx


font = ImageFont.load_default()
for tag, pexp, cexp, srcname, wbox in FIGS:
    cand = [s for s in SEEDS if s['pno'] == pexp and s['col'] == cexp]
    assert len(cand) == 1, (tag, len(cand))
    s = cand[0]
    page = doc[pexp - 1]
    H = page.rect.height
    cl, colw = s['cl'], COLW
    band = pymupdf.Rect(cl + 0.2, s['up'] + 0.3, cl + colw - 0.2, s['dn'] - 0.3)  # pt
    seed = pymupdf.Rect(s['seed'].x0 - 1, s['seed'].y0 - 1, s['seed'].x1 + 1, s['seed'].y1 + 1)
    B = mod.fig_bbox(page, band, seed)                       # 600dpi 参考（会裁标签）
    img = page_img(pexp)
    comps, mask, bx = band_components(img, band)
    ys, xs = np.nonzero(mask)
    R = pymupdf.Rect(band.x0 + xs.min() / PXS, band.y0 + ys.min() / PXS,
                     band.x0 + (xs.max() + 1) / PXS, band.y0 + (ys.max() + 1) / PXS)
    # 长文字行（文本≥3字，宽窄均算）bbox 外扩 0.5mm，完全落入者＝行墨，剔出标签链；
    # 图内标签行文本≤2字（A₁、①…），不受影响。
    lines3 = [lr for t, lr in mod.col_lines(page, cl, wide_only=False) if len(t.strip()) >= 3]
    linx = [pymupdf.Rect(lr.x0 - .5 * PT, lr.y0 - .5 * PT, lr.x1 + .5 * PT, lr.y1 + .5 * PT) for lr in lines3]

    def lbl_like(r):
        return (r.width <= LBL_W and LBL_HMIN <= r.height <= LBL_H
                and not any(lc.contains(r) for lc in linx))

    def grow(rc, g):
        return pymupdf.Rect(rc.x0 - g, rc.y0 - g, rc.x1 + g, rc.y1 + g)

    # base：与种子矩形（线框簇）直接相交者全收（线框本体可能很大）；
    #       外加 8mm 内的标签样件；再迭代链入 8mm 内标签样件。
    keep = [c for c in comps if c.intersects(seed)]
    keep += [c for c in comps if c not in keep and lbl_like(c) and c.intersects(grow(seed, GROW))]
    U = pymupdf.Rect(seed)
    for r in keep:
        U |= r
    for _ in range(6):
        g6 = grow(U, GROW)
        add = [c for c in comps if lbl_like(c) and g6.contains(c) and not any(c.intersects(k) for k in keep)]
        if not add:
            break
        keep += add
        for r in add:
            U |= r
    L('%s p%d c%d | 600B %.2f×%.2f | 带墨R %.2f×%.2f | 裁片U %.2f×%.2f @(%.2f,%.2f)mm | 标签件 %d'
      % (tag, pexp, cexp, B.width / PT, B.height / PT, R.width / PT, R.height / PT,
         U.width / PT, U.height / PT, U.x0 / PT, U.y0 / PT, len(keep)))
    # ---- 终版裁片 ----
    x0 = max(U.x0 - PAD, cl - 1.5 * PT)
    x1 = min(U.x1 + PAD, cl + colw + 1.5 * PT)
    y0 = max(U.y0 - PAD, 2 * PT)
    y1 = min(U.y1 + PAD, H - 2 * PT)
    box = (int(np.floor(x0 * PXS)), int(np.floor(y0 * PXS)), int(np.ceil(x1 * PXS)), int(np.ceil(y1 * PXS)))
    fin = img.crop(box)
    fg = np.asarray(fin.convert('L')) < 200
    fy, fx = np.nonzero(fg)
    L('   crop %dx%dpx ink-margin L/T/R/B=%d/%d/%d/%d (pad≈%.0fpx)'
      % (fin.width, fin.height, fx.min(), fy.min(), fin.width - 1 - fx.max(), fin.height - 1 - fy.max(), PAD * PXS))
    fp = os.path.join(OUT, '终版-%s-p%dc%d.png' % (tag, pexp, cexp))
    fin.save(fp)
    # ---- 源位图缩放到置宽（150dpi 同尺）----
    srcim = flat_white(Image.open(os.path.join(MEDIA, srcname)))
    tgt_w = int(round(wbox * 150.0 / 25.4))
    tgt_h = int(round(srcim.height * tgt_w / srcim.width))
    srcs = srcim.resize((tgt_w, tgt_h), Image.LANCZOS)
    sp = os.path.join(OUT, '源-%s-%s.png' % (tag, os.path.splitext(srcname)[0]))
    srcs.save(sp)
    # ---- 并排对照 ----
    gap, m, th = 8, 12, 20
    W = m + fin.width + gap + srcs.width + m
    Hh = m + th + max(fin.height, srcs.height) + m
    mon = Image.new('RGB', (W, Hh), 'white')
    dr = ImageDraw.Draw(mon)
    title = '%s  final(p%dc%d crop) vs %s scaled to %.1fmm  @150dpi' % (tag, pexp, cexp, srcname, wbox)
    dr.text((m, m // 2), title, fill='black', font=font)
    top = m + th
    mon.paste(fin, (m, top + (Hh - top - m - fin.height) // 2))
    mon.paste(srcs, (m + fin.width + gap, top + (Hh - top - m - srcs.height) // 2))
    dp = os.path.join(OUT, '对照-%s-p%dc%d.png' % (tag, pexp, cexp))
    mon.save(dp)
    # ---- 上下文：整栏宽，图（U）上下各 +30mm ----
    cy0 = max(U.y0 - 30 * PT, 2 * PT)
    cy1 = min(U.y1 + 30 * PT, H - 2 * PT)
    cbox = (int((cl - PT) * PXS), int(cy0 * PXS), int((cl + colw + PT) * PXS), int(cy1 * PXS))
    ctx = img.crop(cbox)
    cp = os.path.join(OUT, '上下文-%s-p%dc%d.png' % (tag, pexp, cexp))
    ctx.save(cp)
    L('   saved: %s | %s %dx%d | %s | %s %dx%d'
      % (os.path.basename(fp), os.path.basename(sp), srcs.width, srcs.height,
         os.path.basename(dp), os.path.basename(cp), ctx.width, ctx.height))

with open(os.path.join(OUT, '_run-log.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(log) + '\n')
print('DONE ->', OUT)
