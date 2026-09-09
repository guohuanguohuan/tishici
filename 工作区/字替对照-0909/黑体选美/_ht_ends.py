# -*- coding: utf-8 -*-
"""末端特写 v2：只裁「一」右端 18% 区域，原倍像素展示（不缩放），看微喇叭口。"""
import pymupdf, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

QP = "C:/提示词/高中物理/参考/全品学练考官方样书/选必一/【5563】2025-2026（上）全品学练考 高中物理 选择性必修第一册 RJ 导学案.pdf"
NF = "C:/提示词/工作区/字替对照-0909/variantE/_calib/fonts/"
FB = "C:/提示词/工作区/字替对照-0909/fonts/"
OUT = "C:/提示词/工作区/字替对照-0909/黑体选美/"
EMF = 434.0
labf = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 26)
rows = []

def addrow(label, img):
    h, w = img.shape[:2]
    k = 4
    img = np.asarray(Image.fromarray(img).resize((w * k, h * k), Image.NEAREST))
    h, w = img.shape[:2]
    row = Image.new("RGB", (w + 330, h + 8), "white")
    ImageDraw.Draw(row).text((8, h // 2 - 14), label, font=labf, fill="black")
    row.paste(Image.fromarray(img), (330, 4))
    rows.append(row)

def endcrop(gray, x1_px, frac=0.18, pady=10):
    dark = gray < 128
    ys, xs = np.where(dark)
    x_from = int(xs.max() - (xs.max() - xs.min()) * frac)
    return gray[max(0, ys.min() - pady):ys.max() + pady, max(0, x_from):xs.max() + pady + 4]

doc = pymupdf.open(QP)
page = doc[3]
Z = EMF / 20.67
for b in page.get_text("rawdict")["blocks"]:
    for l in b.get("lines", []):
        for sp in l["spans"]:
            if abs(sp["bbox"][0] - 99.7) < 1 and "ZCHK" in sp["font"]:
                c = sp["chars"][1]
                bx = c["bbox"]
                clip = pymupdf.Rect(bx[0] - 1.5, bx[1] - 1.5, bx[2] + 1.5, bx[3] + 1.5)
                pm = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csRGB, clip=clip)
                img = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3)
                gray = np.asarray(Image.fromarray(img).convert("L"))
                addrow("全品 FZLTZCHK 真迹", endcrop(gray, 0))
doc.close()

def cand_endcrop(label, path, dil=0):
    font = ImageFont.truetype(path, int(EMF))
    im = Image.new("L", (int(EMF) + 100, int(EMF) + 100), 255)
    ImageDraw.Draw(im).text((50, int(EMF * 1.5)), "一", font=font, fill=0, anchor="ls")
    a = np.asarray(im)
    if dil:
        a = np.where(ndimage.binary_dilation(a < 128, iterations=dil), 0, 255).astype(np.uint8)
    addrow(label, endcrop(a, 0))

cand_endcrop("思源 NSC-w650", NF + "NSC-w650.ttf")
cand_endcrop("普惠 Bold", FB + "PuHuiTi__Alibaba-PuHuiTi-Bold.ttf")
cand_endcrop("HarmonyOS Bold", FB + "_npm原始包/npm_fontpkg--harmony-os-sans-sc/package/HarmonyOS_Sans_SC_Bold.ttf")
cand_endcrop("雅黑 Regular+2px（校验）", "C:/Windows/Fonts/msyh.ttc", 2)

W = max(r.width for r in rows) + 346
H2 = sum(r.height for r in rows) + 44
board = Image.new("RGB", (W, H2), "white")
d = ImageDraw.Draw(board)
d.text((8, 6), "末端形态 tie-break v2：章岗「一」右端 18%·原倍像素（上→下：全品/思源/普惠/HarmonyOS/雅黑）", font=labf, fill="black")
y = 40
for r in rows:
    board.paste(r, (8, y)); y += r.height
board.save(OUT + "对照HT-末端特写.png")
print("已写", OUT + "对照HT-末端特写.png", board.size)
