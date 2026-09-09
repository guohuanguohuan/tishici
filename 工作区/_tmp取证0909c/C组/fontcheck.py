# -*- coding: utf-8 -*-
"""意见33 补充：①交付字体 FY-w400BEVL100.ttf 真身核验（name/轴/实际笔画）；
②同法渲染 w400/w600/w900 对照；③全品多页 变式/例N 标签普查测量。只读。"""
import os
import glob
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from fontTools.ttLib import TTFont

OUT = os.path.dirname(os.path.abspath(__file__))
FONTS = r'C:\提示词\工作区\字替对照-0909\variantF\fonts'
PXD = r'C:\提示词\工作区\全品结构提取\数学选必一\导学案页图'
PX5 = 360 / 25.4
EM_MM = 12.03 * 25.4 / 72


def font_report(path):
    f = TTFont(path, lazy=True)
    name = f['name']
    g1 = name.getDebugName(1) or ''
    g2 = name.getDebugName(2) or ''
    g4 = name.getDebugName(4) or ''
    g6 = name.getDebugName(6) or ''
    g16 = name.getDebugName(16) or ''
    g17 = name.getDebugName(17) or ''
    axes = ''
    if 'fvar' in f:
        axes = ','.join(f'{a.axisTag}={a.minValue}-{a.defaultValue}-{a.maxValue}' for a in f['fvar'].axes)
    os2 = f['OS/2'] if 'OS/2' in f else None
    usw = os2.usWeightClass if os2 else -1
    print(f'{os.path.basename(path)}: fam={g1!r} sub={g2!r} full={g4!r} ps={g6!r} '
          f'typFam={g16!r} typSub={g17!r} usWeightClass={usw} fvar=[{axes}]')
    f.close()


def render_char(path, ch, px_em=400):
    """FreeType 渲染单字，返回灰度数组"""
    font = ImageFont.truetype(path, px_em)
    im = Image.new('L', (px_em * 2, px_em * 2), 255)
    d = ImageDraw.Draw(im)
    d.text((px_em // 2, px_em // 2), ch, font=font, fill=0)
    a = np.asarray(im)
    dk = a < 200
    ys, xs = np.where(dk)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def stroke_of_char(arr, thr=128):
    """竖笔宽：中带内二值 run 众数＋AA积分中位（同 bianshi.py 口径）"""
    h, w = arr.shape
    dark = arr < thr
    runs, ints = [], []
    for y in range(int(0.25 * h), h - int(0.2 * h)):
        row = dark[y]
        d = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
        ss = np.where(d == 1)[0]
        ee = np.where(d == -1)[0]
        for s, e in zip(ss, ee):
            if 2 <= e - s <= 0.45 * w:
                runs.append(e - s)
                prof = 1.0 - arr[y, max(0, s - 3):e + 3].astype(np.float64) / 255.0
                ints.append(prof.sum())
    if not runs:
        return None
    lens = np.array(runs)
    mode = float(np.median(lens))
    sel = [iv for iv, ln in zip(ints, lens) if abs(ln - mode) <= 1]
    return mode, float(np.median(sel))


print('==== ① 交付字体真身 ====')
for p in ['FY-w400.ttf', 'FY-w400BEVL100.ttf', 'FangYuanTi-w600圆-BEVL100.ttf']:
    font_report(os.path.join(FONTS, p))

print('==== ② 同尺渲染笔画（em=400px，折 12.03pt 比例） ====')
for p in ['FY-w400.ttf', 'FY-w400BEVL100.ttf', 'FangYuanTi-w600圆-BEVL100.ttf']:
    full = os.path.join(FONTS, p)
    for ch in '变式':
        arr = render_char(full, ch)
        m = stroke_of_char(arr)
        if m:
            em_px = arr.shape[0]
            print(f'{os.path.basename(p)} 「{ch}」: 竖粗={m[0]:.1f}px/{em_px}px_em'
                  f' 积分={m[1]:.1f}px → {m[1]/em_px:.4f}em')

print('==== ③ 全品多页「变式/例N」标签普查（360dpi） ====')


def char_boxes(label, thr=128, gap=3):
    colink = label.any(axis=0)
    xs = np.where(colink)[0]
    if len(xs) == 0:
        return []
    boxes, s, p = [], xs[0], xs[0]
    for v in xs[1:]:
        if v - p > gap:
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


def stroke_stats(gray, bbox, tag):
    x0, y0, x1, y1 = bbox
    h, w = y1 - y0 + 1, x1 - x0 + 1
    dark = gray < 128
    runs, ints = [], []
    for y in range(y0 + int(0.25 * h), y1 - int(0.2 * h)):
        row = dark[y, x0:x1 + 1]
        d = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
        ss = np.where(d == 1)[0]
        ee = np.where(d == -1)[0]
        for s, e in zip(ss, ee):
            if 2 <= e - s <= 0.45 * w:
                runs.append(e - s)
                prof = 1.0 - gray[y, x0 + max(0, s - 3):x0 + e + 3].astype(np.float64) / 255.0
                ints.append(prof.sum())
    core = gray[y0:y1 + 1, x0:x1 + 1]
    dens = float(dark[y0:y1 + 1, x0:x1 + 1].mean())
    if not runs:
        print(f'  {tag}: {w}x{h}px 密度={dens:.3f} （无有效竖笔）')
        return None
    lens = np.array(runs)
    mode = float(np.median(lens))
    sel = [iv for iv, ln in zip(ints, lens) if abs(ln - mode) <= 1]
    iw = float(np.median(sel))
    print(f'  {tag}: {w}x{h}px 竖粗二值中位={mode:.1f}px AA积分={iw:.2f}px={iw/PX5:.3f}mm'
          f'={iw/PX5/EM_MM:.3f}em 密度={dens:.3f}')
    return iw


# 逐页找行首「变式」标签：取每页上部区域扫描黑行；改用已知坐标附近搜索更稳——
# 直接在整页找「孤立的粗黑字符行」太宽泛，改为手工窗：各页 变式 出现在课中探究各探究点行首。
# 普查策略：找页面左/右栏内 与 变式标签同款（高度 45-55px 的连片粗黑行）——用例1/变式的行首特征：
# 行最左字符字面 46-54px 宽且行内前两字符密度 >0.45。
for n in range(5, 12):
    p = os.path.join(PXD, f'p{n:02d}.png')
    if not os.path.exists(p):
        continue
    a = np.asarray(Image.open(p).convert('L'))
    H, W = a.shape
    dark = a < 128
    rows_ink = dark.sum(axis=1)
    found = 0
    for y in range(200, H - 200, 4):
        if rows_ink[y] < 60:
            continue
        # 行带
        y0, y1 = y, y
        while y0 > 0 and rows_ink[y0 - 1] > 8:
            y0 -= 1
        while y1 < H - 1 and rows_ink[y1 + 1] > 8:
            y1 += 1
        y = y1 + 4
        if not (38 <= y1 - y0 <= 62):
            continue
        band = dark[y0:y1 + 1]
        cols = band.any(axis=0)
        xs = np.where(cols)[0]
        if len(xs) < 40:
            continue
        # 行首簇（前 110px 内）
        head = cols[xs[0]:xs[0] + 110]
        segs = char_boxes(head[None, :].astype(np.uint8) > 0)
        if len(segs) < 2:
            continue
        c0w = segs[0][2] - segs[0][0]
        c1w = segs[1][2] - segs[1][0]
        if not (42 <= c0w <= 58 and 40 <= c1w <= 58):
            continue
        # 密度判定（标签字密度显著高于宋体正文）
        d0 = dark[y0:y1 + 1, xs[0] + segs[0][0]:xs[0] + segs[0][2] + 1].mean()
        d1 = dark[y0:y1 + 1, xs[0] + segs[1][0]:xs[0] + segs[1][2] + 1].mean()
        if d0 > 0.45 and d1 > 0.22:
            crop = a[max(0, y0 - 6):y1 + 7, max(0, xs[0] - 8):xs[0] + 240]
            Image.fromarray(crop).save(os.path.join(OUT, f'_qp_p{n:02d}_label_y{y0}.png'))
            i0 = stroke_stats(a, (xs[0] + segs[0][0], y0, xs[0] + segs[0][2], y1), f'p{n:02d} y{y0} 字0')
            i1 = stroke_stats(a, (xs[0] + segs[1][0], y0, xs[0] + segs[1][2], y1), f'p{n:02d} y{y0} 字1')
            found += 1
            if found >= 4:
                break
    if found == 0:
        print(f'  p{n:02d}: 未检出标签行')
