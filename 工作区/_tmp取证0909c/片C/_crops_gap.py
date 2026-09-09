# -*- coding: utf-8 -*-
"""片C 墨隙标注片（终版，正确标注 a=λb 与 λ=0 两处）。"""
import pymupdf
from PIL import Image, ImageDraw, ImageFont

PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
OUT = r'C:\提示词\工作区\_tmp取证0909c\片C'
doc = pymupdf.open(PDF)
f = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)


def annotate(pno, y0, y1, x0, x1, name, note):
    page = doc[pno - 1]
    clip = pymupdf.Rect(x0 - 30, y0 - 10, x1 + 30, y1 + 10)
    pix = page.get_pixmap(dpi=600, clip=clip)
    p = OUT + r'\_tmp_ann.png'
    pix.save(p)
    im = Image.open(p).convert('RGB')
    sc = im.width / clip.width
    canvas = Image.new('RGB', (im.width, im.height + 46), (255, 255, 255))
    canvas.paste(im, (0, 0))
    dr = ImageDraw.Draw(canvas)
    dr.rectangle([(x0 - clip.x0) * sc, (y0 - clip.y0) * sc,
                  (x1 - clip.x0) * sc, (y1 - clip.y0) * sc], outline=(255, 0, 0), width=2)
    dr.text((8, im.height + 10), note, fill=(180, 0, 0), font=f)
    canvas.save(f'{OUT}\\片C_{name}.png')
    print('saved', f'片C_{name}.png', canvas.size)


annotate(2, 237.0, 247.1, 57.67, 64.30, '墨隙_正文=_a=λb',
         '正文 =（a=λb，条目2）：左墨隙 0.93mm／右墨隙 1.57mm（advance 胶 0.996mm）')
annotate(2, 126.9, 136.95, 147.62, 154.25, '墨隙_正文=_λ=0',
         '正文 =（λ=0，条目1）：左墨隙 1.61mm／右墨隙 1.40mm（advance 胶 0.982mm；差＝字形边距）')
annotate(1, 557.6, 567.4, 228.6, 236.87, '墨隙_正文∥_0∥a',
         '正文 ∥（0∥a，条目3）：左墨隙 1.10mm／右墨隙 1.06mm（advance 胶 1.00/0.99mm）')
annotate(2, 217.1, 226.9, 111.0, 119.27, '墨隙_正文∥_判断a∥b',
         '判断题干 ∥（a∥b）：左墨隙 0.68mm／右墨隙 0.93mm（改前同对 1.82/2.16）')
