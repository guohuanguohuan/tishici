# -*- coding: utf-8 -*-
# RECHECK组证据拼图：每图白底合成，找出全部墨迹连通域，裁剪「最小文字候选区」4x放大
# 每个候选标注程序测的簇高h
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

MED = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-X1衔接1\media检查'
OUT = os.path.join(MED, '_证据拼图.png')
RECHECK = ['image6','image9','image10','image16','image18','image22','image32','image43','image44','image45',
           'image47','image48','image49','image19','image21','image23','image25','image26','image31','image35',
           'image36','image52','image54','image55','image14','image50']

try: font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 18)
except Exception: font = ImageFont.load_default()

cells = []
for name in RECHECK:
    fn = name + '.png'
    img = Image.open(os.path.join(MED, fn)).convert('RGBA')
    bg = Image.new('RGBA', img.size, (255,255,255,255))
    img = Image.alpha_composite(bg, img).convert('L')
    a = np.array(img)
    H, W = a.shape
    hist, _ = np.histogram(a, bins=256, range=(0,256))
    total = a.size; sum_all = np.dot(np.arange(256), hist); sumB=0.0; wB=0; best_t=128; best_var=-1
    for t in range(256):
        wB += hist[t]
        if wB == 0: continue
        wF = total - wB
        if wF == 0: break
        sumB += t*hist[t]
        mB = sumB/wB; mF = (sum_all-sumB)/wF
        var = wB*wF*(mB-mF)**2
        if var > best_var: best_var=var; best_t=t
    th = min(best_t, 200)
    dark = a < th
    lab, n = ndimage.label(dark)
    objs = ndimage.find_objects(lab)
    cands = []
    for i, sl in enumerate(objs, 1):
        if sl is None: continue
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        area = (lab[sl]==i).sum()
        if 2 <= h <= 90 and 2 <= w <= 90:
            ar = max(h,w)/max(1,min(h,w))
            if ar <= 5.0 and area/(h*w) >= 0.15:
                cands.append((h, sl[0].start, sl[1].start, sl[0].stop, sl[1].stop))
    cands.sort(key=lambda c: c[0])
    # 取最小的8个簇，各自裁剪4x放大（含40px上下文）
    picks = cands[:8]
    crops = []
    for (h, y0, x0, y1, x1) in picks:
        cy0 = max(0, y0-25); cx0 = max(0, x0-25)
        cy1 = min(H, y1+25); cx1 = min(W, x1+25)
        crop = Image.fromarray(a[cy0:cy1, cx0:cx1]).resize(((cx1-cx0)*4, (cy1-cy0)*4), Image.NEAREST)
        cd = ImageDraw.Draw(crop)
        cd.rectangle([(x0-cx0)*4, (y0-cy0)*4, (x1-cx0)*4, (y1-cy0)*4], outline='red', width=2)
        cd.text((2,2), 'h=%d' % h, fill='blue', font=font)
        crops.append(crop)
    if not crops:
        crops = [Image.new('L', (200, 60), 255)]
    # 拼该图的证据行：图缩略＋裁剪串
    k = min(1.0, 460/W)
    thumb = Image.fromarray(a).resize((int(W*k), int(H*k))) if k<1 else Image.fromarray(a)
    ch = max(c.size[1] for c in crops) + 24
    cw = max(500, 460 + sum(c.size[0]+8 for c in crops[:6]))
    cell = Image.new('L', (cw, max(thumb.size[1], ch)+30), 255)
    d = ImageDraw.Draw(cell)
    d.text((4,2), '%s %dx%d (缩x%.2f)' % (name, W, H, k), fill=0, font=font)
    cell.paste(thumb, (4, 26))
    x = 470
    for c in crops[:6]:
        cell.paste(c, (x, 26))
        x += c.size[0]+8
    cells.append((name, cell))

# 纵向拼接
total_h = sum(c.size[1]+6 for _, c in cells)
max_w = max(c.size[0] for _, c in cells)
sheet = Image.new('L', (max_w+10, total_h+10), 255)
y = 5
for name, c in cells:
    sheet.paste(c, (5, y))
    y += c.size[1]+6
sheet.save(OUT)
print(OUT, sheet.size, len(cells))
