# -*- coding: utf-8 -*-
"""Build the same-scale comparison sheet (600dpi): top = source bitmap at print width, bottom = redraw."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DPI = 600
W_MM = 41.1
PANEL_W = int(round(W_MM / 25.4 * DPI))          # 971 px
PX = 25.4 / DPI

src_rgba = Image.open(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image1.png")
a = np.array(src_rgba)[..., 3].astype(float) / 255.0
gray = Image.fromarray((255 * (1 - a)).astype(np.uint8))          # ink on white
H_SRC = int(round(gray.size[1] / gray.size[0] * PANEL_W))
src_panel = gray.resize((PANEL_W, H_SRC), Image.LANCZOS)

ren = Image.open('_img1_render600.png').convert('L')
ren_panel = ren.resize((PANEL_W, int(round(ren.size[1] / ren.size[0] * PANEL_W))), Image.LANCZOS)

CAP_H = 46
SEP = 4
W = PANEL_W + 24 * 2
H = CAP_H + src_panel.size[1] + SEP * 3 + CAP_H + ren_panel.size[1] + 80
sheet = Image.new('L', (W, H), 255)
d = ImageDraw.Draw(sheet)
try:
    f = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 30)
    f2 = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
except Exception:
    f = f2 = ImageFont.load_default()

y = 12
d.text((24, y), "源位图（variantF/media/media/image1.png）按源排印宽 41.1mm 缩放 @600dpi", font=f, fill=0)
y += CAP_H
sheet.paste(src_panel, (24, y))
y += src_panel.size[1]
d.rectangle([24, y + SEP, 24 + PANEL_W, y + SEP + 2], fill=0)
y += SEP * 3
d.text((24, y), "TikZ 重绘（img1_tikz.pdf，自然宽 41.1mm，同尺）@600dpi", font=f, fill=0)
y += CAP_H
sheet.paste(ren_panel, (24, y))
y += ren_panel.size[1]
d.text((24, H - 40), "两幅同尺 41.1mm｜画布 971×1628px（源 691×1159px）｜1px(源)=0.059479mm", font=f2, fill=0)
sheet.save('img1_对照_600dpi.png')
print('img1_对照_600dpi.png', sheet.size)

# --- overlay evidence: red = source only, blue = redraw only, black = both ---
s = np.array(src_panel) < 128
r = np.array(ren_panel.resize((PANEL_W, src_panel.size[1]))) < 128
Hh, Ww = s.shape
img = np.full((Hh, Ww, 3), 255, np.uint8)
img[s & ~r] = (215, 20, 20)
img[r & ~s] = (20, 80, 215)
img[s & r] = (0, 0, 0)
ov = Image.fromarray(img)
ov = ov.resize((Ww // 2, Hh // 2), Image.LANCZOS)
ov.save('img1_叠加_600dpi.png')
inter = (s & r).sum(); uni = (s | r).sum()
print('img1_叠加_600dpi.png', ov.size, ' IoU=%.3f  源墨%dpx 重绘墨%dpx  重合%dpx' % (inter/uni, s.sum(), r.sum(), inter))
