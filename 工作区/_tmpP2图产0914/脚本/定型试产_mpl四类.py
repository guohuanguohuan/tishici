# -*- coding: utf-8 -*-
"""P2 图产试产臂·工艺定型试产（matplotlib 链）——四类各一：电路图/等势面图/φ-x 图象/f-Ek 折线。
风格照 P1-必修3第9章 figs 先例：白底黑线、青色虚线辅线、cm 数学字体、SimHei 中文、无图题。
红线：禁 AI 三维图（军规）——本链全为二维矢量示意。输出 150dpi PNG。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

OUT = r"C:\提示词\工作区\_tmpP2图产0914\试产-工艺定型"
CYAN = "#29B6F6"   # P1 先例辅线青
LW = 1.6

# ---------- 定型1：电路图（E、S、R、电容 AB 单环） ----------
fig, ax = plt.subplots(figsize=(4.6, 3.0))
ax.set_aspect("equal"); ax.axis("off")
k = dict(color="k", lw=LW, solid_capstyle="butt", zorder=3)
# 左侧电池 E（长线正上、短线负下）
ax.plot([0, 0], [0, 1.05], **k); ax.plot([0, 0], [1.75, 2.6], **k)
ax.plot([-0.34, 0.34], [1.75, 1.75], **k)          # 长线（＋）
ax.plot([-0.20, 0.20], [1.38, 1.38], lw=3.2, color="k", zorder=3)  # 短线（－）
ax.text(-0.52, 1.62, "$+$", fontsize=11)
ax.text(-0.55, 1.02, "$E$", fontsize=14)
# 顶边开关 S（枢轴 1.5，掷点 2.3）
ax.plot([0, 1.5], [2.6, 2.6], **k); ax.plot([2.3, 4.2], [2.6, 2.6], **k)
ax.plot(1.5, 2.6, "k.", ms=5); ax.plot(2.3, 2.6, "k.", ms=5)
ax.plot([1.5, 2.22], [2.6, 2.95], **k)
ax.text(1.78, 3.02, "$S$", fontsize=14)
# 右侧电容 AB（水平极板、竖直引线）
ax.plot([4.2, 4.2], [2.6, 1.72], **k); ax.plot([4.2, 4.2], [1.08, 0], **k)
ax.plot([3.86, 4.54], [1.72, 1.72], lw=2.4, color="k", zorder=3)
ax.plot([3.86, 4.54], [1.08, 1.08], lw=2.4, color="k", zorder=3)
ax.text(4.66, 1.70, "$A$", fontsize=13); ax.text(4.66, 0.92, "$B$", fontsize=13)
ax.annotate("", xy=(4.2, 1.20), xytext=(4.2, 1.60),
            arrowprops=dict(arrowstyle="->", color=CYAN, lw=1.2))
# 底边电阻 R（教科书面框式）
ax.plot([4.2, 2.75], [0, 0], **k); ax.plot([1.45, 0], [0, 0], **k)
ax.add_patch(plt.Rectangle((1.45, -0.17), 1.3, 0.34, fill=False, lw=LW, ec="k", zorder=3))
ax.text(2.06, -0.52, "$R$", fontsize=14)
ax.set_xlim(-0.9, 5.3); ax.set_ylim(-0.8, 3.4)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\定型1-电路图_mpl.png", dpi=150, facecolor="white")
plt.close(fig)

# ---------- 定型2：等势面图（正点电荷同心圆＋标值＋场线） ----------
fig, ax = plt.subplots(figsize=(4.2, 4.2))
ax.set_aspect("equal"); ax.axis("off")
for r, lab in [(0.72, "15 V"), (1.18, "10 V"), (1.64, "5 V")]:
    th = np.linspace(0, 2 * np.pi, 361)
    ax.plot(r * np.cos(th), r * np.sin(th), color=CYAN, lw=1.1, ls="--", zorder=2)
    ang = np.deg2rad(22.5)                    # 标值放两根场线之间，防压线
    ax.text((r + 0.09) * np.cos(ang), (r + 0.09) * np.sin(ang),
            lab, fontsize=11, color="k")
for ang in np.arange(90, 360 + 90, 45):   # 8 条辐射电场线（沿量化方向）
    dx, dy = np.cos(np.deg2rad(ang)), np.sin(np.deg2rad(ang))
    ax.plot([0.16 * dx, 2.05 * dx], [0.16 * dy, 2.05 * dy], color="k", lw=1.1, zorder=1)
    ax.annotate("", xy=(0.62 * dx, 0.62 * dy), xytext=(0.46 * dx, 0.46 * dy),
                arrowprops=dict(arrowstyle="->", color="k", lw=1.1))
ax.plot(0, 0, "o", ms=11, mfc="#FFF9C4", mec="k", mew=1.3, zorder=4)
ax.text(0.0, 0.0, "+", ha="center", va="center", fontsize=12, zorder=5)
ax.text(0.10, -0.30, "$q$", fontsize=13)
ax.set_xlim(-2.3, 2.3); ax.set_ylim(-2.3, 2.3)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\定型2-等势面图_mpl.png", dpi=150, facecolor="white")
plt.close(fig)

# ---------- 定型3：φ-x 图象（02-E6 数据草案：Q_N=1 于 0，Q_M=4 于 −0.2m） ----------
# 自验：20cm 处最低＝−5（单位 kQ_N/m）；过零 x₀＝1/15 m
x = np.linspace(0.006, 0.46, 900)
phi = 1.0 / x - 4.0 / (x + 0.20)
assert abs(phi[np.argmin(np.abs(x - 0.20))] + 5.0) < 0.05, "20cm 处非最低 −5"
x0 = 1 / 15
assert abs((1 / x0 - 4 / (x0 + 0.2))) < 1e-12, "过零点非 x₀=1/15"
fig, ax = plt.subplots(figsize=(4.8, 3.4))
ax.axhline(0, color="k", lw=1.0, zorder=2)
ax.axvline(0, color="k", lw=1.0, zorder=2)
ax.plot(x, phi, color="k", lw=1.6, zorder=3)
ax.plot(0, 0, "k.", ms=6); ax.plot(-0.20, 0, "k.", ms=6)
ax.annotate("$N$", (0, 0), xytext=(0.012, -1.6), fontsize=13)
ax.annotate("$M$", (-0.20, 0), xytext=(-0.245, -1.6), fontsize=13)
ax.plot([x0], [0], "k.", ms=6)
ax.annotate("$x_0$", (x0, 0), xytext=(x0 - 0.085, 1.1), fontsize=13)
ax.plot([0.20], [-5.0], "k.", ms=6)
ax.annotate("20 cm", (0.20, -5.0), xytext=(0.245, -5.75), fontsize=11)
ax.set_xlim(-0.28, 0.50); ax.set_ylim(-6.8, 6.8)
ax.set_xlabel("$x$", fontsize=12, loc="right")
ax.set_ylabel(r"$\varphi$", fontsize=14, loc="top", rotation=0)
ax.set_xticks([]); ax.set_yticks([])
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\定型3-φx图象_mpl.png", dpi=150, facecolor="white")
plt.close(fig)

# ---------- 定型4：f-Ek 折线（R4M-05 候补示意风格：均匀减小→均匀增大） ----------
fig, ax = plt.subplots(figsize=(4.6, 3.2))
ax.axhline(0, color="k", lw=1.0); ax.axvline(0, color="k", lw=1.0)
xs = [0.0, 1.6, 3.4]; ys = [5.2, 1.6, 5.2]
ax.plot(xs, ys, color="k", lw=1.7, zorder=3)
for px, py in zip(xs[1:], ys[1:]):
    ax.plot([px], [py], "k.", ms=5)
ax.plot([1.6, 1.6], [0, 1.6], color=CYAN, lw=1.0, ls="--", zorder=1)
ax.plot([0, 1.6], [1.6, 1.6], color=CYAN, lw=1.0, ls="--", zorder=1)
ax.text(0.55, 4.35, "均匀减小", fontsize=11)
ax.text(2.28, 2.42, "均匀增大", fontsize=11)
ax.text(1.56, -0.62, "$x_1$", fontsize=12)
ax.text(3.34, -0.62, "$x_2$", fontsize=12)
ax.set_xlim(-0.25, 4.1); ax.set_ylim(-1.2, 6.4)
ax.set_xlabel("$x$", fontsize=12, loc="right")
ax.set_ylabel("$E_k$", fontsize=13, loc="top", rotation=0)
ax.set_xticks([]); ax.set_yticks([])
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\定型4-fEk折线_mpl.png", dpi=150, facecolor="white")
plt.close(fig)
print("定型试产 matplotlib 链 4 张写出：定型1电路/定型2等势面/定型3φx/定型4fEk")
