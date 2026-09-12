# -*- coding: utf-8 -*-
"""拓-020 图回源落位：精确裁框＋白底清理＋白底版落 拓展册/上册/figs/t020_0.png。
登记口径：源位图回提（人教B选必1 printed p28 第9题图，矢量转 400dpi 位图）＋
底色白化清理（教材页装饰底框→白，笔画/标号原样，非改绘）。"""
import pymupdf, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
OUT = "工作区/M2-第1章量产0911/_tmp装配图债014"
FIGS = "工作区/M2-第1章量产0911/成卷/拓展册/上册/figs"
doc = pymupdf.open("高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf")
page = doc[34]
box = pymupdf.Rect(419, 633.5, 518, 744.5)
pix = page.get_pixmap(dpi=400, clip=box)  # RGB
w, h, n = pix.width, pix.height, pix.n
samples = pix.samples
assert n == 3, pix.n
TH = 170  # 白化阈：三通道全>TH → 白（笔画黑、灰阶浅标号保留）
buf = bytearray(samples)
cnt = 0
for i in range(0, len(buf), 3):
    r, g, b = buf[i], buf[i + 1], buf[i + 2]
    if r > TH and g > TH and b > TH:
        buf[i] = buf[i + 1] = buf[i + 2] = 255
        cnt += 1
pix2 = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, w, h), False)
pix2.set_rect(pix2.irect, (255, 255, 255)) if False else None
# 直接重建
import struct, zlib
def write_png(path, w, h, rgb):
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + rgb[y * w * 3:(y + 1) * w * 3] for y in range(h))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    open(path, "wb").write(png)
p_flat = os.path.join(OUT, "b9_白底.png")
write_png(p_flat, w, h, bytes(buf))
print("saved", p_flat, w, "x", h, "whitened px:", cnt, "/", w * h)
os.makedirs(FIGS, exist_ok=True)
import shutil
dst = os.path.join(FIGS, "t020_0.png")
shutil.copyfile(p_flat, dst)
print("落位 ->", dst)
