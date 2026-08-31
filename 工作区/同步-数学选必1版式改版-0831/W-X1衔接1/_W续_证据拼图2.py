# -*- coding: utf-8 -*-
# 证据拼图v2：对不确定图框出v4最小串位置（红框）＋周边上下文，3x放大
import os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

MED = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-X1衔接1\media检查'
TARGETS = ['image14','image15','image16','image18','image22','image32','image33','image34','image35','image42',
           'image47','image48','image50','image53','image55']
try: font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 18)
except Exception: font = ImageFont.load_default()

def otsu(a):
    hist,_ = np.histogram(a, bins=256, range=(0,256))
    total=a.size; sum_all=np.dot(np.arange(256),hist); sumB=0.0; wB=0; best=128; bv=-1
    for t in range(256):
        wB+=hist[t]
        if wB==0: continue
        wF=total-wB
        if wF==0: break
        sumB+=t*hist[t]
        mB=sumB/wB; mF=(sum_all-sumB)/wF
        v=wB*wF*(mB-mF)**2
        if v>bv: bv=v; best=t
    return min(best,200)

cells = []
for name in TARGETS:
    fn = name+'.png'
    img = Image.open(os.path.join(MED, fn)).convert('RGBA')
    bg = Image.new('RGBA', img.size, (255,255,255,255))
    img = Image.alpha_composite(bg, img).convert('L')
    a = np.array(img); H,W = a.shape
    dark = a < otsu(a)
    lab, n = ndimage.label(dark)
    objs = ndimage.find_objects(lab)
    cands = []
    for i,sl in enumerate(objs,1):
        if sl is None: continue
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start
        area=(lab[sl]==i).sum()
        if 6<=h<=130 and 2<=w<=130:
            ar=max(h,w)/max(1,min(h,w))
            if ar<=5 and area/(h*w)>=0.15:
                cands.append({'h':h,'w':w,'y0':sl[0].start,'y1':sl[0].stop,'x0':sl[1].start,'x1':sl[1].stop})
    cands.sort(key=lambda c:c['h'])
    # 全图白底RGB＋红框标注最小6簇
    rgb = Image.fromarray(a).convert('RGB')
    dr = ImageDraw.Draw(rgb)
    for c in cands[:6]:
        dr.rectangle([c['x0']-3, c['y0']-3, c['x1']+3, c['y1']+3], outline='red', width=2)
    # 放大3x局部：最小簇周围
    zooms = []
    for c in cands[:3]:
        cx0=max(0,c['x0']-60); cy0=max(0,c['y0']-40); cx1=min(W,c['x1']+60); cy1=min(H,c['y1']+40)
        z = rgb.crop((cx0,cy0,cx1,cy1))
        z = z.resize((z.size[0]*3, z.size[1]*3), Image.NEAREST)
        zd = ImageDraw.Draw(z)
        zd.text((4,4),'h=%d'%c['h'], fill='blue', font=font)
        zooms.append(z)
    k = min(1.0, 560/W)
    thumb = rgb.resize((int(W*k), int(H*k))) if k<1 else rgb
    zh = max((z.size[1] for z in zooms), default=40)+10
    zw = sum(z.size[0]+10 for z in zooms)+10
    cw = max(580+zw, thumb.size[0]+10)
    cell = Image.new('RGB', (cw, max(thumb.size[1], zh)+34), 'white')
    d = ImageDraw.Draw(cell)
    d.text((4,2), '%s %dx%d x%.2f' % (name, W, H, k), fill='black', font=font)
    cell.paste(thumb, (4, 28))
    x = 580
    for z in zooms:
        cell.paste(z, (x, 28)); x += z.size[0]+10
    cells.append(cell)

tot_h = sum(c.size[1]+6 for c in cells)
max_w = max(c.size[0] for c in cells)
sheet = Image.new('RGB', (max_w+10, tot_h+10), 'white')
y=5
for c in cells:
    sheet.paste(c, (5,y)); y += c.size[1]+6
outp = os.path.join(MED, '_证据拼图v2.png')
sheet.save(outp)
print(outp, sheet.size, len(cells))
