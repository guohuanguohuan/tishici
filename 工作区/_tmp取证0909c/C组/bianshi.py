# -*- coding: utf-8 -*-
"""意见33 取证：「变式N」标签笔画竖粗＋灰度实测（我方 main.pdf vs 全品 p06）。只读，产物写本目录。"""
import os
import numpy as np
from PIL import Image
import fitz

OUT = os.path.dirname(os.path.abspath(__file__))
PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
P6 = r'C:\提示词\工作区\全品结构提取\数学选必一\导学案页图\p06.png'
PX5 = 360 / 25.4          # zoom5.0 口径 = 14.1732 px/mm（对照说明 9.2 笔画单位）
EM_MM = 12.03 * 25.4 / 72  # 12.03pt = 4.2427mm


def char_boxes(label, thr=128):
    """按列空隙切字符，返回每字 bbox (x0,y0,x1,y1)（label 为二值图）"""
    colink = label.any(axis=0)
    xs = np.where(colink)[0]
    if len(xs) == 0:
        return []
    boxes, s, p = [], xs[0], xs[0]
    for v in xs[1:]:
        if v - p > 3:
            boxes.append((s, p))
            s = v
        p = v
    boxes.append((s, p))
    out = []
    for x0, x1 in boxes:
        sub = label[:, x0:x1 + 1]
        ys = np.where(sub.any(axis=1))[0]
        out.append((x0, ys.min(), x1, ys.max()))
    return out


def stroke_stats(gray, bbox, pxmm, tag):
    """对单字 bbox：竖笔宽（二值众数＋AA积分中位）、墨深、墨密度"""
    x0, y0, x1, y1 = bbox
    h = y1 - y0 + 1
    w = x1 - x0 + 1
    dark = gray < 128
    runs = []
    for y in range(y0 + int(0.25 * h), y1 - int(0.2 * h)):
        row = dark[y, x0:x1 + 1]
        d = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
        ss = np.where(d == 1)[0]
        ee = np.where(d == -1)[0]
        for s, e in zip(ss, ee):
            ln = e - s
            if 2 <= ln <= 0.45 * w:
                runs.append((y, x0 + s, x0 + e, ln))
    rep = {}
    if runs:
        lens = np.array([r[3] for r in runs])
        mode = int(np.median(lens))
        sel = [r for r in runs if abs(r[3] - mode) <= 1]
        ints = []
        for (y, xs, xe, ln) in sel:
            prof = 1.0 - gray[y, max(0, xs - 3):xe + 3].astype(np.float64) / 255.0
            ints.append(prof.sum())
        rep['mode_bin_px'] = mode
        rep['int_px_med'] = float(np.median(ints))
        rep['int_mm'] = rep['int_px_med'] / pxmm
        rep['em_ratio'] = rep['int_mm'] / EM_MM
        rep['nrun'] = len(runs)
    core = gray[y0:y1 + 1, x0:x1 + 1]
    dk = core[core < 128]
    rep['min_gray'] = int(core.min())
    rep['p10_gray'] = int(np.percentile(dk, 10)) if dk.size else -1
    rep['ink_density'] = float(dark[y0:y1 + 1, x0:x1 + 1].mean())
    rep['ink_h_mm'] = h / pxmm
    rep['ink_w_mm'] = w / pxmm
    print(f"  {tag}: 字面{w}x{h}px 竖粗二值众数={rep.get('mode_bin_px')}px "
          f"AA积分={rep.get('int_px_med', 0):.2f}px={rep.get('int_mm', 0):.3f}mm"
          f"={rep.get('em_ratio', 0):.4f}em | 墨深min={rep['min_gray']} p10={rep['p10_gray']} "
          f"密度={rep['ink_density']:.3f} 字高={rep['ink_h_mm']:.2f}mm")
    return rep


def crop_label(img_gray, x0, y0, x1, y1, name, thr=128):
    sub = img_gray[y0:y1, x0:x1]
    dark = sub < thr
    ys, xs = np.where(dark)
    bb = (xs.min(), ys.min(), xs.max(), ys.max())
    Image.fromarray(sub).save(os.path.join(OUT, name))
    return sub, bb


def main():
    print('==== 我方 main.pdf「变式N」====')
    doc = fitz.open(PDF)
    hits = []
    for pno in range(len(doc)):
        for r in doc[pno].search_for('变式'):
            hits.append((pno + 1, r))
    print('命中：', [(p, round(r.x0), round(r.y0)) for p, r in hits])
    # 取第一个「变式1」（p2 探究点一）
    pg, rect = hits[0]
    page = doc[pg - 1]
    # 字体自证
    d = page.get_text('dict')
    for bl in d['blocks']:
        for ln in bl.get('lines', []):
            for sp in ln['spans']:
                if '变式' in sp['text']:
                    print(f"  span p{pg}: font={sp['font']} size={sp['size']:.2f} "
                          f"color=#{sp['color']:06x} text={sp['text']!r}")
    pad = 6
    clip = fitz.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad)
    zoom = 12
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, colorspace=fitz.csGRAY)
    g12 = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).copy()
    PX12 = 72 * zoom / 25.4
    # 同图降回 zoom5 口径
    im5 = Image.fromarray(g12).resize((int(g12.shape[1] * PX5 / PX12), int(g12.shape[0] * PX5 / PX12)),
                                      Image.LANCZOS)
    g5 = np.asarray(im5)
    Image.fromarray(g12).save(os.path.join(OUT, '_us_bianshi_z12.png'))
    lab = g12 < 128
    cbs = char_boxes(lab)
    print(f'  渲染 {PX12:.1f}px/mm（zoom{zoom}），字符数={len(cbs)}')
    us = []
    for i, cb in enumerate(cbs):
        us.append(stroke_stats(g12, cb, PX12, f'我方字{i}（zoom12）'))
    # zoom5 口径（与标定同口径）
    lab5 = g5 < 128
    cbs5 = char_boxes(lab5)
    us5 = []
    for i, cb in enumerate(cbs5):
        us5.append(stroke_stats(g5, cb, PX5, f'我方字{i}（zoom5口径）'))

    print('==== 全品 p06「变式」标签 ====')
    qp = np.asarray(Image.open(P6).convert('L'))
    # 目测两处标签：左栏 (238..340, 265..330)、右栏 (1540..1660, 265..330)，放宽取大窗
    for name, (wx0, wy0, wx1, wy1) in [('左', (200, 230, 480, 360)), ('右', (1480, 230, 1760, 360))]:
        sub, bb = crop_label(qp, wx0, wy0, wx1, wy1, f'_qp_bianshi_{name}.png')
        x0, y0, x1, y1 = bb
        print(f'  [{name}] 标签bbox=({wx0+x0},{wy0+y0})-({wx0+x1},{wy0+y1})')
        labc = sub < 128
        cbs = char_boxes(labc)
        for i, cb in enumerate(cbs):
            cb_abs = (cb[0], cb[1], cb[2], cb[3])
            stroke_stats(sub, cb_abs, PX5, f'全品[{name}]字{i}（360dpi=zoom5口径）')
        # 放大证据图（4x nearest）
        big = Image.fromarray(sub).resize((sub.shape[1] * 4, sub.shape[0] * 4), Image.NEAREST)
        big.save(os.path.join(OUT, f'_qp_bianshi_{name}_x4.png'))

    print('==== 字重标定档案复核（variantE F400-12.03=4px 的口径） ====')
    print(f'  4px @14.1732px/mm = {4/PX5:.3f}mm = {4/PX5/EM_MM:.4f}em')
    print(f'  我方 zoom12 AA积分中位（字0「变」）= {us[0].get("int_mm",0):.3f}mm = {us[0].get("em_ratio",0):.4f}em')
    print(f'  我方 zoom5  二值众数（字0「变」）= {us5[0].get("mode_bin_px")}px')


if __name__ == '__main__':
    main()
