# -*- coding: utf-8 -*-
"""选项修0910：裁片器 v2。用法：python crop.py <src> <out.png> <x0> <y0> <x1> <y1> [maxw] [dpi]，坐标 mm。
png 扫描页按页面物理宽 399.8mm 折算 pt/mm；pdf 直接 mm→pt。"""
import sys
import pymupdf

SRC, OUT = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = [float(v) for v in sys.argv[3:7]]
maxw = float(sys.argv[7]) if len(sys.argv) > 7 else 1400.0
dpi = float(sys.argv[8]) if len(sys.argv) > 8 else 0.0
doc = pymupdf.open(SRC)
page = doc[0]
if SRC.lower().endswith(".pdf"):
    S = 72 / 25.4
else:
    S = page.rect.width / 399.8
clip = pymupdf.Rect(x0 * S, y0 * S, x1 * S, y1 * S)
zoom = (dpi / 72) if dpi else 1406.0 / clip.width  # 默认≈输出宽不超 maxw 由循环收敛
while clip.width * zoom > maxw:
    zoom *= 0.95
pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
print("crop px %dx%d -> %s" % (pix.width, pix.height, OUT))
pix.save(OUT)
