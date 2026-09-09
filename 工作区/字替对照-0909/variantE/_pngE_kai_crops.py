# -*- coding: utf-8 -*-
# 对照⑥ 楷体/仿宋换挂裁片（0909 补欠验证）：
#   全品侧＝导学案页图 p04（全品真身内嵌 FZKTK/FZFSK）；我方侧＝替换后 variantE main.pdf 高倍重渲（FZKTK.TTF/FZFSK.TTF）
#   行1 楷体·【学习目标】条目；行2 仿宋·【诊断分析】说明行。并排放大（全品 2977px 宽页、我方 zoom 4）
import pymupdf
from PIL import Image, ImageDraw, ImageFont

E = "png-E"
QP = "C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/"
F = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 26)
Fs = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 20)

def qp(box):
    return Image.open(QP + "p04.png").convert("RGB").crop(box)

def my(pno, box_px150, zoom=4):
    """我方页 box 以 150dpi png 像素给值，PDF 按 zoom 重渲（保锐度）"""
    pt = [v * 72.0 / 150 for v in box_px150]
    doc = pymupdf.open("main.pdf")
    pm = doc[pno - 1].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), colorspace=pymupdf.csRGB,
                                 clip=pymupdf.Rect(*pt))
    doc.close()
    return Image.frombytes("RGB", (pm.width, pm.height), pm.samples)

def board(fname, title, rows):
    pad, hh = 24, 44
    W = max(sum(im.width for im in imgs) + pad * (len(imgs) + 1) for _, imgs in rows) + 8
    H = hh + sum(imgs[0].height + 58 for _, imgs in rows) + 12
    b = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(b)
    d.text((16, 10), title, font=F, fill="black")
    y = hh
    for rl, imgs in rows:
        x = pad
        for im in imgs:
            b.paste(im, (x, y))
            x += im.width + pad
        d.text((16, y + imgs[0].height + 6), rl, font=Fs, fill=(90, 90, 90))
        y += imgs[0].height + 58
    b.save(f"{E}/{fname}")
    print("已写", fname, b.size)

TH = 190
r1_qp = qp((230, 1015, 2900, 1430))            # 全品【学习目标】标签＋楷体条目 1./2.
r1_my = my(1, (95, 400, 1160, 600))            # 我方同位（页1 顶部通栏）
r1_qp = r1_qp.resize((int(r1_qp.width * TH / r1_qp.height), TH))
r1_my = r1_my.resize((int(r1_my.width * TH / r1_my.height), TH))

TH2 = 110
r2_qp = qp((1490, 1415, 2800, 1515))           # 全品【诊断分析】说明行（仿宋 FZFSK 同位）
r2_my = my(1, (625, 1065, 1241, 1140))         # 我方 \zhenhead 说明行（页1 右栏）
r2_qp = r2_qp.resize((int(r2_qp.width * TH2 / r2_qp.height), TH2))
r2_my = r2_my.resize((int(r2_my.width * TH2 / r2_my.height), TH2))

board("对照⑥楷体对照裁片-换挂FZKTK-FZFSK.png",
      "对照⑥ 楷体/仿宋换挂对照（左＝全品 p04 真身｜右＝我方 E 换挂 FZKTK.TTF/FZFSK.TTF，放大）",
      [("行1 楷体·【学习目标】条目：全品 p04（内嵌 FZKTK）", [r1_qp, r1_my]),
       ("行2 仿宋·【诊断分析】说明行：全品 p04（内嵌 FZFSK）", [r2_qp, r2_my])])
