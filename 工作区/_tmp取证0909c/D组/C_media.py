# -*- coding: utf-8 -*-
"""取证C1：media/image1-5.png 白边实测（非白像素 bbox vs 全幅），按置入宽 33.12mm 折算 mm。"""
import os, json
from PIL import Image
BASE = r'C:\提示词\工作区\字替对照-0909\variantF\media\media'
OUT = r'C:\提示词\工作区\_tmp取证0909c\D组'
placed_w_mm = 33.12  # 0.40\linewidth 列 82.8mm
rows = []
for n in range(1, 6):
    p = os.path.join(BASE, f'image{n}.png')
    im = Image.open(p).convert('RGB')
    w, h = im.size
    g = im.convert('L').point(lambda v: 255 if v < 245 else 0)
    bb = g.getbbox()
    l, t, r, b = bb
    scale = placed_w_mm / w  # mm per px（横向）；纵向同 scale（等比置入）
    rows.append(dict(name=f'image{n}.png', px=[w, h],
                     white_l=round(l*scale,2), white_t=round(t*scale,2),
                     white_r=round((w-r)*scale,2), white_b=round((h-b)*scale,2),
                     ink_w_mm=round((r-l)*scale,2), ink_h_mm=round((b-t)*scale,2),
                     px_bbox=list(bb)))
    # 存一张带 bbox 的缩略证据图
    from PIL import ImageDraw
    dr = ImageDraw.Draw(im)
    dr.rectangle(bb, outline=(255, 0, 0), width=max(2, w//300))
    im.save(os.path.join(OUT, f'C_media_image{n}_bbox.png'))
json.dump(rows, open(os.path.join(OUT, 'C_media_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for r in rows:
    print(f"{r['name']} {r['px'][0]}x{r['px'][1]}px 白边 左{r['white_l']} 上{r['white_t']} 右{r['white_r']} 下{r['white_b']}mm  墨幅 {r['ink_w_mm']}x{r['ink_h_mm']}mm")
