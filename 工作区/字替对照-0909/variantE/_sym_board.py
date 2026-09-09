# -*- coding: utf-8 -*-
# 对照④符号终态板：教材真迹（人教B选必1）vs 我方 Termes Math 栈（symprobe.pdf）
# 逐行 [符号名 | 教材裁片 | 我方裁片]，msyhbd 标签；⌒ 行教材侧记「无实例」
import pymupdf, numpy as np
from PIL import Image, ImageDraw, ImageFont

def render(pdf, pno, clip, zoom):
    doc = pymupdf.open(pdf)
    page = doc[pno - 1]
    pm = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), colorspace=pymupdf.csRGB,
                         clip=pymupdf.Rect(*clip))
    arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3)
    doc.close()
    return Image.fromarray(arr)

def pad(img, target_h):
    w = int(img.width * target_h / img.height)
    return img.resize((w, target_h), Image.LANCZOS)

E = "png-E"
ROOT = "C:/提示词"
TBPDF = ROOT + "/高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf"
FONT = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 22)
FONT_S = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 17)

# ---- 教材侧裁片（bbox 外扩以含上下文箭头/字母） ----
tb = {
    "∠":  render(TBPDF, 15,
                 (213.4 - 14, 622.4 - 6, 225.2 + 46, 647.0 + 6), 7),
    "⊥":  render(TBPDF, 16,
                 (90.5 - 30, 109.8 - 4, 102.4 + 60, 134.4 + 4), 7),
    "∥":  render(TBPDF, 10,
                 (246.9 - 26, 751.3 - 4, 258.7 + 66, 776.0 + 4), 7),
    "→":  render(TBPDF, 10,
                 (76.0 - 8, 438.3 - 6, 86.3 + 46, 459.7 + 10), 7),
}
# ---- 我方侧：symprobe 各条目行（按锚词定位） ----
doc = pymupdf.open("_calib/symprobe.pdf")
page = doc[0]
anchors = [("∠", "夹角"), ("⊥", "垂直"), ("∥", "平行"), ("→", "箭头"), ("⌒", "弧：")]
mine = {}
for name, word in anchors:
    r = page.search_for(word)[0]
    clip = (r.x0 - 4, r.y0 - 5, r.x0 + 300, r.y1 + 5)
    pm = page.get_pixmap(matrix=pymupdf.Matrix(5, 5), colorspace=pymupdf.csRGB, clip=pymupdf.Rect(*clip))
    arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3)
    mine[name] = Image.fromarray(arr)
doc.close()

H = 96
rows = []
for name in ["∠", "⊥", "∥", "→", "⌒"]:
    lab = Image.new("RGB", (150, H), "white")
    d = ImageDraw.Draw(lab)
    d.text((46, 30), name, font=ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 40), fill="black")
    if name == "⌒":
        tcell = Image.new("RGB", (300, H), "white")
        ImageDraw.Draw(tcell).text((12, 34), "教材 190 页无 U+2312 实例", font=FONT_S, fill="black")
    else:
        tcell = pad(tb[name], H)
    mcell = pad(mine[name], H)
    row = Image.new("RGB", (150 + tcell.width + 24 + mcell.width + 24, H), "white")
    row.paste(lab, (0, 0)); row.paste(tcell, (150, 0)); row.paste(mcell, (150 + tcell.width + 24, 0))
    rows.append(row)

W = max(r.width for r in rows) + 40
H2 = sum(r.height for r in rows) + 5 * 46 + 60
board = Image.new("RGB", (W, H2), "white")
d = ImageDraw.Draw(board)
d.text((16, 12), "对照④ 符号终态（左符号｜中＝教材真迹 人教B选必1｜右＝我方 unicode-math＋Termes Math）",
       font=FONT, fill="black")
y = 58
for name, r in zip(["∠", "⊥", "∥", "→", "⌒"], rows):
    d.text((16, y + 2), name, font=FONT_S, fill=(120, 120, 120))
    board.paste(r, (20, y + 30))
    y += r.height + 46
board.save(f"{E}/对照④符号终态.png")
print("已写", f"{E}/对照④符号终态.png", board.size)
