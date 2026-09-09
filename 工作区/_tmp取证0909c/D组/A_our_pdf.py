# -*- coding: utf-8 -*-
"""取证A：main.pdf 5组图文并排几何 + 判断题 √/× 字符定位（只读，不改项目文件）。
输出：D组/A_result.json + 每组裁片 A_g{i}_ctx.png（300dpi 带标注框）。"""
import os, json
import pymupdf as fitz

BASE = r'C:\提示词\工作区\字替对照-0909\variantF'
OUT = r'C:\提示词\工作区\_tmp取证0909c\D组'
doc = fitz.open(os.path.join(BASE, 'main.pdf'))
MM = 72 / 25.4  # pt per mm

# ---- 1. xref -> pixel size ----
media_dir = os.path.join(BASE, 'media', 'media')
media_sizes = {}
from PIL import Image
for n in range(1, 6):
    p = os.path.join(media_dir, f'image{n}.png')
    with Image.open(p) as im:
        media_sizes[im.size] = f'image{n}.png'

groups = []
for pno in range(len(doc)):
    page = doc[pno]
    infos = page.get_image_info(xrefs=True)
    if not infos:
        continue
    for info in infos:
        w, h = info['width'], info['height']
        name = media_sizes.get((w, h), f'xref{info.get("xref")}?{w}x{h}')
        bbox = fitz.Rect(info['bbox'])
        groups.append(dict(page=pno + 1, name=name, bbox=[round(v, 2) for v in bbox],
                           px=[w, h], xref=info.get('xref')))

# ---- 2. per group: stem lines left of image, overlapping vertically ----
res = []
for g in groups:
    page = doc[g['page'] - 1]
    r = fitz.Rect(g['bbox'])
    d = page.get_text('dict', clip=fitz.Rect(0, r.y0 - 60, page.rect.width, r.y1 + 60))
    lines = []
    for blk in d['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk['lines']:
            lr = fitz.Rect(ln['bbox'])
            if lr.x1 <= r.x0 + 3 and lr.y0 < r.y1 - 4:  # left of image & overlaps image v-span
                spans = [dict(text=''.join(s['text'] for s in sp['spans']) if 'spans' in sp else sp.get('text', ''),
                              bbox=[round(v, 2) for v in sp['bbox']],
                              size=round(sp['size'], 2), font=sp['font'])
                         for sp in ln['spans']]
                lines.append(dict(bbox=[round(v, 2) for v in lr], y0=round(lr.y0, 2),
                                  x1=round(lr.x1, 2), x0=round(lr.x0, 2), spans=spans))
    lines.sort(key=lambda L: L['y0'])
    # 仅保留与图盒竖向重叠 ≥ 半行的行（排除紧跟图底下方行）
    keep = [L for L in lines if L['y0'] < r.y1 - 4]
    stem = keep
    first = stem[0] if stem else None
    text_right_max = max((L['x1'] for L in stem), default=None)
    entry = dict(g)
    entry['stem_lines'] = stem
    if first and text_right_max is not None:
        entry['seam_pt'] = round(r.x0 - text_right_max, 2)
        entry['seam_mm'] = round((r.x0 - text_right_max) / MM, 2)
        # 图盒顶 - 题干首行字框顶（正=图更低）
        entry['topdiff_pt'] = round(r.y0 - first['y0'], 2)
        entry['topdiff_mm'] = round((r.y0 - first['y0']) / MM, 2)
        # 逐行缝
        entry['per_line_seam_mm'] = [round((r.x0 - L['x1']) / MM, 2) for L in stem]
        entry['first_line_text'] = ''.join(s['text'] for s in first['spans'])[:40]
    entry['placed_w_mm'] = round(r.width / MM, 2)
    entry['placed_h_mm'] = round(r.height / MM, 2)
    res.append(entry)

# ---- 3. 判断题 √/× 字符（页1-2）----
zhen = []
for pno in range(2):
    page = doc[pno]
    rd = page.get_text('rawdict')
    for blk in rd['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk['lines']:
            for sp in ln['spans']:
                for ch in sp['chars']:
                    if ch['c'] in ('×', '√', 'X', 'x'):
                        b = fitz.Rect(ch['bbox'])
                        if ch['c'] in ('×', '√'):
                            zhen.append(dict(page=pno + 1, c=ch['c'],
                                             bbox=[round(v, 2) for v in b],
                                             font=sp['font'], size=round(sp['size'], 2)))

out = dict(groups=res, zhen=zhen)
with open(os.path.join(OUT, 'A_result.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1, default=str)
print('== 图块 ==')
for e in res:
    print(f"p{e['page']} {e['name']:12s} bbox={e['bbox']} 墨缝mm={e.get('seam_mm')} 逐行={e.get('per_line_seam_mm')} 图顶-首行顶mm={e.get('topdiff_mm')} 置入={e['placed_w_mm']}x{e['placed_h_mm']}mm")
print('== 判断题字符 ==')
for z in zhen:
    print(z)
