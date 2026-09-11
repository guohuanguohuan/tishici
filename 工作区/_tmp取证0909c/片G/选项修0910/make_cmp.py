# -*- coding: utf-8 -*-
"""选项修0910：Q2 选项行 vs 扫描页 2 项行 并排对照拼图（同 6px/mm 比例）。"""
from PIL import Image, ImageDraw, ImageFont
import pymupdf

PXMM = 6.0
SCAN_PXMM = 14.062
LBLH = 40

def grab_pdf(pdf, pno, x0, y0, x1, y1):
    doc = pymupdf.open(pdf)
    clip = pymupdf.Rect(x0 * 72 / 25.4, y0 * 72 / 25.4, x1 * 72 / 25.4, y1 * 72 / 25.4)
    pix = doc[pno].get_pixmap(matrix=pymupdf.Matrix(PXMM * 25.4 / 72, PXMM * 25.4 / 72), clip=clip)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

def grab_scan(png, x0, y0, x1, y1):
    im = Image.open(png).convert("RGB").crop(
        (int(x0 * SCAN_PXMM), int(y0 * SCAN_PXMM), int(x1 * SCAN_PXMM), int(y1 * SCAN_PXMM)))
    w = int(im.width * PXMM / SCAN_PXMM)
    h = int(im.height * PXMM / SCAN_PXMM)
    return im.resize((w, h), Image.LANCZOS)

top = grab_pdf(r"C:/提示词/工作区/字替对照-0909/靠齐样张-0910/测评卷/main.pdf",
               0, 139.9, 14.5, 261.0, 30.5)
bot = grab_scan(r"C:/提示词/工作区/全品结构提取/数学选必一/测评卷页图/p01.png",
                8.9, 73.5, 130.0, 94.5)
W = max(top.width, bot.width)
canvas = Image.new("RGB", (W + 20, top.height + bot.height + 2 * LBLH + 40), "white")
d = ImageDraw.Draw(canvas)
try:
    font = ImageFont.truetype(r"C:/Windows/Fonts/msyh.ttc", 26)
except OSError:
    font = ImageFont.load_default()
d.text((10, 8), "上＝样张（修后）Q2 两项行：A|B、C|D 定宽槽 57.1mm 列对齐", fill="navy", font=font)
canvas.paste(top, (10, LBLH))
y2 = LBLH + top.height + 10
d.line([(0, y2), (W, y2)], fill="red", width=3)
d.text((10, y2 + 6), "下＝扫描页 p01 Q1 两项行（原件网格）：B/D 同列 67.7mm＝槽距≈53.0mm（短选项后同样留白）", fill="green", font=font)
canvas.paste(bot, (10, y2 + LBLH + 14))
out = r"C:/提示词/工作区/_tmp取证0909c/片G/选项修0910/目验-Q2选项对扫描页.png"
canvas.save(out)
print("saved", out, canvas.size)
