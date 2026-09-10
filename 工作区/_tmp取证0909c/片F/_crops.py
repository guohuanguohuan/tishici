# -*- coding: utf-8 -*-
r"""片F 裁片：改前/改后同一异常行放大对照（标注空档实测）
产出：片F_对照_用户引例行.png / 片F_对照_变式1行p3.png / 片F_对照_判断题序号.png / 片F_对照_序号隙_p2.png
"""
import os
import pymupdf
from PIL import Image, ImageDraw, ImageFont

OUT = r'C:\提示词\工作区\_tmp取证0909c\片F'
BEFORE = os.path.join(OUT, '基线_main.pdf')
AFTER = os.path.join(r'C:\提示词\工作区', '字替对照-0909', 'variantF', 'main.pdf')
DPI = 400
SC = DPI / 72.0
PTMM = 72 / 25.4

try:
    F = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
    F2 = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
except Exception:
    F = F2 = ImageFont.load_default()


def render(pdf, pno, rect):
    doc = pymupdf.open(pdf)
    clip = pymupdf.Rect(*rect)
    pix = doc[pno - 1].get_pixmap(dpi=DPI, clip=clip)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def marks(im, clip, marks_pt, labels, color=(220, 0, 0)):
    dr = ImageDraw.Draw(im)
    for x in marks_pt:
        px = (x - clip[0]) * SC
        dr.line([(px, 0), (px, im.height)], fill=color, width=1)
    for i, (x, txt) in enumerate(labels):
        px = (x - clip[0]) * SC
        dr.text((px + 3, 4 + i * 24), txt, fill=color, font=F2)
    return im


def stack(pairs, path, title_h=34):
    w = max(im.width for im, _ in pairs)
    h = sum(im.height + title_h + 6 for im, _ in pairs)
    canvas = Image.new('RGB', (w, h), (255, 255, 255))
    dr = ImageDraw.Draw(canvas)
    y = 0
    for im, title in pairs:
        dr.text((4, y + 6), title, fill=(0, 0, 160), font=F)
        canvas.paste(im, (0, y + title_h))
        y += im.height + title_h + 6
    canvas.save(path)
    print(path, canvas.size)


# ---- A 用户引例行：变式1[简单(知识点三)]已知|a|=3√2…（#41「式/1」30.4pt、「简/单」10pt 原址）----
clipA = (305, 728, 552, 772)
imA0 = render(BEFORE, 5, clipA)
imA0 = marks(imA0, clipA, [349.6, 380.0, 406.2, 416.2, 460.7, 470.7, 501.7, 511.7],
             [(349.6, '式→1 = 30.37pt（用户引 30.4pt）'),
              (406.2, '简→单 = 10.03pt（用户引 10pt）'),
              (460.7, '知→识 10.03 / 识→点 10.04 / 点→三 10.04pt（字间整体拉大）')])
clipA2 = (305, 676, 552, 706)
imA1 = render(AFTER, 5, clipA2)
imA1 = marks(imA1, clipA2, [364.5, 372.7, 383.7, 390.7],
             [(364.5, '式→1 = 2.77pt（自然档）'),
              (383.7, '简→单 = 0pt（无空档）——整行重排后零拉伸')])
stack([(imA0, '改前（基线 0909c）p5 变式1·探究点七：式|1 空档 30.37pt＋简|单 10.03pt＋题侧字间 10pt×3'),
       (imA1, '改后（片F FINAL）p5 同一题：式|1 2.77pt，简|单 无空档——#41 行内拉伸治理生效')],
      os.path.join(OUT, '片F_对照_用户引例行.png'))

# ---- B p3 变式1 行（变|式 6.18pt→0）----
clipB = (305, 596, 552, 622)
imB0 = render(BEFORE, 3, clipB)
imB0 = marks(imB0, clipB, [340.89, 355.78], [(340.89, '变→式 = 6.18pt（CJKglue 被拉伸）')])
imB1 = render(AFTER, 3, clipB)
imB1 = marks(imB1, clipB, [334.6, 334.7], [(334.6, '变→式 = 0pt（kern0pt 刚性化）')])
stack([(imB0, '改前 p3 变式1 行：变|式 空档 6.18pt（0.51em，唯一残留 CJK-CJK 拉伸）'),
       (imB1, '改后 p3 同位置：变|式 0pt——CJK-CJK 拉伸异常行归零')],
      os.path.join(OUT, '片F_对照_变式1行p3.png'))

# ---- C 判断题序号（#43）----
clipC = (308, 578, 470, 600)
imC0 = render(BEFORE, 1, clipC)
imC0 = marks(imC0, clipC, [322.47, 333.66], [(322.47, '(1) 后隙 ink 4.239mm（随行拉伸浮动）')])
imC1 = render(AFTER, 1, clipC)
imC1 = marks(imC1, clipC, [322.47, 331.9], [(322.47, '(1) 后隙 ink 1.030mm（定值 kern 2.1pt，零拉伸）')])
stack([(imC0, '改前 p1 判断(1)：序号后隙 4.239mm（基线 6 处 1.094–4.239mm 浮动）'),
       (imC1, '改后 p1 判断(1)：序号后隙 1.030mm（全件 6 处 0.945–1.030mm，不随拉伸动）')],
      os.path.join(OUT, '片F_对照_判断题序号.png'))

# ---- D 判断题序号 p2（若 档）----
clipD = (49.8, 540, 210, 556)
imD0 = render(BEFORE, 2, clipD)
imD0 = marks(imD0, clipD, [61.14, 64.26], [(61.14, '(1) 后隙 ink 1.094mm（自然档）')])
imD1 = render(AFTER, 2, clipD)
imD1 = marks(imD1, clipD, [61.14, 63.3], [(61.14, '(1) 后隙 ink 0.945mm（钉 0.99±0.1mm 窗内）')])
stack([(imD0, '改前 p2 判断(1)：1.094mm'), (imD1, '改后 p2 判断(1)：0.945mm')],
      os.path.join(OUT, '片F_对照_序号隙_p2.png'))
print('done')
