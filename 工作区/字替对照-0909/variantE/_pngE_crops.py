# -*- coding: utf-8 -*-
# png-E 对照⑤裁片组：章节标题带 / 例N行 / ∥行（含≥400%端点特写） / 表格区 / 页脚页码区
# 全品侧＝导学案页图 p04/p05（2977×4176）；我方侧＝png-E/page*.png（150dpi）＋main.pdf 高倍渲染
import pymupdf, numpy as np
from PIL import Image, ImageDraw, ImageFont

E = "png-E"
QP = "C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/"
TBPDF = "C:/提示词/高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf"
F = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 26)
Fs = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 20)

def qp(p, box):
    return Image.open(QP + f"p{p:02d}.png").convert("RGB").crop(box)

def my(p, box):
    return Image.open(f"{E}/page{p}.png").convert("RGB").crop(box)

def render(pdf, pno, clip, zoom):
    doc = pymupdf.open(pdf)
    pm = doc[pno - 1].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), colorspace=pymupdf.csRGB,
                                 clip=pymupdf.Rect(*clip))
    arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3)
    doc.close()
    return Image.fromarray(arr)

def board(fname, title, rows, colw=("全品学练考 p04", "我方 variantE p1")):
    """rows: list of (rowlabel, [img,...])"""
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

# ① 章节标题带（章＋节＋小节＋课时 通栏）
b1_qp = qp(4, (0, 225, 2977, 1030))
b1_my = my(1, (0, 50, 1241, 385))
th = 420
b1_qp = b1_qp.resize((int(b1_qp.width * th / b1_qp.height), th))
b1_my = b1_my.resize((int(b1_my.width * th / b1_my.height), th))
board("对照⑤-1章节标题带.png", "对照⑤-1 章节标题带（左＝全品 p04｜右＝我方 E p1）",
      [("", [b1_qp, b1_my])])

# ② 例N行（◆探究点一＋例1 标签行＋题侧）
b2_qp = qp(5, (1524, 2129, 2925, 2380))
b2_my = my(3, (90, 595, 1090, 705))
th = 150
b2_qp = b2_qp.resize((int(b2_qp.width * th / b2_qp.height), th))
b2_my = b2_my.resize((int(b2_my.width * th / b2_my.height), th))
board("对照⑤-2例N行.png", "对照⑤-2 例N 圆黑标签行（上＝全品 p05 例1｜下＝我方 E p3 例1）",
      [("全品 p05", [b2_qp]), ("我方 E p3", [b2_my])])

# ③ ∥行＋端点特写（≥400%）
r3_qp = qp(4, (230, 3550, 1510, 3855))                 # 全品 表格「记作 a∥b」行
tb_row = render(TBPDF, 10, (225, 738, 345, 786), 6)    # 教材 p10 ∥ 行上下文
r3_my = my(1, (640, 848, 1135, 912))                   # 我方 表格 ∥ 行
TH = 210
cells3 = [im.resize((int(im.width * TH / im.height), TH)) for im in (r3_qp, tb_row, r3_my)]

# —— 端点特写：三侧各自定位 ∥ 墨迹 → 裁紧 → 同高并排 ——
from scipy import ndimage

def locate_qp():
    """全品 p04：行裁片内按形状拣 ∥ 两笔（同高配对），回全局像素框"""
    OX, OY = 230, 3550
    im = np.asarray(qp(4, (OX, OY, OX + 1280, OY + 305)).convert("L"))
    lab, n = ndimage.label(im < 128)
    strokes = []
    for i in range(1, n + 1):
        m = lab == i
        ys, xs = np.where(m)
        h = ys.max() - ys.min() + 1
        if h < 30:
            continue
        rows = {r: np.average(np.flatnonzero(m[r])) for r in range(ys.min(), ys.max() + 1) if m[r].any()}
        rr = np.array(sorted(rows))
        k, _ = np.polyfit(rr, np.array([rows[r] for r in rr]), 1)
        if -0.62 < k < -0.38 and (xs.max() - xs.min()) < 0.6 * h:
            strokes.append([xs.min(), ys.min(), xs.max(), ys.max()])
    assert strokes, "全品 ∥ 未定位"
    pair = None
    for i in range(len(strokes)):
        for j in range(i + 1, len(strokes)):
            a, b = strokes[i], strokes[j]
            ov = min(a[3], b[3]) - max(a[1], b[1])
            if ov > 0.8 * min(a[3] - a[1], b[3] - b[1]):
                pair = (a, b)
    assert pair, f"全品 ∥ 配对失败：{strokes}"
    (a, b) = pair
    return (OX + min(a[0], b[0]) - 6, OY + min(a[1], b[1]) - 6,
            OX + max(a[2], b[2]) + 7, OY + max(a[3], b[3]) + 7)

def locate_tb():
    """教材 p10：宽 clip 渲染后按形状拣 ∥，回 PIL 裁片"""
    Z = 16
    pm = render(TBPDF, 10, (235, 738, 285, 790), Z)
    im = np.asarray(pm.convert("L"))
    lab, n = ndimage.label(im < 128)
    hits = []
    for i in range(1, n + 1):
        m = lab == i
        ys, xs = np.where(m)
        h = ys.max() - ys.min() + 1
        if h < 40:
            continue
        rows = {r: np.average(np.flatnonzero(m[r])) for r in range(ys.min(), ys.max() + 1) if m[r].any()}
        rr = np.array(sorted(rows))
        k, _ = np.polyfit(rr, np.array([rows[r] for r in rr]), 1)
        if -0.62 < k < -0.38 and 0.3 < (xs.max() - xs.min()) / h < 0.75:
            hits.append((xs.min(), ys.min(), xs.max(), ys.max()))
    assert hits, "教材 ∥ 未定位"
    x0 = min(h[0] for h in hits) - 10; y0 = min(h[1] for h in hits) - 8
    x1 = max(h[2] for h in hits) + 12; y1 = max(h[3] for h in hits) + 10
    return pm.crop((x0, y0, x1, y1))

# 我方：drawings 精确定位（页1 表格 ∥），±2.2pt 紧裁
doc = pymupdf.open("main.pdf")
rects = []
for dr in doc[0].get_drawings():
    r = dr["rect"]
    if dr["type"] == "f" and 8 < r.height < 13 and 0.50 <= r.width / r.height <= 0.56 and r.x0 > 280:
        rects.append(r)
doc.close()
rects.sort(key=lambda r: r.x0)
u = rects[0] | rects[1]
r3_my16 = render("main.pdf", 1, (u.x0 - 2.2, u.y0 - 2.0, u.x1 + 2.2, u.y1 + 2.0), 16)
tb16 = locate_tb()
qp16 = qp(4, locate_qp())
s = r3_my16.height
qp16u = qp16.resize((max(1, int(qp16.width * s / qp16.height)), s), Image.LANCZOS)
tb16u = tb16.resize((max(1, int(tb16.width * s / tb16.height)), s), Image.LANCZOS)
board("对照⑤-3平行号行.png", "对照⑤-3 ∥行（上排）与端点特写（下排 ≥400%：同高对齐）",
      [("全品 p04 表格行｜教材 p10｜我方 E p1 表格行", cells3),
       ("全品 ∥ 特写（254dpi 原图素放大）", [qp16u]),
       ("教材 ∥ 特写（zoom16＝1152dpi）", [tb16u]),
       ("我方 ∥ 特写（zoom16＝1152dpi）", [r3_my16])])

# ④ 表格区（表头＋零向量/单位向量/相等向量 行）
b4_qp = qp(4, (225, 2310, 1530, 3470))
b4_my = my(1, (640, 590, 1135, 1020))
th = 560
b4_qp = b4_qp.resize((int(b4_qp.width * th / b4_qp.height), th))
b4_my = b4_my.resize((int(b4_my.width * th / b4_my.height), th))
board("对照⑤-4表格区.png", "对照⑤-4 表格区（左＝全品 p04｜右＝我方 E p1）",
      [("", [b4_qp, b4_my])])

# ⑤ 页脚页码区（底部通栏）
b5_qp = qp(4, (1900, 3900, 2977, 4010))
b5_my = my(1, (600, 1630, 1241, 1700))
th = 160
b5_qp = b5_qp.resize((int(b5_qp.width * th / b5_qp.height), th), Image.LANCZOS)
b5_my = b5_my.resize((int(b5_my.width * th / b5_my.height), th), Image.LANCZOS)
board("对照⑤-5页脚页码区.png", "对照⑤-5 页脚页码区（上＝全品 p04 底右｜下＝我方 E p1 底右；同高 160px）",
      [("全品 p04", [b5_qp]), ("我方 E p1", [b5_my])])
