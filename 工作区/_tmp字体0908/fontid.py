# -*- coding: utf-8 -*-
# 方正书宋 vs 全品扫描 同文字形比对（鉴定用一次性脚本）
from PIL import Image, ImageFont, ImageDraw
import numpy as np

SCAN = r'C:\提示词\工作区\全品结构提取\数学选必一\导学案页图\p06.png'
SAMPLES = [
    ('其中是相反向量的有', (245, 840, 760, 945)),
    ('化简结果的向量；', (140, 1830, 720, 1910)),
]
FONTS = [
    ('FZShuSong',  r'C:\Users\28120\AppData\Local\Microsoft\Windows\Fonts\FZShuSong-Z01S.ttf', 0),
    ('SimSun',     r'C:\Windows\Fonts\simsun.ttc', 0),
    ('STZhongsong',r'C:\Windows\Fonts\STZHONGS.TTF', 0),
    ('FandolSong', r'c:\Users\28120\AppData\Roaming\TinyTeX\texmf-dist\fonts\opentype\public\fandol\FandolSong-Regular.otf', 0),
]

def tight(mask):
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return mask
    return mask[ys.min():ys.max()+1, xs.min():xs.max()+1]

def render_mask(text, path, index, em=400):
    f = ImageFont.truetype(path, em, index=index)
    d = ImageDraw.Draw(Image.new('L', (10, 10)))
    bb = d.textbbox((0, 0), text, font=f)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    im = Image.new('L', (w+em//2, h+em//2), 255)
    d = ImageDraw.Draw(im)
    d.text((em//4-bb[0], em//4-bb[1]), text, font=f, fill=0)
    return tight(np.array(im) < 128)

def scale_to(mask, h):
    im = Image.fromarray((~mask)*255)  # ink=black(0)
    w = max(1, round(mask.shape[1]*h/mask.shape[0]))
    im = im.resize((w, h), Image.LANCZOS)
    return np.array(im) < 128

def best_iou(scan, ren, scales):
    hs, ws = scan.shape
    best = (0.0, None)
    for s in scales:
        r = scale_to(ren, max(8, round(hs*s)))
        hr, wr = r.shape
        H = max(hs, hr)+24; W = max(ws, wr)+48
        for dy in range(-8, 9, 2):
            for dx in range(-16, 17, 2):
                canvas = np.zeros((H, W), dtype=bool)
                y0 = 12+(H-24-hs)//2+dy; x0 = 24+(W-48-ws)//2+dx
                canvas[y0:y0+hs, x0:x0+ws] = scan
                rr = np.zeros((H, W), dtype=bool)
                y1 = 12+(H-24-hr)//2; x1 = 24+(W-48-wr)//2
                rr[y1:y1+hr, x1:x1+wr] = r
                inter = np.logical_and(canvas, rr).sum()
                union = np.logical_or(canvas, rr).sum()
                iou = inter/union
                if iou > best[0]:
                    best = (iou, s)
    return best

def metrics(mask, em):
    h, w = mask.shape
    return dict(字面高=round(h/em, 3), 字面宽每字=round(w/em/MAXLEN, 3), 墨密=round(mask.mean(), 4))

im = Image.open(SCAN).convert('L')
results = {}
mont_rows = []
for text, box in SAMPLES:
    crop = np.array(im.crop(box))
    scan_m = tight(crop < 180)
    hs = scan_m.shape[0]
    mont_rows.append(('扫描件', Image.fromarray(np.where(scan_m, 0, 255).astype('uint8'))))
    for name, path, idx in FONTS:
        ren = render_mask(text, path, idx)
        key = (text[:4], name)
        if key not in results:
            results[key] = []
        iou, s = best_iou(scan_m, ren, np.arange(0.92, 1.101, 0.01))
        ink_h = ren.shape[0]/400
        dens = ren.mean()
        results[key].append((iou, s))
        mont_rows.append((f'{name} IoU={iou:.3f}', Image.fromarray(np.where(scale_to(ren, hs), 0, 255).astype('uint8'))))
        print(f'[{text[:4]}…] {name:12s} IoU={iou:.4f} (scale={s:.2f})  字面高/em={ink_h:.3f} 墨密={dens:.4f}')

# 汇总每字体两行平均 IoU
print('\n== 汇总（两行平均 IoU）==')
for name, _, _ in FONTS:
    vals = [results[(t[:4], name)][0][0] for t, _ in SAMPLES]
    print(f'{name:12s} avg IoU = {sum(vals)/len(vals):.4f}')

# 拼对照图
pad = 12
wmax = max(r.width for _, r in mont_rows)
Htot = sum(r.height for _, r in mont_rows) + pad*(len(mont_rows)+1)
canvas = Image.new('L', (wmax+300, Htot), 255)
d = ImageDraw.Draw(canvas)
y = pad
for label, row in mont_rows:
    canvas.paste(row, (280, y))
    d.text((10, y+row.height//3), label, fill=0)
    y += row.height+pad
canvas.save('montage_0908.png')
print('\nmontage_0908.png saved')
