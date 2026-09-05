# -*- coding: utf-8 -*-
# 临时脚本：成书路线③图片重绘一期（用完即删）
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, Polygon
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
DPI = 300
FS = 9.0          # 主体字符≈9pt（[9,12]带域精调）
LW = 0.9
GRAY_FILL = "#D9D9D9"
GRAY_FILL2 = "#BFBFBF"

plt.rcParams["mathtext.fontset"] = "stix"


def newfig(w_cm, h_cm):
    fig = plt.figure(figsize=(w_cm / 2.54, h_cm / 2.54), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    return fig, ax


def arrow(ax, x0, y0, x1, y1, lw=LW, color="k", ms=7):
    ax.add_patch(FancyArrow(x0, y0, x1 - x0, y1 - y0, width=0.0,
                            head_width=0.16, head_length=0.22,
                            length_includes_head=True, lw=lw, color=color))


def axes_xy(ax, xlim, ylim, ox, oy, xlabel="$x$", ylabel="$y$", olab="$O$",
            loff=(-0.28, -0.30)):
    arrow(ax, xlim[0], oy, xlim[1], oy)
    arrow(ax, ox, ylim[0], ox, ylim[1])
    ax.text(xlim[1] - 0.02, oy - 0.30, xlabel, fontsize=FS, ha="right", va="top")
    ax.text(ox + 0.14, ylim[1] - 0.02, ylabel, fontsize=FS, ha="left", va="top")
    ax.text(ox + loff[0], oy + loff[1], olab, fontsize=FS, ha="right", va="top")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, facecolor="white")
    plt.close(fig)
    print("wrote", name)


# ---------------- I2 差图 ----------------
def fig_line_p0p():  # image3 点斜式
    fig, ax = newfig(3.6, 2.9)
    ax.set_xlim(-0.6, 5.2); ax.set_ylim(-0.6, 4.0)
    axes_xy(ax, (-0.4, 5.0), (-0.4, 3.8), 0.0, 0.0)
    x = np.array([1.0, 4.4]); y = 0.75 * (x - 1.0) + 0.7
    ax.plot(x, y, color="k", lw=LW)
    ax.text(4.5, 0.75 * 3.5 + 0.7 + 0.15, "$l$", fontsize=FS)
    ax.plot([2.2], [0.75 * 1.2 + 0.7], "o", ms=2.6, color="k")
    ax.plot([3.4], [0.75 * 2.4 + 0.7], "o", ms=2.6, color="k")
    ax.text(2.25, 0.75 * 1.2 + 0.7 - 0.42, "$P_0$", fontsize=FS)
    ax.text(3.45, 0.75 * 2.4 + 0.7 - 0.42, "$P$", fontsize=FS)
    save(fig, "I2_image3.png")


def fig_line_b():  # image4 斜截式
    fig, ax = newfig(3.0, 2.8)
    ax.set_xlim(-1.6, 3.4); ax.set_ylim(-1.2, 3.0)
    axes_xy(ax, (-1.4, 3.2), (-1.0, 2.8), 0.0, 0.0)
    x = np.array([-1.0, 2.4]); y = -0.85 * x + 1.6
    ax.plot(x, y, color="k", lw=LW)
    ax.text(0.12, 1.62, "$b$", fontsize=FS)
    save(fig, "I2_image4.png")


def fig_line_p1p2():  # image5 两点式
    fig, ax = newfig(2.8, 2.4)
    ax.set_xlim(-1.6, 3.4); ax.set_ylim(-1.4, 2.4)
    axes_xy(ax, (-1.4, 3.2), (-1.2, 2.2), 0.0, 0.0)
    x = np.array([-1.1, 3.0]); y = -0.55 * x + 0.85
    ax.plot(x, y, color="k", lw=LW)
    ax.plot([0.35], [-0.55 * 0.35 + 0.85], "o", ms=2.6, color="k")
    ax.plot([2.2], [-0.55 * 2.2 + 0.85], "o", ms=2.6, color="k")
    ax.text(0.48, -0.55 * 0.35 + 0.85 + 0.10, "$P_1$", fontsize=FS)
    ax.text(2.10, -1.00, "$P_2$", fontsize=FS)
    save(fig, "I2_image5.png")


def fig_line_intercept():  # image6 截距式
    fig, ax = newfig(3.2, 3.0)
    ax.set_xlim(-1.6, 3.6); ax.set_ylim(-1.4, 3.0)
    axes_xy(ax, (-1.4, 3.4), (-1.2, 2.8), 0.0, 0.0)
    x = np.array([-1.1, 3.1]); y = -0.8 * x + 1.7
    ax.plot(x, y, color="k", lw=LW)
    ax.text(0.14, 1.78, "$(0,b)$", fontsize=FS)
    ax.text(2.125, 0.16, "$(a,0)$", fontsize=FS)
    save(fig, "I2_image6.png")


def fig_hyperbola():  # imageW2044 双曲线定义
    fig, ax = newfig(4.6, 4.6)
    ax.set_xlim(-4.4, 4.4); ax.set_ylim(-3.6, 3.6)
    axes_xy(ax, (-4.2, 4.2), (-3.4, 3.4), 0.0, 0.0)
    a, b = 1.2, 1.6
    t = np.linspace(-1.5, 1.5, 200)
    xr = a * np.cosh(t); yr = b * np.sinh(t)
    ax.plot(xr, yr, color="k", lw=LW)
    ax.plot(-xr, yr, color="k", lw=LW)
    c = np.hypot(a, b)
    ax.plot([-c], [0], "o", ms=2.6, color="k")
    ax.plot([c], [0], "o", ms=2.6, color="k")
    ax.text(-c - 0.10, -0.50, "$F_1$", fontsize=FS, ha="right")
    ax.text(c + 0.02, -0.50, "$F_2$", fontsize=FS)
    px, py = a * np.cosh(0.9), b * np.sinh(0.9)
    ax.plot([px], [py], "o", ms=2.6, color="k")
    ax.text(px + 0.12, py + 0.10, "$P$", fontsize=FS)
    ax.plot([-c, px], [0, py], color="k", lw=LW * 0.8)
    ax.plot([c, px], [0, py], color="k", lw=LW * 0.8)
    save(fig, "I2_imageW2044.png")


def _parab_right(ax, mirror_x=False, mirror_y=False):
    t = np.linspace(-2.2, 2.2, 200)
    x = 0.45 * t ** 2
    y = t
    if mirror_x:
        x = -x
    if mirror_y:
        y = -y
    return x, y


def fig_parab(open_dir, name, w=3.4, h=4.0):
    # open_dir: 'right','left','up','down'
    fig, ax = newfig(w, h)
    ax.set_xlim(-3.2, 3.2); ax.set_ylim(-3.2, 3.2)
    axes_xy(ax, (-3.0, 3.0), (-3.0, 3.0), 0.0, 0.0)
    t = np.linspace(-2.3, 2.3, 200)
    if open_dir == "right":
        px, py = 0.42 * t ** 2, t
        F = (0.7, 0); lpos = "v"; lcoord = -0.7
        P = (0.42 * 1.5 ** 2, 1.5)
    elif open_dir == "left":
        px, py = -0.42 * t ** 2, t
        F = (-0.7, 0); lpos = "v"; lcoord = 0.7
        P = (-0.42 * 1.5 ** 2, 1.5)
    elif open_dir == "up":
        px, py = t, 0.42 * t ** 2
        F = (0, 0.7); lpos = "h"; lcoord = -0.7
        P = (1.5, 0.42 * 1.5 ** 2)
    else:
        px, py = t, -0.42 * t ** 2
        F = (0, -0.7); lpos = "h"; lcoord = 0.7
        P = (1.5, -0.42 * 1.5 ** 2)
    ax.plot(px, py, color="k", lw=LW)
    if lpos == "v":
        ax.plot([lcoord, lcoord], [-2.6, 2.6], color="k", lw=LW)
        ax.text(lcoord - 0.10 if open_dir == "right" else lcoord + 0.10,
                2.55, "$l$", fontsize=FS,
                ha="right" if open_dir == "right" else "left")
    else:
        ax.plot([-2.6, 2.6], [lcoord, lcoord], color="k", lw=LW)
        ax.text(-2.55, lcoord - 0.12 if open_dir == "up" else lcoord + 0.12,
                "$l$", fontsize=FS,
                va="top" if open_dir == "up" else "bottom")
    ax.plot([F[0]], [F[1]], "o", ms=2.6, color="k")
    if open_dir == "right":
        ax.text(F[0] + 0.05, F[1] - 0.45, "$F$", fontsize=FS)
    elif open_dir == "left":
        ax.text(F[0] - 0.25, F[1] - 0.55, "$F$", fontsize=FS)
    elif open_dir == "up":
        ax.text(F[0] - 0.42, F[1] + 0.05, "$F$", fontsize=FS)
    else:
        ax.text(F[0] - 0.52, F[1] - 0.40, "$F$", fontsize=FS)
    ax.plot([P[0]], [P[1]], "o", ms=2.6, color="k")
    ax.text(P[0] + 0.12, P[1] + 0.10, "$P$", fontsize=FS)
    ax.plot([P[0], F[0]], [P[1], F[1]], color="k", lw=LW * 0.8)
    if lpos == "v":
        ax.plot([P[0], lcoord], [P[1], P[1]], color="k", lw=LW * 0.8)
    else:
        ax.plot([P[0], P[0]], [P[1], lcoord], color="k", lw=LW * 0.8)
    save(fig, name)


def fig_focal_chord():  # imageW2060 焦点弦
    fig, ax = newfig(3.6, 4.4)
    ax.set_xlim(-1.4, 4.0); ax.set_ylim(-3.2, 3.2)
    axes_xy(ax, (-1.2, 3.8), (-3.0, 3.0), 0.0, 0.0)
    t = np.linspace(-2.5, 2.5, 200)
    ax.plot(0.42 * t ** 2, t, color="k", lw=LW)
    A = (0.42 * 2.0 ** 2, 2.0)
    B = (0.42 * (-2.0) ** 2, -2.0)
    ax.plot([A[0]], [A[1]], "o", ms=2.6, color="k")
    ax.plot([B[0]], [B[1]], "o", ms=2.6, color="k")
    ax.text(A[0] + 0.05, A[1] + 0.12, "$A$", fontsize=FS)
    ax.text(B[0] + 0.05, B[1] - 0.40, "$B$", fontsize=FS)
    ax.plot([A[0], B[0]], [A[1], B[1]], color="k", lw=LW)
    G = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    ax.plot([G[0]], [G[1]], "o", ms=2.2, color="k")
    ax.text(G[0] + 0.14, G[1] - 0.05, "$G$", fontsize=FS)
    save(fig, "I2_imageW2060.png")


# ---------------- 异质图 ----------------
def fig_tetra_vectors():  # I1 image17 手绘四面体向量
    fig, ax = newfig(4.6, 4.2)
    ax.set_xlim(-0.5, 6.0); ax.set_ylim(-0.5, 5.0)
    O = np.array([0.6, 2.2]); A = np.array([2.6, 0.4])
    B = np.array([5.2, 2.0]); C = np.array([3.2, 4.4])
    for P, Q in [(O, A), (O, B), (O, C), (A, B), (B, C), (C, A)]:
        ax.plot([P[0], Q[0]], [P[1], Q[1]], color="k", lw=LW)
    arrow(ax, *O, *A); arrow(ax, *O, *B); arrow(ax, *O, C[0], C[1])
    ax.text(0.15, 2.30, "$O$", fontsize=FS)
    ax.text(2.55, 0.05, "$A$", fontsize=FS)
    ax.text(5.30, 1.95, "$B$", fontsize=FS)
    ax.text(3.25, 4.50, "$C$", fontsize=FS)
    ax.text(1.35, 1.05, "$\\vec{a}$", fontsize=FS)
    ax.text(4.10, 1.85, "$\\vec{b}$", fontsize=FS)
    ax.text(1.45, 3.50, "$\\vec{c}$", fontsize=FS)
    ax.text(4.00, 0.85, "$\\vec{b}-\\vec{a}$", fontsize=FS)
    ax.text(4.45, 3.35, "$\\vec{c}-\\vec{b}$", fontsize=FS)
    ax.text(2.80, 2.70, "$\\vec{c}-\\vec{a}$", fontsize=FS)
    save(fig, "I1_image17.png")


def fig_tetra_height(out_name="I1_image18.png"):  # I1 image18 / B sub3_B_17 四面体高
    fig, ax = newfig(4.4, 4.4)
    ax.set_xlim(-0.5, 6.0); ax.set_ylim(-0.5, 5.4)
    O = np.array([0.6, 1.8]); A = np.array([2.4, 0.3]); B = np.array([5.0, 1.6])
    C = np.array([3.0, 4.8])
    H = np.array([3.0, 1.35])
    ax.plot([O[0], A[0]], [O[1], A[1]], color="k", lw=LW)
    ax.plot([O[0], B[0]], [O[1], B[1]], color="k", lw=LW)
    ax.plot([A[0], B[0]], [A[1], B[1]], color="k", lw=LW)
    ax.plot([O[0], C[0]], [O[1], C[1]], color="k", lw=LW)
    ax.plot([A[0], C[0]], [A[1], C[1]], color="k", lw=LW)
    ax.plot([B[0], C[0]], [B[1], C[1]], color="k", lw=LW)
    ax.plot([C[0], H[0]], [C[1], H[1]], color="k", lw=LW * 0.8, ls="--")
    ax.plot([O[0], H[0]], [O[1], H[1]], color="k", lw=LW * 0.8, ls="--")
    ax.text(0.15, 1.85, "$O$", fontsize=FS)
    ax.text(2.35, -0.05, "$A$", fontsize=FS)
    ax.text(5.10, 1.55, "$B$", fontsize=FS)
    ax.text(3.05, 4.90, "$C$", fontsize=FS)
    ax.text(3.12, 1.20, "$H$", fontsize=FS)
    ax.text(1.20, 0.85, "$a$", fontsize=FS)
    ax.text(4.00, 1.45, "$b$", fontsize=FS)
    ax.text(1.55, 3.4, "$c$", fontsize=FS)
    ax.text(3.12, 3.1, "$h$", fontsize=FS)
    ax.text(1.05, 2.15, "$\\beta$", fontsize=FS)
    save(fig, out_name)


def fig_dihedral(seed, name, n1dir, n2dir):
    fig, ax = newfig(5.2, 4.4)
    ax.set_xlim(-1.0, 8.0); ax.set_ylim(-0.8, 5.8)
    A = np.array([2.4, 1.4]); B = np.array([4.4, 1.4])
    u = np.array([-0.5, 2.8])   # plane1 direction (up-left)
    v = np.array([2.5, 1.0])    # plane2 direction (up-right)
    ax.add_patch(Polygon([A, B, B + u, A + u], closed=True,
                         facecolor=GRAY_FILL, edgecolor="k", lw=LW * 0.7))
    ax.add_patch(Polygon([A, B, B + v, A + v], closed=True,
                         facecolor=GRAY_FILL2, edgecolor="k", lw=LW * 0.7))
    ax.plot([A[0], B[0]], [A[1], B[1]], color="k", lw=LW)
    M = A + 0.60 * u + 0.40 * (B - A)
    D = A + 0.90 * v + 0.50 * (B - A)
    C = np.array([1.0, 5.0]); foot = A + 0.35 * u + 0.25 * (B - A)
    ax.plot([C[0], foot[0]], [C[1], foot[1]], color="k", lw=LW * 0.7, ls="--")
    ax.plot([C[0]], [C[1]], "o", ms=2.6, color="k")
    ax.text(C[0] - 0.12, C[1] + 0.08, "$C$", fontsize=FS, ha="right")
    c1 = A + 0.50 * u + 0.50 * (B - A)
    c2 = A + 0.50 * v + 0.50 * (B - A)
    arrow(ax, c1[0], c1[1], c1[0] + n1dir[0], c1[1] + n1dir[1], lw=1.2)
    arrow(ax, c2[0], c2[1], c2[0] + n2dir[0], c2[1] + n2dir[1], lw=1.2)
    ax.text(A[0] - 0.10, A[1] - 0.40, "$A$", fontsize=FS)
    ax.text(B[0] + 0.06, B[1] - 0.40, "$B$", fontsize=FS)
    ax.text(M[0] - 0.10, M[1] + 0.10, "$M$", fontsize=FS)
    ax.text(D[0] + 0.10, D[1] + 0.05, "$D$", fontsize=FS)
    ax.text(c1[0] + n1dir[0] * 0.62 - 0.45, c1[1] + n1dir[1] * 0.62,
            "$\\vec{n_1}$", fontsize=FS)
    ax.text(c2[0] + n2dir[0] * 0.62 + 0.10, c2[1] + n2dir[1] * 0.62,
            "$\\vec{n_2}$", fontsize=FS)
    save(fig, name)


def make_bust():
    from PIL import Image, ImageOps, ImageEnhance
    import zipfile, io
    src = r"C:/提示词/高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"
    with zipfile.ZipFile(src) as z:
        im = Image.open(io.BytesIO(z.read("word/media/image294.png")))
    im = im.convert("RGB")
    w, h = im.size
    # bust occupies left ~27% width, above caption band
    bust = im.crop((0, 0, int(w * 0.27), int(h * 0.86)))
    g = ImageOps.grayscale(bust)
    g = ImageOps.autocontrast(g, cutoff=0)
    g = ImageEnhance.Contrast(g).enhance(1.05)
    # upscale to 300dpi target ~2.4cm wide
    target_w_px = int(2.4 / 2.54 * DPI)
    ratio = target_w_px / g.width
    g = g.resize((target_w_px, int(g.height * ratio)), Image.LANCZOS)
    g.save(os.path.join(OUT, "C_image294.png"), dpi=(DPI, DPI))
    print("wrote C_image294.png", g.size)


if __name__ == "__main__":
    fig_line_p0p()
    fig_line_b()
    fig_line_p1p2()
    fig_line_intercept()
    fig_hyperbola()
    fig_parab("right", "I2_image25.png")
    fig_parab("left", "I2_image26.png")
    fig_parab("up", "I2_image27.png")
    fig_parab("down", "I2_image28.png")
    fig_parab("right", "I2_image29.png")
    fig_parab("left", "I2_image30.png")
    fig_parab("up", "I2_image31.png")
    fig_parab("down", "I2_image32.png")
    fig_focal_chord()
    fig_tetra_vectors()
    fig_tetra_height("I1_image18.png")
    fig_dihedral(0, "B_image76.png", (-1.3, 1.6), (1.4, -1.7))
    fig_dihedral(1, "B_image77.png", (-1.5, 1.2), (1.2, -1.9))
    fig_dihedral(2, "B_image78.png", (-1.2, 1.7), (1.5, -1.5))
    fig_tetra_height("B_sub3_B_17.png")
    make_bust()
