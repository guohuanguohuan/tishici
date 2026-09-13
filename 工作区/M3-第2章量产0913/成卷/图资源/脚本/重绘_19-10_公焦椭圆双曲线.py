# -*- coding: utf-8 -*-
"""重绘 19-10（课时19 变式10：椭圆 C₁ 与双曲线 C₂ 公共焦点，A(二象限)、B(四象限) 公共点）
源：富矿件19-#8，源件无图（段邻域±(2,14)无图实测），按题面数据重绘。
自验：|OF₁|=½|AB|、∠OF₁B=π/6、A/B 同落两曲线、|AF₁|=|AF₂| 关系全核。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

c = 1.0
F1 = np.array([-c, 0.0]); F2 = np.array([c, 0.0])
# B 第四象限：|OB|=c，∠OF₁B=π/6 → ∠F₁OB=2π/3 → OB 方位 −60°
B = np.array([c * np.cos(np.pi / 3), -c * np.sin(np.pi / 3)])
A = -B                                    # O 为 AB 中点（二象限）
e1 = 2 / (np.sqrt(3) + 1)                 # 椭圆离心率
e2 = 2 / (np.sqrt(3) - 1)                 # 双曲线离心率
a1 = c / e1; b1 = np.sqrt(a1**2 - c**2)   # 椭圆
a2 = c / e2; b2 = np.sqrt(c**2 - a2**2)   # 双曲线

# —— 自验（题面数据逐条）——
AB = np.linalg.norm(B - A)
assert abs(2 * c - AB) < 1e-12, "|AB|≠2|OF₁|"
ang = np.arccos(np.dot(B - F1, -F1) / (np.linalg.norm(B - F1) * c))
assert abs(ang - np.pi / 6) < 1e-12, "∠OF₁B≠π/6"
for P in (A, B):
    d_ell = np.hypot(P[0] / a1, P[1] / b1)
    d_hyp = P[0] ** 2 / a2**2 - P[1] ** 2 / b2**2
    assert abs(d_ell - 1) < 1e-9, "点不在椭圆上"
    assert abs(d_hyp - 1) < 1e-9, "点不在双曲线上"
    assert abs(np.hypot(P[0] - c, P[1]) + np.hypot(P[0] + c, P[1]) - 2 * a1) < 1e-9
print("19-10 自验：|AB|=2c=%.2f ✓ ∠OF₁B=30° ✓ A/B 同落两曲线 ✓ e₁e₂=%.6f（=2）" % (AB, e1 * e2))
assert abs(e1 * e2 - 2) < 1e-12

fig, ax = plt.subplots(figsize=(4.8, 4.0))
t = np.linspace(0, 2 * np.pi, 721)
ax.plot(a1 * np.cos(t), b1 * np.sin(t), color="k", lw=1.4, zorder=2)          # 椭圆
xx = np.linspace(a2, 2.6, 401)
yy = b2 * np.sqrt(xx**2 / a2**2 - 1)
for sx in (+1, -1):
    for sy in (+1, -1):
        ax.plot(sx * xx, sy * yy, color="k", lw=1.4, zorder=2)                # 双曲线两支
ax.axhline(0, color="0.55", lw=0.6, zorder=1)
ax.axvline(0, color="0.55", lw=0.6, zorder=1)

ax.plot(*F1, "k.", ms=6); ax.plot(*F2, "k.", ms=6)
ax.plot(*A, "k.", ms=6);  ax.plot(*B, "k.", ms=6)
ax.annotate("$F_1$", F1, xytext=(-1.28, -0.30), fontsize=13)
ax.annotate("$F_2$", F2, xytext=(0.82, -0.30), fontsize=13)
ax.annotate("$A$", A, xytext=(A[0] - 0.34, A[1] + 0.10), fontsize=13)
ax.annotate("$B$", B, xytext=(B[0] + 0.06, B[1] - 0.30), fontsize=13)
ax.annotate("$O$", (0, 0), xytext=(-0.30, -0.32), fontsize=13)
ax.plot([A[0], B[0]], [A[1], B[1]], color="0.45", lw=0.8, ls="--", zorder=1)  # 对角线 AB
ax.set_xlim(-1.75, 1.75); ax.set_ylim(-1.42, 1.42)
ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout(pad=0.2)

out = r"C:\提示词\工作区\M3-第2章量产0913\成卷\图资源\19-10"
fig.savefig(out + ".png", dpi=300, facecolor="white")
fig.savefig(out + ".pdf", facecolor="white")
print("写出", out + ".png / .pdf")
