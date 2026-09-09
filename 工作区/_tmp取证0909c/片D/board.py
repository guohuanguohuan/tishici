# -*- coding: utf-8 -*-
"""片D 0909c 证据板：变式标签双字重（同尺对比板＋600dpi 高倍裁片＋笔画实测标注）。
口径：360dpi=14.1732px/mm（与全品 p06 页图同尺）；600dpi 高倍另附。"""
import os
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
OUR_AFTER = r"C:/提示词/工作区/字替对照-0909/variantF/main.pdf"
OUR_BEFORE = OUT + "/基线_main.pdf"
QP6 = r"C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/p06.png"
F_TXT = "C:/Windows/Fonts/msyh.ttc"
FONT = ImageFont.truetype(F_TXT, 15)
FONT_S = ImageFont.truetype(F_TXT, 13)

def label_crop_ours(path, pno, dpi):
    doc = pymupdf.open(path)
    page = doc[pno]
    for bl in page.get_text('dict')['blocks']:
        for ln in bl.get('lines', []):
            for sp in ln['spans']:
                if '变' in sp['text'] and 'Fang' in sp['font']:
                    bb = sp['bbox']
                    clip = pymupdf.Rect(bb[0] - 3, bb[1] - 3, bb[2] + 3, bb[3] + 3)
                    pm = page.get_pixmap(dpi=dpi, clip=clip, colorspace=pymupdf.csGRAY)
                    g = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width).copy()
                    doc.close()
                    return g
    doc.close()
    return None

def ink_crop(g, pad=2):
    dk = g < 128
    ys, xs = np.where(dk)
    return g[max(0, ys.min() - pad):ys.max() + pad + 1, max(0, xs.min() - pad):xs.max() + pad + 1]

def char_split(g, gap=3):
    lab = g < 128
    colink = lab.any(axis=0)
    xs = np.where(colink)[0]
    boxes, s, p = [], xs[0], xs[0]
    for v in xs[1:]:
        if v - p > gap:
            boxes.append((s, p)); s = v
        p = v
    boxes.append((s, p))
    out = []
    for x0, x1 in boxes:
        sub = lab[:, x0:x1 + 1]
        yy = np.where(sub.any(axis=1))[0]
        out.append((x0, yy.min(), x1, yy.max()))
    return out

# ---- 素材 ----
our_after_360 = ink_crop(label_crop_ours(OUR_AFTER, 2, 360))   # p3 首个变式1
our_before_360 = ink_crop(label_crop_ours(OUR_BEFORE, 2, 360))
our_after_600 = ink_crop(label_crop_ours(OUR_AFTER, 2, 600))
qp = np.asarray(Image.open(QP6).convert('L'))

def qp_label(win):
    """全品窗口→只取前两个字（变式；后随 如/（1） 非标签，剔除）"""
    wx0, wy0, wx1, wy1 = win
    sub = qp[wy0:wy1, wx0:wx1]
    cbs = char_split(sub)
    xs0, ys0 = cbs[0][0], min(c[1] for c in cbs[:2])
    xs1, ys1 = cbs[1][2], max(c[3] for c in cbs[:2])
    return ink_crop(sub[ys0:ys1 + 1, xs0:xs1 + 1])

qp_left = qp_label((200, 230, 480, 360))
qp_right = qp_label((1480, 230, 1760, 360))

S = 3  # 展示放大倍率（nearest）
def up(img, s=S):
    return Image.fromarray(img).resize((img.shape[1] * s, img.shape[0] * s), Image.NEAREST)

tiles = [
    ("全品 p06 左 真迹", qp_left, "变 8.73px / 式 4.50px"),
    ("全品 p06 右 真迹", qp_right, "变 9.34px / 式 4.51px"),
    ("我方 改后 (p3)", our_after_360, "变 7.08px / 式 4.39px"),
    ("我方 改前 (p3)", our_before_360, "变 3.86px / 式 3.85px"),
]
TH = max(t[1].shape[0] for t in tiles) * S + 46
TW = max(t[1].shape[1] for t in tiles) * S + 20
board = Image.new('L', (TW * 4 + 50, TH), 255)
dr = ImageDraw.Draw(board)
for i, (name, img, meas) in enumerate(tiles):
    x = 10 + i * (TW + 10)
    board.paste(up(img), (x + 10, 34))
    dr.text((x + 10, 8), name, fill=0, font=FONT)
    dr.text((x + 10, TH - 40), meas, fill=0, font=FONT_S)
board.save(OUT + "/片D_变式双字重_同尺对比板.png")
print("saved 同尺对比板", board.size)

# ---- 600dpi 高倍：我方 600dpi vs 全品 p06 上采样 600/360 同尺 ----
qp_left_600 = np.asarray(Image.fromarray(qp_left).resize(
    (round(qp_left.shape[1] * 600 / 360), round(qp_left.shape[0] * 600 / 360)), Image.LANCZOS))
h = max(our_after_600.shape[0], qp_left_600.shape[0]) + 50
w = max(our_after_600.shape[1], qp_left_600.shape[1]) + 20
b2 = Image.new('L', (w * 2 + 60, h), 255)
d2 = ImageDraw.Draw(b2)
b2.paste(Image.fromarray(our_after_600), (10, 34))
b2.paste(Image.fromarray(qp_left_600), (w + 50, 34))
d2.text((10, 8), "我方改后 600dpi（变 11.78 / 式 7.29px）", fill=0, font=FONT)
d2.text((w + 50, 8), "全品 p06 左 ×1.67 同尺（变 14.5 / 式 7.5px）", fill=0, font=FONT)
b2.save(OUT + "/片D_变式双字重_600dpi高倍.png")
print("saved 600dpi 高倍", b2.size)

# ---- 笔画标注图（我方 600dpi，逐字标出竖笔实测） ----
ann = Image.fromarray(our_after_600).convert('RGB')
sc = 6
ann = ann.resize((ann.width * sc, ann.height * sc), Image.NEAREST)
da = ImageDraw.Draw(ann)
for i, cb in enumerate(char_split(our_after_600)):
    x0, y0, x1, y1 = [v * sc for v in cb]
    da.rectangle([x0, y0, x1, y1], outline=(255, 0, 0))
    lab = ('变 11.78px', '式 7.29px', '1 8.10px')[i] if i < 3 else f'ch{i}'
    da.text((x0, max(0, y0 - 20)), lab, fill=(255, 0, 0), font=FONT_S)
ann.save(OUT + "/片D_变式双字重_笔画标注_600dpi.png")
print("saved 笔画标注")
