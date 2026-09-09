# -*- coding: utf-8 -*-
"""片C 裁片：5 处编注改后放大＋=/∥ 墨隙标注。"""
import pymupdf
from PIL import Image, ImageDraw, ImageFont

PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
OUT = r'C:\提示词\工作区\_tmp取证0909c\片C'
doc = pymupdf.open(PDF)
try:
    f = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
except Exception:
    f = ImageFont.load_default()

targets = [
    ('与共线充要条件衔接', '编注1_条目3_与共线充要条件衔接'),
    ('见共面的充要条件及后续应用', '编注2_条目1_见共面的充要条件'),
    ('与共面的充要条件混淆', '编注3_条目2_与共面的充要条件混淆'),
    ('核心运算；注意数量积', '编注4_条目2_核心运算'),
    ('后续三余弦定理与点面距', '编注5_条目3_后续三余弦定理'),
]
for txt, name in targets:
    found = False
    for pno, page in enumerate(doc, 1):
        hits = page.search_for(txt)
        if hits:
            r = hits[0]
            clip = pymupdf.Rect(max(0, r.x0 - 8), r.y0 - 14, min(page.rect.width, r.x1 + 60), r.y1 + 14)
            pix = page.get_pixmap(dpi=400, clip=clip)
            pix.save(f'{OUT}\\片C_{name}.png')
            print(f'{name}: p{pno} y={r.y0:.1f} → 片C_{name}.png')
            found = True
            break
    if not found:
        print(f'{name}: 未找到「{txt}」')

# =/∥ 墨隙标注片：∥（p1 0∥a）＋=（p2 a=λb）
def annotate(pno, y0, y1, x0, x1, gaps, name, note):
    page = doc[pno - 1]
    clip = pymupdf.Rect(x0 - 26, y0 - 8, x1 + 26, y1 + 8)
    pix = page.get_pixmap(dpi=600, clip=clip)
    p = f'{OUT}\\_tmp_{name}.png'
    pix.save(p)
    im = Image.open(p).convert('RGB')
    dr = ImageDraw.Draw(im)
    sc = im.width / clip.width
    def px(x): return (x - clip.x0) * sc
    def py(y): return (y - clip.y0) * sc
    dr.rectangle([px(x0), py(y0), px(x1), py(y1)], outline=(255, 0, 0), width=2)
    dr.text((6, 4), note, fill=(180, 0, 0), font=f)
    im.save(f'{OUT}\\片C_{name}.png')
    print(f'{name}: → 片C_{name}.png {im.size}')

# p1 0∥a（∥ 墨盒 [228.6,236.87] y[557.6,567.4]）；标注左右墨隙（600dpi ink 实测值）
annotate(1, 557.6, 567.4, 228.6, 236.87, (1.10, 1.06), '墨隙_正文∥_0∥a',
         '正文 ∥：左墨隙 1.10mm／右墨隙 1.06mm（advance 胶 1.00/0.99mm）')
# p2 a=λb（= 墨盒 [147.62,154.25] y[126.9,136.95]）
annotate(2, 126.9, 136.95, 147.62, 154.25, (1.61, 1.40), '墨隙_正文=_a=λb',
         '正文 =：左墨隙 1.61mm／右墨隙 1.40mm（advance 胶 0.98mm；差＝字形边距）')
