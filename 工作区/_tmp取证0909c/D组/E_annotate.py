# -*- coding: utf-8 -*-
"""E：终版证据图标注。
E1: 我方 g1-g5 ctx 标注（图盒/图墨/文右缘min缝/首行墨顶/顶差）
E2: 全品 p06 变式标注（图bbox/①行顶/缝）
E3: 全品 说明行 ×√ 标注 + 全品×vs我方× 同比例对比板
"""
import json, os
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont

OUT = r'C:\提示词\工作区\_tmp取证0909c\D组'
BASE = r'C:\提示词\工作区\字替对照-0909\variantF'
MMPT = 72/25.4
B = json.load(open(os.path.join(OUT, 'B_result.json'), encoding='utf-8'))
A = json.load(open(os.path.join(OUT, 'A_result.json'), encoding='utf-8'))
doc = fitz.open(os.path.join(BASE, 'main.pdf'))

def font(sz):
    try:
        return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', sz)
    except Exception:
        return ImageFont.load_default()

# ---------- E1 我方 5 组 ----------
for e in B['side']:
    im = Image.open(e['ctx_png']).convert('RGB')
    dr = ImageDraw.Draw(im)
    page = doc[e['page']-1]
    g = [x for x in A['groups'] if x['name'] == e['name'] and x['page'] == e['page']][0]
    # 重算 clip（与 B_ink.py 同参）
    r = fitz.Rect(g['bbox'])
    col_left = r.x0 - 140
    d = page.get_text('dict', clip=fitz.Rect(col_left, r.y0-30, page.rect.width, r.y1+10))
    stem = []
    for blk in d['blocks']:
        if blk['type'] != 0: continue
        for ln in blk['lines']:
            lr = fitz.Rect(ln['bbox'])
            if lr.x0 >= col_left-2 and lr.x1 <= r.x0+4 and lr.y0 < r.y1-4 and lr.y1 > r.y0-4:
                stem.append(lr)
    stem.sort(key=lambda L: L.y0)
    pad = 6
    clip = fitz.Rect(min(L.x0 for L in stem)-pad, min(L.y0 for L in stem)-pad, r.x1+pad, max(r.y1, max(L.y1 for L in stem))+pad)
    sc = im.width/clip.width
    def topx(x): return (x-clip.x0)*sc
    def topy(y): return (y-clip.y0)*sc
    # 图盒（蓝）
    dr.rectangle([topx(r.x0), topy(r.y0), topx(r.x1), topy(r.y1)], outline=(0,120,255), width=2)
    # 图墨（红）
    if e['img_ink_pt']:
        x0,y0,x1,y1 = e['img_ink_pt']
        dr.rectangle([topx(x0), topy(y0), topx(x1), topy(y1)], outline=(255,0,0), width=2)
    # 文墨右缘min缝位置（黄）：最窄缝行的行带 + 图墨左缘线
    img_ink_x0 = e['img_ink_pt'][0]
    dr.line([topx(img_ink_x0), 0, topx(img_ink_x0), im.height], fill=(255,200,0), width=2)
    # 首行墨顶（绿）
    fx0, fy0, fx1, fy1 = stem[0]
    sub_top = e['topdiff_ink_pt']
    ty = topy(fy0) + (0)
    dr.line([0, topy(stem[0].y0), topx(stem[0].x1), topy(stem[0].y0)], fill=(0,180,0), width=1)
    f = font(22)
    dr.text((10, 8), f"seam_ink={e['seam_ink_mm']}mm  top_ink={e['topdiff_ink_mm']}mm  (box top={e['topdiff_box_mm']}mm)", fill=(180,0,180), font=f)
    im.save(e['ctx_png'].replace('_ctx.png', '_ctx_标注.png'))
    print('saved', os.path.basename(e['ctx_png'].replace('_ctx.png', '_ctx_标注.png')))

# ---------- E2 全品 p06 变式 ----------
HX, VY = 2977/210, 4176/297
src = Image.open(r'C:\提示词\工作区\全品结构提取\数学选必一\导学案页图\p06.png')
ox, oy = 240, 240
crop = src.crop((ox, oy, 1460, 910)).convert('RGB')
dr = ImageDraw.Draw(crop)
def pr(x): return (x-ox)/HX* (HX)  # page px → crop px（同尺度，直接减 offset）
# 图bbox
dr.rectangle([1010-ox, 474-oy, 1429-ox, 829-oy], outline=(255,0,0), width=4)
dr.line([1010-ox, 0, 1010-ox, crop.height], fill=(255,200,0), width=3)
# ①行顶
dr.line([0, 447-oy, 800-ox, 447-oy], fill=(0,160,0), width=3)
# 文右缘 626
dr.line([626-ox, 447-oy, 626-ox, 829-oy], fill=(255,0,255), width=3)
f = font(34)
dr.text((20, 20), '图墨bbox 29.63x25.32mm; 图顶-①行顶=+1.92mm; 缝(①-④带)min=27.1 中位=29.8mm', fill=(160,0,160), font=f)
crop.save(os.path.join(OUT, 'E2_p06_bianshi_标注.png'))
print('saved E2')

# ---------- E3 全品 ×√ 标注 + 对比板 ----------
im = Image.open(os.path.join(OUT, 'D2_p04_zhenhead1.png')).convert('RGB')
dr = ImageDraw.Draw(im)
dr.rectangle([1154, 39, 1187, 72], outline=(255,0,0), width=3)
dr.rectangle([834, 32, 875, 79], outline=(0,120,255), width=3)
f = font(26)
dr.text((880, 6), 'quanpin ×=2.40x2.42mm', fill=(255,0,0), font=f)
dr.text((620, 6), '√=2.96x3.41mm', fill=(0,90,255), font=f)
im.save(os.path.join(OUT, 'E3_p04_zhenhead_标注.png'))

# 对比板：同 mm 比例并排（600dpi 我方 vs 14.176px/mm 全品 放到同尺度 8px/mm）
our_x = Image.open(os.path.join(OUT, 'B2b_z2_×_p1_tight.png')).convert('L')
our_sqrt = Image.open(os.path.join(OUT, 'B2b_z0_√_p1_tight.png')).convert('L')
qp = Image.open(os.path.join(OUT, 'D2_p04_zhenhead1.png')).convert('L')
qx = qp.crop((1150, 35, 1191, 76))    # 全品×+2px边
qs = qp.crop((830, 28, 879, 83))      # 全品√
S = 8  # px per mm
def rescale(img, pxmm_in, pxmm_out):
    w, h = img.size
    return img.resize((max(1,int(w*pxmm_out/pxmm_in)), max(1,int(h*pxmm_out/pxmm_in))), Image.LANCZOS)
tiles = [rescale(our_x, 600/25.4, S), rescale(qx, HX, S), rescale(our_sqrt, 600/25.4, S), rescale(qs, HX, S)]
labels = ['ours x 1.69x1.69', 'quanpin x 2.40x2.42', 'ours radical 3.5x3.4', 'quanpin sqrt 2.96x3.41']
Wt = sum(t.width for t in tiles) + 50; Ht = max(t.height for t in tiles) + 50
board = Image.new('L', (Wt, Ht), 255)
drb = ImageDraw.Draw(board)
xx = 10
for t, lb in zip(tiles, labels):
    board.paste(t, (xx, 30))
    drb.text((xx, 8), lb, fill=0, font=font(15))
    xx += t.width + 10
board.save(os.path.join(OUT, 'E3_x_sqrt_对比板.png'))
print('saved E3 board')
