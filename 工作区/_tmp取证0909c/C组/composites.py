# -*- coding: utf-8 -*-
"""取证证据拼图：意见31（表格同尺对比）＋意见33（变式标签同尺对比）。只读源，产物写本目录。"""
import os
import numpy as np
from PIL import Image, ImageDraw
import fitz

OUT = os.path.dirname(os.path.abspath(__file__))
QP = r'C:\提示词\工作区\全品结构提取\数学选必一\导学案页图'
PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
PX5 = 360 / 25.4


def togray(img):
    return img.convert('L') if img.mode != 'L' else img


def caption(img, text):
    base = Image.new('L', (img.width, img.height + 26), 255)
    base.paste(img, (0, 26))
    d = ImageDraw.Draw(base)
    d.text((4, 4), text, fill=0)
    return base


# ---------- 意见31：表格同尺对比（14.17px/mm） ----------
qp04 = Image.open(os.path.join(QP, 'p04.png')).convert('L')
qp_tab = qp04.crop((235, 2340, 1450, 3875))          # 全品 p04 特殊向量表（含外框）
doc = fitz.open(PDF)
page1 = doc[0]
# 我方表1 @600dpi：y 2388..4148, x 2585..4550 → clip(pt)=px/600*72
clip = fitz.Rect(2585 / 600 * 72, 2388 / 600 * 72, 4550 / 600 * 72, 4148 / 600 * 72)
pix = page1.get_pixmap(matrix=fitz.Matrix(600 / 72, 600 / 72), clip=clip, colorspace=fitz.csGRAY)
us_tab_600 = Image.frombytes('L', (pix.width, pix.height), pix.samples)
# 降到 14.17px/mm（360dpi 等尺）
us_tab = us_tab_600.resize((int(us_tab_600.width * PX5 / (600 / 25.4)),
                            int(us_tab_600.height * PX5 / (600 / 25.4))), Image.LANCZOS)
W = max(qp_tab.width, us_tab.width) + 8
cmp31 = Image.new('L', (W, qp_tab.height + us_tab.height + 90), 255)
cmp31.paste(caption(qp_tab, 'QP p04 (360dpi native)  row2line=16.16mm padT/B=4.02/4.30  head=9.03mm pad=2.8/3.1'), (0, 0))
cmp31.paste(caption(us_tab, 'OURS p1 (same 14.17px/mm)  row2line=12.19mm padT/B=2.16/1.65  head=7.87mm pad=2.2/2.2'),
            (0, qp_tab.height + 45))
cmp31.save(os.path.join(OUT, '_cmp31_table_same_scale.png'))
print('_cmp31_table_same_scale.png', cmp31.size)

# 放大细节：单行/表头行对比（同尺再 2 倍）
qp_head = qp04.crop((235, 2340, 800, 2480))          # 表头行
us_head = us_tab.crop((5, 2, int(5 + 565), int(2 + 140)))
d31 = Image.new('L', (max(qp_head.width, us_head.width) + 8, (qp_head.height + us_head.height) * 2 + 120), 255)
d31.paste(caption(qp_head.resize((qp_head.width * 2, qp_head.height * 2), Image.NEAREST),
                  'QP p04 header row (x2)'), (0, 0))
d31.paste(caption(us_head.resize((us_head.width * 2, us_head.height * 2), Image.NEAREST),
                  'OURS p1 header row (x2)'), (0, qp_head.height * 2 + 60))
d31.save(os.path.join(OUT, '_cmp31_header_zoom.png'))
print('_cmp31_header_zoom.png', d31.size)

# ---------- 意见33：变式标签同尺对比（14.17px/mm，再 3 倍放大） ----------
def panel(img, text):
    return caption(img, text)

qp6 = Image.open(os.path.join(QP, 'p06.png')).convert('L')
qp_bs_l = qp6.crop((246, 272, 420, 338))             # 全品 变式（左栏）
qp_bs_r = qp6.crop((1542, 272, 1716, 338))           # 全品 变式（右栏）
qp5 = Image.open(os.path.join(QP, 'p05.png')).convert('L')
qp_li1 = qp5.crop((1538, 2172, 1712, 2238))          # 全品 例1
# 我方 变式1：固定取 rect 左上角起 12.28×4.66mm 窗（fitz 单位＝pt，1mm=72/25.4pt）
page3 = doc[2]
hits = page3.search_for('变式')
rect = hits[0]
wmm, hmm = 174 / PX5 * 72 / 25.4, 66 / PX5 * 72 / 25.4
clip = fitz.Rect(rect.x0 - 1.0 * 72 / 25.4, rect.y0 - 0.7 * 72 / 25.4,
                 rect.x0 - 1.0 * 72 / 25.4 + wmm, rect.y0 - 0.7 * 72 / 25.4 + hmm)
pix = page3.get_pixmap(matrix=fitz.Matrix(12, 12), clip=clip, colorspace=fitz.csGRAY)
us_bs = Image.frombytes('L', (pix.width, pix.height), pix.samples)
us_bs = us_bs.resize((int(us_bs.width * PX5 / (12 * 72 / 25.4)), int(us_bs.height * PX5 / (12 * 72 / 25.4))),
                     Image.LANCZOS)

panels = [
    panel(qp_bs_l, 'QP p06 L: [bianshi]  stroke bian=8.7px shi=4.5px (zoom5 px)'),
    panel(qp_bs_r, 'QP p06 R: [bianshi]  stroke bian=9.3px shi=4.5px'),
    panel(qp_li1,  'QP p05: [li1]  stroke=7.5px'),
    panel(us_bs,   'OURS p3: [bianshi1] FY w400 BEVL100  stroke=3.8px'),
]
S = 3
pw = max(p.width for p in panels) * S
ph = sum(p.height * S + 8 for p in panels)
cmp33 = Image.new('L', (pw, ph), 255)
y = 0
for p in panels:
    big = p.resize((p.width * S, p.height * S), Image.NEAREST)
    cmp33.paste(big, (0, y))
    y += big.height + 8
cmp33.save(os.path.join(OUT, '_cmp33_bianshi_same_scale.png'))
print('_cmp33_bianshi_same_scale.png', cmp33.size)
