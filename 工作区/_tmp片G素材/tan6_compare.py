# -*- coding: utf-8 -*-
"""探六(tan6)专用：源 vs 重绘 同尺对照裁片 + 差分红框 + 叠加图。600dpi。
（本目录与并行代理共用，故文件名前缀 tan6_ 防撞。）"""
import numpy as np
from PIL import Image, ImageDraw
import fitz, cv2

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image3.png"
PDF = r"C:\提示词\工作区\_tmp片G素材\tikz_tan6.pdf"
OUT = r"C:\提示词\工作区\_tmp片G素材\tikz_tan6_对照.png"
OUT_OV = r"C:\提示词\工作区\_tmp片G素材\tikz_tan6_叠加.png"
DPI = 600
mm2px = DPI / 25.4

doc = fitz.open(PDF); page = doc[0]
pix = page.get_pixmap(matrix=fitz.Matrix(DPI/72, DPI/72), alpha=False)
tikz = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)[:, :, 0]
Ht, Wt = tikz.shape
src0 = np.array(Image.open(SRC).convert("L"))
scale = Wt / src0.shape[1]
src = np.array(Image.open(SRC).convert("L").resize((Wt, round(src0.shape[0]*scale)), Image.LANCZOS))
pad = np.full((Ht, Wt), 255, np.uint8); pad[:src.shape[0], :] = src; src = pad
print("tikz:", tikz.shape, "source:", src.shape, f"scale={scale:.4f}")

ms, mt = src < 165, tikz < 165
k = np.ones((5, 5), np.uint8)
ds = cv2.dilate(ms.astype(np.uint8), k).astype(bool)
dt = cv2.dilate(mt.astype(np.uint8), k).astype(bool)
diff = ((ms & ~dt) | (mt & ~ds)).astype(np.uint8)
diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
n, lab, stats, cent = cv2.connectedComponentsWithStats(diff, 8)
boxes = [tuple(stats[i]) for i in range(1, n) if stats[i][4] >= 60]
boxes.sort(key=lambda b: -b[4])
print(f"diff comps >=60px: {len(boxes)}  total diff px={int(diff.sum())}")
for (x, y, w, h, a) in boxes[:20]:
    print(f"   ({x/mm2px:5.1f},{(Ht-y-h)/mm2px:5.1f})mm  {w/mm2px:.1f}x{h/mm2px:.1f}  area={a}")

gap = 80
qimg = Image.new("L", (Wt, Ht + gap + Ht), 255)
qimg.paste(Image.fromarray(src), (0, 0))
qimg.paste(Image.fromarray(tikz), (0, Ht + gap))
rgb = qimg.convert("RGB")
dr = ImageDraw.Draw(rgb)
for (x, y, w, h, a) in boxes:
    for yo in (0, Ht + gap):
        dr.rectangle([x-8, y+yo-8, x+w+8, y+h+yo+8], outline=(230, 0, 0), width=4)
dr.line([(0, Ht+gap//2), (Wt, Ht+gap//2)], fill=(120, 120, 120), width=3)
# 面板角标（黑块白字，避免与图混）
rgb.save(OUT)
print("saved", OUT, rgb.size)

ov = np.full((Ht, Wt, 3), 255, np.uint8)
ov[:, :, 0] = 255 - (mt*200).astype(np.uint8)
ov[:, :, 1] = 255 - (ms*200).astype(np.uint8)
Image.fromarray(ov).save(OUT_OV)
print("saved", OUT_OV)
