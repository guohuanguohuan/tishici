# -*- coding: utf-8 -*-
"""取证B：墨级实测（600dpi）。
B1 = 5组并排：图墨盒/文墨右缘/图墨左缘→墨缝、图墨顶 vs 题干首行墨顶→顶差。
B2 = 判断题 √/× 字符墨尺寸+笔画横走线宽（600dpi, t128）。
输出 B_result.json + 证据裁片。只读项目文件。"""
import os, json
import pymupdf as fitz
from PIL import Image, ImageDraw

BASE = r'C:\提示词\工作区\字替对照-0909\variantF'
OUT = r'C:\提示词\工作区\_tmp取证0909c\D组'
DPI = 600
PXMM = DPI / 25.4
doc = fitz.open(os.path.join(BASE, 'main.pdf'))

def render(page, rect, path, dpi=DPI):
    pix = page.get_pixmap(dpi=dpi, clip=rect)
    pix.save(path)
    return path

def ink_bbox(img, thr=128):
    g = img.convert('L').point(lambda v: 255 if v < thr else 0)
    bb = g.getbbox()  # dark bbox
    return bb  # (l,t,r,b) or None

# ---------- B1 ----------
A = json.load(open(os.path.join(OUT, 'A_result.json'), encoding='utf-8'))
sides = [g for g in A['groups'] if g['name'].startswith('image')]
res1 = []
for i, g in enumerate(sides, 1):
    page = doc[g['page'] - 1]
    r = fitz.Rect(g['bbox'])
    col_left = r.x0 - 140  # 左minipage宽≤46.4mm=131.5pt，取140pt 窗
    d = page.get_text('dict', clip=fitz.Rect(col_left, r.y0 - 30, page.rect.width, r.y1 + 10))
    stem = []
    for blk in d['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk['lines']:
            lr = fitz.Rect(ln['bbox'])
            if lr.x0 >= col_left - 2 and lr.x1 <= r.x0 + 4 and lr.y0 < r.y1 - 4 and lr.y1 > r.y0 - 4:
                txt = ''.join(s['text'] for s in ln['spans'])
                stem.append(dict(y0=lr.y0, y1=lr.y1, x0=lr.x0, x1=lr.x1, text=txt[:44],
                                 spans=[dict(bbox=[round(v,2) for v in s['bbox']], size=s['size'], font=s['font']) for s in ln['spans']]))
    stem.sort(key=lambda L: L['y0'])
    # 渲染整组区域（含左右）
    pad = 6  # pt
    clip = fitz.Rect(min([L['x0'] for L in stem], default=r.x0 - 135) - pad, min([L['y0'] for L in stem], default=r.y0) - pad,
                     r.x1 + pad, max(r.y1, max([L['y1'] for L in stem], default=r.y1)) + pad)
    png = os.path.join(OUT, f'B_g{i}_{g["name"].replace(".png","")}_ctx.png')
    render(page, clip, png)
    im = Image.open(png).convert('L')
    sc = im.width / clip.width  # px per pt
    def pt2px(pt_x, pt_y):
        return ((pt_x - clip.x0) * sc, (pt_y - clip.y0) * sc)

    # 图墨盒：在图盒内侧小窗内找墨
    ix0, iy0 = pt2px(r.x0 + 0.5, r.y0 + 0.5); ix1, iy1 = pt2px(r.x1 - 0.5, r.y1 - 0.5)
    sub = im.crop((int(ix0), int(iy0), int(ix1), int(iy1)))
    ibb = ink_bbox(sub)
    img_ink = None
    if ibb:
        gx0 = clip.x0 + (ix0 + ibb[0]) / sc; gy0 = clip.y0 + (iy0 + ibb[1]) / sc
        gx1 = clip.x0 + (ix0 + ibb[2]) / sc; gy1 = clip.y0 + (iy0 + ibb[3]) / sc
        img_ink = [round(gx0, 2), round(gy0, 2), round(gx1, 2), round(gy1, 2)]

    # 题干首行墨顶
    first = stem[0]
    fx0, fy0 = pt2px(first['x0'], first['y0'] - 2); fx1, fy1 = pt2px(first['x1'], first['y1'])
    fsub = im.crop((int(fx0), int(fy0), int(fx1), int(fy1)))
    fbb = ink_bbox(fsub)
    stem_ink_top = clip.y0 + (fy0 + fbb[1]) / sc if fbb else None

    # 文墨右缘：对图墨竖向范围内每行像素，找 x∈[stem.x0, img.x0) 的最右墨；取全带最右 + 首行带最右
    text_ink_right_band = None
    if img_ink:
        ys = range(int(pt2px(clip.x0, img_ink[1])[1]), int(pt2px(clip.x0, img_ink[3])[1]))
        x_stop = int(pt2px(clip.x0, 0)[0] + (r.x0 - clip.x0) * sc) - 1  # 图盒左缘
        best = None
        for yy in ys:
            row = [x for x in range(int((first['x0'] - clip.x0) * sc), x_stop) if im.getpixel((x, yy)) < 128]
            if row:
                xr = clip.x0 + max(row) / sc
                if best is None or xr > best[0]:
                    best = (xr, clip.y0 + yy / sc)
        text_ink_right_band = best
    seam_ink = None
    if img_ink and text_ink_right_band:
        seam_ink = img_ink[0] - text_ink_right_band[0]
    topdiff_ink = (img_ink[1] - stem_ink_top) if (img_ink and stem_ink_top) else None
    e = dict(idx=i, name=g['name'], page=g['page'],
             imgbox_mm=[round(v / (72/25.4), 2) for v in r],
             img_ink_pt=img_ink,
             img_ink_mm=[round(v / (72/25.4), 2) for v in img_ink] if img_ink else None,
             stem_first=first['text'],
             stem_first_y0=round(first['y0'], 2),
             stem_lines_n=len(stem),
             stem_lines=[dict(y0=round(L['y0'],2), x1=round(L['x1'],2), seam_box_mm=round((r.x0 - L['x1'])/(72/25.4),2), text=L['text']) for L in stem],
             seam_box_min_mm=round(min((r.x0 - L['x1'])/(72/25.4) for L in stem), 2),
             seam_ink_pt=round(seam_ink, 2) if seam_ink is not None else None,
             seam_ink_mm=round(seam_ink / (72/25.4), 2) if seam_ink is not None else None,
             topdiff_box_mm=round((r.y0 - first['y0']) / (72/25.4), 2),
             topdiff_ink_pt=round(topdiff_ink, 2) if topdiff_ink is not None else None,
             topdiff_ink_mm=round(topdiff_ink / (72/25.4), 2) if topdiff_ink is not None else None,
             ctx_png=png)
    res1.append(e)

# ---------- B2 ----------
res2 = []
for j, z in enumerate(A['zhen']):
    page = doc[z['page'] - 1]
    b = fitz.Rect(z['bbox'])
    clip = fitz.Rect(b.x0 - 4, b.y0 - 4, b.x1 + 4, b.y1 + 4)
    png = os.path.join(OUT, f'B_z{j}_{z["c"]}_p{z["page"]}.png')
    render(page, clip, png)
    im = Image.open(png).convert('L')
    sc = im.width / clip.width
    bb = ink_bbox(im)
    if not bb:
        res2.append(dict(z, ink=None)); continue
    iw = (bb[2] - bb[0]) / sc / (72/25.4); ih = (bb[3] - bb[1]) / sc / (72/25.4)
    # 笔画横走线宽：行 25/40/60/75% 处的墨 run 宽（px@600dpi）
    runs = []
    h = bb[3] - bb[1]
    for fr in (0.25, 0.40, 0.60, 0.75):
        yy = bb[1] + int(h * fr)
        xs = [x for x in range(bb[0], bb[2]) if im.getpixel((x, yy)) < 128]
        if not xs:
            continue
        # 连续 run 分段
        segs, s0, px_ = [], xs[0], xs[0]
        for x in xs[1:]:
            if x == px_ + 1:
                px_ = x
            else:
                segs.append(px_ - s0 + 1); s0 = px_ = x
        segs.append(px_ - s0 + 1)
        runs.append(round(fr, 2))
        runs.append(segs)
    res2.append(dict(j=j, c=z['c'], page=z['page'], font=z['font'], size=z['size'],
                     ink_w_mm=round(iw, 2), ink_h_mm=round(ih, 2),
                     runs_600dpi=runs, png=png))

json.dump(dict(side=res1, zhen=res2), open(os.path.join(OUT, 'B_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('== B1 并排组墨级 ==')
for e in res1:
    print(f"g{e['idx']} {e['name']} p{e['page']} 墨缝盒口径min={e['seam_box_min_mm']}mm 墨缝墨口径={e['seam_ink_mm']}mm "
          f"顶差盒={e['topdiff_box_mm']}mm 顶差墨={e['topdiff_ink_mm']}mm 首行「{e['stem_first'][:22]}」 行数={e['stem_lines_n']}")
print('== B2 判断题字符墨级 ==')
for e in res2:
    print(f"z{e['j']} {e['c']} p{e['page']} {e['font']} {e['size']}pt 墨 {e['ink_w_mm']}x{e['ink_h_mm']}mm runs={e['runs_600dpi']}")
