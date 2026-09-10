# -*- coding: utf-8 -*-
"""出对照裁片：①上源下绘（同尺 835dpi）②叠影 ③局部 2× 放大。"""
import numpy as np, pymupdf, os
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

SG = r"C:\提示词\工作区\_tmp片G素材"
SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image5.png"
PDF = SG + r"\fig-image5-fold.pdf"
S = 54.7 / 1798.0
ZOOM = (1 / S) * 25.4 / 72.0

# ---- 源图 -> 灰度（RGB 全 0，墨在 alpha；白底合成 => gray = 255 - alpha）----
a = np.array(Image.open(SRC))[:, :, 3]
src_gray = (255 - a).astype(np.uint8)
src_ink = a > 128

# ---- 重绘光栅 ----
page = pymupdf.open(PDF)[0]
pix = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM), alpha=False)
red_gray = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, 0]
red_ink = red_gray < 128


def net_vertices(mask):
    lab, _ = ndimage.label(mask, structure=np.ones((3, 3)))
    sz = np.bincount(lab.ravel()); sz[0] = 0
    net = lab == sz.argmax()
    ys, xs = np.where(net)
    return np.array([xs.min(), ys.min()]), np.array([xs.max(), ys.max()])


def fit_lines(mask, vr):
    def prof(p, q, t, half=9):
        p = np.array(p, float); q = np.array(q, float)
        d = q - p; L = np.hypot(*d); u = d / L; nv = np.array([-u[1], u[0]])
        pt = p + u * t
        offs = np.arange(-half, half + .001, .25)
        v = []
        for o in offs:
            x, y = pt + nv * o
            xi, yi = int(round(x)), int(round(y))
            v.append(mask[yi, xi] if 0 <= xi < mask.shape[1] and 0 <= yi < mask.shape[0] else False)
        v = np.array(v, float)
        return None if v.sum() < 3 else (offs * v).sum() / v.sum()

    def fit(p, q, trim=14, step=3):
        p = np.array(p, float); q = np.array(q, float)
        L = np.hypot(*(q - p)); u = (q - p) / L; nv = np.array([-u[1], u[0]])
        pts = []
        for t in np.arange(trim, L - trim, step):
            c = prof(p, q, t)
            if c is not None:
                pts.append(p + u * t + nv * c)
        pts = np.array(pts); m = pts.mean(0)
        _, _, vv = np.linalg.svd(pts - m)
        dv = vv[0]
        return m, (dv if dv @ u > 0 else -dv)

    E = {'AB': ('A', 'B'), 'BC': ('B', 'C'), 'CD': ('C', 'D'), 'DA': ('D', 'A')}
    LN = {k: fit(vr[i], vr[j]) for k, (i, j) in E.items()}

    def ix(l1, l2):
        (m1, d1), (m2, d2) = l1, l2
        t = np.linalg.solve(np.array([d1, -d2]).T, m2 - m1)
        return m1 + d1 * t[0]
    return {'A': ix(LN['AB'], LN['DA']), 'B': ix(LN['AB'], LN['BC']),
            'C': ix(LN['BC'], LN['CD']), 'D': ix(LN['CD'], LN['DA'])}


SRCV = {'A': (130.33, 737.79), 'B': (647.41, 174.46), 'C': (1658.04, 738.19), 'D': (1246.83, 1145.02)}
VS = fit_lines(src_ink, SRCV)
(nx0, ny0), (nx1, ny1) = net_vertices(src_ink)
(nn0, nny0), (nn1, nny1) = net_vertices(red_ink)
# 重绘粗播种：源图顶点按「实线网 bbox → 重绘实线网 bbox」线性映射
Vr0 = {k: (nn0 + (v[0] - nx0) * (nn1 - nn0) / (nx1 - nx0),
           nny0 + (v[1] - ny0) * (nny1 - nny0) / (ny1 - ny0)) for k, v in SRCV.items()}
Vr = fit_lines(red_ink, Vr0)
Vs = VS
TV = np.mean([Vs[k] for k in 'ABCD'], axis=0) - np.mean([Vr[k] for k in 'ABCD'], axis=0)
print("顶点重心对齐偏移 Tx,Ty = %.2f, %.2f px" % tuple(TV))
for k in 'ABCD':
    d = Vs[k] - (Vr[k] + TV)
    print(f"  对齐后残差 {k}: ({d[0]:+.2f},{d[1]:+.2f})px = ({d[0]*S:+.3f},{d[1]*S:+.3f})mm")

TX, TY = int(round(TV[0])), int(round(TV[1]))
SH, SW = src_gray.shape
RH, RW = red_gray.shape

# ---------- ① 上源下绘 ----------
M = 14; GAP = 46
W = max(SW, RW + TX) + 2 * M
Hh = M + SH + GAP + RH + M
sheet = Image.new("L", (W, Hh), 255)
sheet.paste(Image.fromarray(src_gray), (M, M))
sheet.paste(Image.fromarray(red_gray), (M + TX, M + SH + GAP + TY))
d = ImageDraw.Draw(sheet)
d.line([(0, M + SH + GAP // 2), (W, M + SH + GAP // 2)], fill=190, width=2)
try:
    f = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 26)
except Exception:
    f = ImageFont.load_default()
d.text((M + 4, M - 1), "源图 image5.png（54.7mm 排印宽 → 835dpi 同尺）", fill=120, font=f)
d.text((M + TX + 4, M + SH + GAP + TY - 1), "重绘 TikZ（同宽同尺，顶点重心对齐）", fill=120, font=f)
sheet.save(SG + r"\对照-image5-上源下绘835dpi.png")
print("① ->", SG + r"\对照-image5-上源下绘835dpi.png", sheet.size)

# ---------- ② 叠影（红＝源图独有，蓝＝重绘独有，黑＝重合） ----------
ov = np.full((Hh, W, 3), 255, np.uint8)
ys, xs = np.where(src_ink)
ov[ys + M, xs + M] = [255, 0, 0]
ys, xs = np.where(red_ink)
ov[ys + M + TY, xs + M + TX] = [0, 0, 255]
ys, xs = np.where(src_ink)
ov[ys + M, xs + M] = [255, 0, 0]
both = np.zeros((Hh, W), bool)
sy, sx = np.where(src_ink); both[sy + M, sx + M] = True
ry, rx = np.where(red_ink)
both[ry + M + TY, rx + M + TX] &= True
ov[both] = [0, 0, 0]
img = Image.fromarray(ov)
d = ImageDraw.Draw(img)
d.text((M + 4, M - 1), "叠影：红=仅源图 / 蓝=仅重绘 / 黑=重合", fill=(0, 0, 0), font=f)
img.save(SG + r"\对照-image5-叠影.png")
print("② ->", SG + r"\对照-image5-叠影.png", img.size)

# ---------- ③ 局部 2×（M/N 垂足区） ----------
BOX = (400, 540, 1420, 1250)     # 源图坐标系
x0, y0, x1, y1 = BOX
cs = Image.fromarray(src_gray[y0:y1, x0:x1]).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.LANCZOS)
cr = Image.fromarray(red_gray[y0 - TY:y1 - TY, x0 - TX:x1 - TX]).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.LANCZOS)
w2, h2 = cs.size
sh2 = Image.new("L", (w2 + 2 * M, M + h2 + GAP + h2 + M), 255)
sh2.paste(cs, (M, M)); sh2.paste(cr, (M, M + h2 + GAP))
d = ImageDraw.Draw(sh2)
d.line([(0, M + h2 + GAP // 2), (w2 + 2 * M, M + h2 + GAP // 2)], fill=190, width=2)
d.text((M + 4, M - 1), "源图局部 ×2（M、N 垂足与虚线）", fill=120, font=f)
d.text((M + 4, M + h2 + GAP - 1), "重绘局部 ×2（同尺）", fill=120, font=f)
sh2.save(SG + r"\对照-image5-局部2x.png")
print("③ ->", SG + r"\对照-image5-局部2x.png", sh2.size)
