# -*- coding: utf-8 -*-
"""重绘 19-16（课时19 例16：C₁:y²=2p₁x 与 C₂:y²=−2px，过 C(−1,0) 直线交 C₁ 于 A、C₂ 于 B，B 为 AC 中点）
源：富矿件19-#15，源件无图（段邻域无图实测），按题面数据重绘（取 p₁=2、p=2 作图）。
自验：C 在 C₁ 准线上；A 落 C₁、B 落 C₂；B 为 AC 中点；A 的横坐标=p/(p+1)。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

p1, p = 2.0, 2.0                    # 作图取值（题面只给 p₁>0、p>0）
C = np.array([-1.0, 0.0])
assert abs(-p1 / 2 - C[0]) < 1e-12  # C 在 C₁ 准线 x=−p₁/2 上

# 联立读数：B(−t²/(2p), t)，A=2B−C，A 落 C₁ → t²=p/(p+1)
t2 = p / (p + 1)
t = np.sqrt(t2)
B = np.array([-t2 / (2 * p), t])
A = 2 * B - C
# —— 自验 ——
assert abs(A[1] ** 2 - 2 * p1 * A[0]) < 1e-9, "A 不在 C₁ 上"
assert abs(B[1] ** 2 - (-2 * p) * B[0]) < 1e-9, "B 不在 C₂ 上"
assert np.allclose((A + C) / 2, B), "B 非 AC 中点"
assert abs(A[0] - p / (p + 1)) < 1e-12, "x_A≠p/(p+1)"
print("19-16 自验：C 在准线 x=%.1f ✓ A(%.3f,%.3f)∈C₁ ✓ B(%.3f,%.3f)∈C₂ ✓ B=AC中点 ✓ x_A=p/(p+1)=%.3f ✓"
      % (-p1 / 2, A[0], A[1], B[0], B[1], A[0]))

fig, ax = plt.subplots(figsize=(5.4, 3.9))
yy = np.linspace(-2.6, 2.6, 481)
ax.plot(yy**2 / (2 * p1), yy, color="k", lw=1.4, zorder=2)      # C₁：y²=2p₁x（右开口）
ax.plot(-yy**2 / (2 * p), yy, color="k", lw=1.4, zorder=2)      # C₂：y²=−2px（左开口）
ax.axhline(0, color="0.55", lw=0.6, zorder=1)
ax.axvline(0, color="0.55", lw=0.6, zorder=1)
ax.plot([C[0], A[0]], [C[1], A[1]], color="0.35", lw=0.9, ls="--", zorder=1)  # 截线 C–B–A
for P, name, dx, dy in ((C, "$C$", -0.16, -0.34), (A, "$A$", 0.12, 0.10), (B, "$B$", 0.12, 0.06)):
    ax.plot(*P, "k.", ms=6)
    ax.annotate(name, P, xytext=(P[0] + dx, P[1] + dy), fontsize=13)
ax.annotate("$O$", (0, 0), xytext=(-0.22, -0.30), fontsize=13)
ax.annotate("$C_1$", (2.35, -1.9), fontsize=13)
ax.annotate("$C_2$", (-2.5, 1.75), fontsize=13)
ax.set_xlim(-2.9, 2.9); ax.set_ylim(-2.35, 2.35)
ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout(pad=0.2)

out = r"C:\提示词\工作区\M3-第2章量产0913\成卷\图资源\19-16"
fig.savefig(out + ".png", dpi=300, facecolor="white")
fig.savefig(out + ".pdf", facecolor="white")
print("写出", out + ".png / .pdf")
