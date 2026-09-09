# -*- coding: utf-8 -*-
"""片C #34 对比板 v2：同尺 16px/mm，标签在每片上方。"""
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont

OURS = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
QP = r'C:\提示词\工作区\全品结构提取\数学选必一\导学案页图\p04.png'
OUT = r'C:\提示词\工作区\_tmp取证0909c\片C'
HX = 2977 / 210
S = 16

doc = pymupdf.open(OURS)
page = doc[1]
pix = page.get_pixmap(dpi=600, clip=pymupdf.Rect(194, 522, 209, 537))
pix.save(OUT + r'\_board_ours_sqrt.png')
im_s = Image.open(OUT + r'\_board_ours_sqrt.png').convert('L')
pix = page.get_pixmap(dpi=600, clip=pymupdf.Rect(251, 521, 268, 538))
pix.save(OUT + r'\_board_ours_x.png')
im_x = Image.open(OUT + r'\_board_ours_x.png').convert('L')
qp = Image.open(QP).convert('L')
qs = qp.crop((2304, 1417, 2367, 1485))
qx = qp.crop((2624, 1424, 2679, 1478))


def trim(im, thr=245):
    a = np.array(im)
    mask = a < thr
    ys, xs = np.where(mask)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def rescale(img, pxmm_in):
    w, h = img.size
    return img.resize((max(1, int(w * S / pxmm_in)), max(1, int(h * S / pxmm_in))), Image.LANCZOS)


tiles = [
    (trim(im_x), 600 / 25.4, 'ours x', '2.41x2.41 TikZ'),
    (trim(qx), HX, 'quanpin x', '2.40x2.40'),
    (trim(im_s), 600 / 25.4, 'ours sqrt', '3.56x3.39 FZFSK'),
    (trim(qs), HX, 'quanpin sqrt', '2.89x3.39'),
]
scaled = [(rescale(t, k), l1, l2) for t, k, l1, l2 in tiles]
try:
    f = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
    f2 = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
except Exception:
    f = f2 = ImageFont.load_default()
pad = 14
W = sum(t.width for t, _, _ in scaled) + pad * (len(scaled) + 1)
H = max(t.height for t, _, _ in scaled) + 76
board = Image.new('L', (W, H), 255)
dr = ImageDraw.Draw(board)
xx = pad
for t, l1, l2 in scaled:
    dr.text((xx, 10), l1, fill=0, font=f)
    dr.text((xx, 32), l2, fill=80, font=f2)
    board.paste(t, (xx, 62))
    xx += t.width + pad
board.save(OUT + r'\片C_x_sqrt_对比板.png')
print('saved', board.size)
