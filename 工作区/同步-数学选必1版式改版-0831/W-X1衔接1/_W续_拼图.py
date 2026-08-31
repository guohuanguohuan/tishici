# -*- coding: utf-8 -*-
# 生成检视拼图：每图缩放到宽<=480，白底黑框，上方标注 文件名|原尺寸|缩放系数
import os
from PIL import Image, ImageDraw, ImageFont

MED = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-X1衔接1\media检查'
files = sorted([f for f in os.listdir(MED) if f.startswith('image') and f.endswith('.png') and '检视' not in f and '拼图' not in f],
               key=lambda x: int(''.join(ch for ch in x if ch.isdigit())))
try:
    font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 16)
except Exception:
    font = ImageFont.load_default()

CELL_W = 500
PAD = 6
per_sheet = 14
sheets = [files[i:i+per_sheet] for i in range(0, len(files), per_sheet)]
for si, group in enumerate(sheets, 1):
    cells = []
    max_h = 0
    for fn in group:
        img = Image.open(os.path.join(MED, fn)).convert('RGBA')
        bg = Image.new('RGBA', img.size, (255,255,255,255))
        img = Image.alpha_composite(bg, img).convert('RGB')
        W, H = img.size
        k = min(1.0, 480 / W)
        if k < 1.0:
            img = img.resize((int(W*k), int(H*k)), Image.LANCZOS)
        cells.append((fn, W, H, k, img))
        max_h = max(max_h, img.size[1])
    row_h = max_h + 30
    cols = 2
    rows = (len(cells)+1)//2
    sheet = Image.new('RGB', (CELL_W*cols+PAD*(cols+1), row_h*rows+PAD*(rows+1)), 'white')
    d = ImageDraw.Draw(sheet)
    for idx, (fn, W, H, k, img) in enumerate(cells):
        r, c = divmod(idx, cols)
        x0 = PAD + c*(CELL_W+PAD); y0 = PAD + r*(row_h+PAD)
        d.rectangle([x0, y0, x0+CELL_W, y0+row_h-4], outline='black')
        d.text((x0+4, y0+4), '%s %dx%d x%.3f' % (fn.replace('.png',''), W, H, k), fill='red', font=font)
        sheet.paste(img, (x0+ (CELL_W-img.size[0])//2, y0+26))
    outp = os.path.join(MED, '_总览拼图%d.png' % si)
    sheet.save(outp)
    print(outp, sheet.size, [c[0] for c in cells])
