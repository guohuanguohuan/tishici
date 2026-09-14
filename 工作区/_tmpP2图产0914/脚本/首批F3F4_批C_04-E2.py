# -*- coding: utf-8 -*-
"""首批面 F3/F4：04-E2（债行〔04-E2〕共2处）题图装置＋四选项图像（合一面）。
题面：电容器充电后断开电源、负极板接地、正检验电荷固定于 P；正极板不动、负极板缓慢右移 l₀。
答案 BC 判据链钉死（以图为准口径）：
  B：Q 恒、S 恒 ⟹ E＝4πkQ/(εrS) 与 d 无关 ⟹ E-x 水平直线（对）；
  C：φ_P＝E·(P 到负极板距离)，负极板右移趋 P ⟹ 距离 L−x 线性减 ⟹ φ-x 线性降（对）；
  A：C-x 真实为双曲线，选项画直线降（错）；D：E_p 真实线性降，选项画非线性曲线（错）。
装置图几何钉死：负极板在 P 左侧、右移趋 P（保 C 选项判立）；接地符号在负极板。
风格照 P1 figs 先例，150dpi。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
OUT = r"C:\提示词\工作区\_tmpP2图产0914"
CYAN = "#29B6F6"

# —— 题-图-答三方一致性自核（编码化）——
Qq, S_, k_eps = 1.0, 1.0, 1.0            # 量纲归一
d0, L = 2.0, 0.6                          # 初始板距、P 到负极板初始距离
Es = []
for x in (0.0, 0.2, 0.4):
    C = k_eps * S_ / (d0 + x)             # 负极板右移⟹板距增大
    U = Qq / C
    Es.append(U / (d0 + x))               # E＝U/d
    assert abs(U / (d0 + x) - Es[0]) < 1e-9, "E 随 d 变（B 判据崩）"
E = Es[0]
for x in (0.0, 0.2, 0.4):
    phiP = E * (L - x)                    # 负极板在 P 左侧、右移趋 P
    assert phiP > 0 and np.gradient([E * (L - xx) for xx in (0, 0.1, 0.2)])[0] < 0, \
        "φ_P 未随 x 线性降（C 判据崩）"
print("04-E2 自核：E=%.2f 恒与 d 无关 ✓ φ_P=E(L−x) 线性降 ✓（装置几何：负—P—正，右移趋P）" % E)

# ---------- F3 题图装置 ----------
fig, ax = plt.subplots(figsize=(4.6, 3.1))
ax.set_aspect("equal"); ax.axis("off")
xn, xp, h = 0.95, 3.15, 1.05
for xx, lab, sgn, pos in [(xn, "负极板", "－", "left"), (xp, "正极板", "＋", "right")]:
    ax.add_patch(plt.Rectangle((xx - 0.035, -h), 0.07, 2 * h, facecolor="white",
                               edgecolor="k", lw=1.7, zorder=4))
    ax.text(xx, h + 0.16, lab, ha="center", fontsize=11)
    ax.text(xx + (0.16 if pos == "right" else -0.16), h - 0.22, sgn,
            ha="center", fontsize=13)
# 场强箭头（正→负，水平向左）
for yy in (-0.52, 0.52):
    ax.annotate("", xy=(xn + 0.12, yy), xytext=(xp - 0.12, yy),
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.3))
ax.annotate("", xy=(1.70, 0), xytext=(1.98, 0),
            arrowprops=dict(arrowstyle="-|>", color="k", lw=1.3))
# P 点正检验电荷
ax.plot(1.55, 0, "k.", ms=7, zorder=5)
ax.text(1.55, 0.17, "$P$", ha="center", fontsize=13)
ax.text(1.47, -0.30, "+", ha="center", fontsize=11)
# 负极板接地符号
ax.plot([xn, xn], [-h, -h - 0.30], color="k", lw=1.4)
for w, yy in [(0.34, -h - 0.30), (0.22, -h - 0.38), (0.10, -h - 0.46)]:
    ax.plot([xn - w / 2, xn + w / 2], [yy, yy], color="k", lw=1.4)
# 负极板右移 x（青虚线箭头）
ax.annotate("", xy=(xn + 0.95, h + 0.55), xytext=(xn, h + 0.55),
            arrowprops=dict(arrowstyle="->", color=CYAN, lw=1.5, linestyle="--"))
ax.text(xn + 0.48, h + 0.68, "$x$", ha="center", fontsize=12, color="k")
ax.set_xlim(0.1, 4.05); ax.set_ylim(-2.05, 2.05)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\04-E2-题图装置.png", dpi=150, facecolor="white")
plt.close(fig)

# ---------- F4 四选项图像（一面四格：A直线降✗ B水平✓ C线性降✓ D曲线降✗） ----------
fig, axs = plt.subplots(2, 2, figsize=(5.4, 3.9))
xx = np.linspace(0, 3, 300)
panels = [
    ("A", "$C$",   lambda x: 3.4 - 0.9 * x,                    "k-"),
    ("B", "$E$",   lambda x: 2.2 + 0 * x,                      "k-"),
    ("C", r"$\varphi$", lambda x: 3.4 - 0.9 * x,               "k-"),
    ("D", "$E_p$", lambda x: 3.4 - 2.9 * (1 - np.exp(-x / 1.05)), "k-"),
]
for axp, (letter, ylab, fun, _) in zip(axs.flat, panels):
    axp.annotate("", xy=(3.45, 0), xytext=(-0.12, 0),
                 arrowprops=dict(arrowstyle="->", color="k", lw=0.9))
    axp.annotate("", xy=(0, 4.15), xytext=(0, -0.12),
                 arrowprops=dict(arrowstyle="->", color="k", lw=0.9))
    axp.plot(xx, fun(xx), color="k", lw=1.6)
    axp.text(3.42, -0.72, "$x$", fontsize=10)
    axp.text(-0.62, 3.72, ylab, fontsize=11)
    axp.text(-0.42, 4.42, letter, fontsize=13,
             fontfamily="SimHei", math_fontfamily="dejavusans")
    axp.set_xlim(-0.75, 3.9); axp.set_ylim(-1.1, 5.0)
    axp.axis("off")
fig.tight_layout(pad=0.35)
fig.savefig(OUT + r"\04-E2-选项图像.png", dpi=150, facecolor="white")
plt.close(fig)
print("F3/F4 写出：04-E2-题图装置.png ＋ 04-E2-选项图像.png（A直✗/B平✓/C直✓/D曲✗）")
