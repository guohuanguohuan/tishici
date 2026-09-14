# -*- coding: utf-8 -*-
"""首批面 F8：02-E6（E-10）双点电荷 φ-x 分布图线。
题面：M 固定于 x=−20cm、N 固定于原点；φ-x 图线（x 轴正半轴）交 x 轴于 x₀，x=20cm 处最低；
无穷远 φ=0。答案 AD 判据钉死：x₀ 处斜率≠0（B 判否）；20cm 处斜率=0 ⟹ Q_M:Q_N=4:1（C 判否）；
x₀→20cm φ 降、越 20cm φ 升（D 判立）；近原点 φ→+∞（N 正电、M 负电，A 判立）。
建模：φ(x)=kQ_N/x−kQ_M/(x+0.2)，Q_M=4Q_N（k、Q_N 归一）。风格照 P1 figs 先例，150dpi。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
OUT = r"C:\提示词\工作区\_tmpP2图产0914"
CYAN = "#29B6F6"

phi = lambda x: 1.0 / x - 4.0 / (x + 0.20)     # Q_N=1、Q_M=4（k 归一）
x0 = 1.0 / 15.0                                 # 过零点 ≈ 6.7cm
# —— 题-图-答三方一致性自核（编码化）——
assert abs(phi(x0)) < 1e-12, "x₀ 处未过零"
xmin = np.linspace(0.05, 0.45, 4001)[np.argmin(phi(np.linspace(0.05, 0.45, 4001)))]
assert abs(xmin - 0.20) < 0.001, "最低点不在 x=20cm"
assert abs((1 / 0.2 - 4 / 0.4) + 5) < 1e-9, "20cm 处 φ_min=−5kQ_N 校验崩"
E0 = -(phi(x0 + 1e-6) - phi(x0 - 1e-6)) / 2e-6   # E=−dφ/dx
assert abs(E0) > 0.5, "x₀ 处斜率为 0（B 判否依据崩）"
assert abs((0.4**2) / (0.2**2) - 4) < 1e-12, "Q_M:Q_N=4:1 距离反比核崩"
assert phi(0.10) > phi(0.20) < phi(0.35), "先降后升形状崩（D 判据）"
assert phi(0.004) > 0, "近原点 φ→+∞（N 正、M 负，A 判据）"
print("02-E6 自核：x₀=1/15≈%.2fcm 过零 ✓ 20cm 最低 φ=−5 ✓ E(x₀)=%.1f≠0 ✓ "
      "Q_M:Q_N=4:1 ✓ 先降后升 ✓" % (x0 * 100, abs(E0)))

fig, ax = plt.subplots(figsize=(4.9, 3.5))
xx = np.linspace(0.0045, 0.50, 1200)
ax.plot(xx, phi(xx), color="k", lw=1.7, zorder=3)
# 坐标轴（带箭头）
ax.annotate("", xy=(0.54, 0), xytext=(-0.31, 0),
            arrowprops=dict(arrowstyle="->", color="k", lw=1.0), zorder=2)
ax.annotate("", xy=(0, 6.6), xytext=(0, -6.8),
            arrowprops=dict(arrowstyle="->", color="k", lw=1.0), zorder=2)
ax.text(0.545, -0.85, "$x$", fontsize=13)
ax.text(-0.075, 6.55, r"$\varphi$", fontsize=14, va="top")
# 点电荷 M（x=−20cm）、N（原点）
ax.plot(0, 0, "k.", ms=6); ax.plot(-0.20, 0, "k.", ms=6)
ax.text(0.004, -1.35, "$N$", fontsize=13)
ax.text(-0.243, -1.35, "$M$", fontsize=13)
# x₀ 过零点与 20cm 最低点（钉死标注）
ax.plot([x0], [0], "k.", ms=6)
ax.plot([x0, x0], [-0.0, -0.28], color="k", lw=1.0)
ax.text(x0 - 0.028, -0.72, "$x_0$", ha="right", fontsize=13)
ax.plot([0.20], [-5.0], "k.", ms=6)
ax.plot([0.20, 0.20], [-5.0, 0], color=CYAN, lw=0.9, ls="--", zorder=1)
ax.plot([0, 0.20], [-5.0, -5.0], color=CYAN, lw=0.9, ls="--", zorder=1)
ax.text(0.185, -0.72, "20 cm", ha="right", fontsize=11)
ax.set_xlim(-0.31, 0.57); ax.set_ylim(-7.0, 6.9)
ax.set_aspect("auto"); ax.axis("off")
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\02-E6-题图φx.png", dpi=150, facecolor="white")
print("F8 写出：02-E6-题图φx.png")
