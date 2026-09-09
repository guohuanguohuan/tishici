# -*- coding: utf-8 -*-
"""片C 对比板（终版）：我方 ×/√（600dpi）vs 全品 p04 说明行真迹，同尺 16px/mm。"""
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
pix = page.get_pixmap(dpi=600, clip=pymupdf.Rect(253.7, 526.3, 261.6, 534.1))
pix.save(OUT + r'\_board_ours_x.png')
im_x = Image.open(OUT + r'\_board_ours_x.png').convert('L')
pix = page.get_pixmap(dpi=600, clip=pymupdf.Rect(195.5, 523.0, 207.5, 535.5))
pix.save(OUT + r'\_board_ours_sqrt.png')
im_s = Image.open(OUT + r'\_board_ours_sqrt.png').convert('L')
qp = Image.open(QP).convert('L')
qs = qp.crop((2312, 1424, 2360, 1478))
qx = qp.crop((2630, 1430, 2672, 1472))


def trim(im, thr=240):
    a = np.array(im)
    ys, xs = np.where(a < thr)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def rescale(img, k):
    return img.resize((max(1, int(img.width * S / k)), max(1, int(img.height * S / k))), Image.LANCZOS)


tiles = [
    (trim(im_x), 600 / 25.4, 'ours × 2.41×2.41', 'TikZ 自绘（#34）'),
    (trim(qx), HX, '全品 × 2.40×2.40', 'p04 说明行真迹'),
    (trim(im_s), 600 / 25.4, 'ours √ 3.56×3.39', 'FZFSK radical（#37）'),
    (trim(qs), HX, '全品 √ 2.89×3.39', 'p04 说明行真迹'),
]
scaled = [(rescale(t, k), l1, l2) for t, k, l1, l2 in tiles]
f = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
f2 = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
colw, pad = 176, 12
W = colw * len(scaled) + pad * 2
H = max(t.height for t, _, _ in scaled) + 86
board = Image.new('L', (W, H), 255)
dr = ImageDraw.Draw(board)
xx = pad
for t, l1, l2 in scaled:
    dr.text((xx, 10), l1, fill=0, font=f)
    dr.text((xx, 34), l2, fill=90, font=f2)
    board.paste(t, (xx + (colw - pad * 2 - t.width) // 2, 64))
    xx += colw
board.save(OUT + r'\片C_x_sqrt_对比板.png')
print('saved', board.size)
