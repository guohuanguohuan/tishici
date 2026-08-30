# -*- coding: utf-8 -*-
"""绘图能力演示：2D 椭圆焦点定义 + 3D 正四棱锥（对应选必1两章主题）"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------- 图1：二维椭圆（选必1 第2章 平面解析几何） ----------
a, b, c = 5.0, 4.0, 3.0
t = np.linspace(0, 2 * np.pi, 400)

fig, ax = plt.subplots(figsize=(7.2, 5.8))
ax.plot(a * np.cos(t), b * np.sin(t), color="#1f77b4", lw=2.4, zorder=4)

for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.spines["left"].set_position("zero")
ax.spines["bottom"].set_position("zero")
ax.set_xlim(-6.4, 6.4)
ax.set_ylim(-5.4, 5.4)
ax.grid(alpha=0.25, ls=":")

# 长/短轴
ax.plot([-a, a], [0, 0], ls="--", color="gray", lw=1.1, zorder=2)
ax.plot([0, 0], [-b, b], ls="--", color="gray", lw=1.1, zorder=2)

# 焦点
ax.scatter([-c, c], [0, 0], color="red", s=30, zorder=6)
ax.text(-c, -0.72, r"$F_1(-3,\,0)$", ha="center", fontsize=11)
ax.text(c, -0.72, r"$F_2(3,\,0)$", ha="center", fontsize=11)

# 椭圆上一点 P 与两条焦半径
tt = 0.92
px, py = a * np.cos(tt), b * np.sin(tt)
ax.plot([px, -c], [py, 0], color="#2ca02c", lw=1.8, zorder=3)
ax.plot([px, c], [py, 0], color="#ff7f0e", lw=1.8, zorder=3)
ax.scatter([px], [py], color="#d62728", s=38, zorder=7)
ax.annotate(r"$P$", (px, py), xytext=(px + 0.3, py + 0.15),
            fontsize=13, color="#d62728")
ax.text(-2.0, 2.05, r"$|PF_1|$", color="#2ca02c", fontsize=12)
ax.text(2.5, 1.75, r"$|PF_2|$", color="#ff7f0e", fontsize=12)

# 顶点标注
ax.text(-a, 0.42, r"$A_1$", ha="center", fontsize=11)
ax.text(a, 0.42, r"$A_2$", ha="center", fontsize=11)
ax.text(0.3, b, r"$B_2$", fontsize=11)
ax.text(0.3, -b - 0.5, r"$B_1$", fontsize=11)

ax.set_title(r"椭圆 $\frac{x^2}{25}+\frac{y^2}{16}=1$：$|PF_1|+|PF_2|=2a=10$",
             fontsize=13, pad=12)
ax.set_aspect("equal")
fig.savefig(os.path.join(OUT, "demo_2d_ellipse.png"), dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------- 图2：三维正四棱锥 P-ABCD（选必1 第1章 空间向量与立体几何） ----------
A = np.array([-1.0, -1.0, 0.0])
B = np.array([1.0, -1.0, 0.0])
C = np.array([1.0, 1.0, 0.0])
D = np.array([-1.0, 1.0, 0.0])
P = np.array([0.0, 0.0, 1.7])
O = np.array([0.0, 0.0, 0.0])

fig = plt.figure(figsize=(6.6, 5.8))
ax = fig.add_subplot(projection="3d")

def seg(u, v, style="-", color="k", lw=1.8):
    ax.plot([u[0], v[0]], [u[1], v[1]], [u[2], v[2]],
            style, color=color, lw=lw)

# 被遮挡的棱画虚线（教材惯例）：后底边 CD、DA，侧棱 PC、PD，高 PO
seg(C, D, "--", "0.45")
seg(D, A, "--", "0.45")
seg(P, C, "--", "0.45")
seg(P, D, "--", "0.45")
seg(P, O, "--", "0.55", lw=1.4)
# 可见棱实线
seg(A, B)
seg(B, C)
seg(P, A)
seg(P, B)

# 底面与两个可见侧面淡淡着色
base = Poly3DCollection([[A, B, C, D]], alpha=0.08, facecolor="#1f77b4")
face1 = Poly3DCollection([[P, A, B]], alpha=0.10, facecolor="#ff7f0e")
face2 = Poly3DCollection([[P, B, C]], alpha=0.10, facecolor="#2ca02c")
for coll in (base, face1, face2):
    ax.add_collection3d(coll)

# 直角记号：PO ⊥ 底面，在 O 处画小方块
s_ = 0.18
ax.plot([0, s_, s_, 0], [-s_, -s_, 0, 0], [0, 0, 0, 0], color="0.4", lw=1.0)

# 顶点标签
lbl = dict(fontsize=13)
ax.text(A[0] - 0.12, A[1] - 0.12, A[2] - 0.12, r"$A$", **lbl)
ax.text(B[0] + 0.08, B[1] - 0.18, B[2] - 0.12, r"$B$", **lbl)
ax.text(C[0] + 0.10, C[1] + 0.10, C[2] - 0.12, r"$C$", **lbl)
ax.text(D[0] - 0.22, D[1] + 0.08, D[2] - 0.12, r"$D$", **lbl)
ax.text(P[0] - 0.10, P[1] - 0.05, P[2] + 0.10, r"$P$", **lbl)
ax.text(O[0] + 0.06, O[1] - 0.28, O[2] - 0.05, r"$O$", fontsize=12)

ax.set_xlim(-1.4, 1.4)
ax.set_ylim(-1.4, 1.4)
ax.set_zlim(0, 2.0)
ax.set_box_aspect((1, 1, 0.8))
ax.view_init(elev=16, azim=-58)
ax.set_axis_off()
ax.set_title("正四棱锥 $P$–$ABCD$（$PO\\perp$ 底面 $ABCD$）", fontsize=13, pad=2)
fig.savefig(os.path.join(OUT, "demo_3d_pyramid.png"), dpi=150, bbox_inches="tight")
plt.close(fig)

print("OK: 2 files written to", OUT)
