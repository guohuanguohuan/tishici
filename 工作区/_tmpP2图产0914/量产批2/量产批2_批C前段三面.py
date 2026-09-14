# -*- coding: utf-8 -*-
"""量产批2（批C 前段 3 面）：04-G1 铭牌图＋04-G1 C项符号图＋05-T1 图甲装置。
钉死规格（台账§2.3 照录，只读）：
  04-G1：题图铭牌承载题给数据（C/Q/U 读数域）＋C 项符号图——按定稿批C-课时04 详解
         「C项符号为可调电容器符号」落图（保答案 B 唯一；债行措辞「固定电容符号图」
         与详解口径差已在 回填段.md 送主脑统落）。
  05-T1：图甲装置与已产图乙方波（脚本/首批F6F7_批C_05-T1T2.py）同参配对：
         u=φ_A−φ_B，[0,T/2)=+U₀ 驱电子向A；极性/周期/幅值不重画图乙。
风格照 P1 figs 先例：白底黑线、青虚线辅线、cm 数学字体、SimHei 中文、无图题、150dpi。
红线：零 git；定稿/台账/在产件只读；写入仅本目录（量产批2/）。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
OUT = r"C:\提示词\工作区\_tmpP2图产0914\量产批2"
CYAN = "#29B6F6"
LW = 1.6

# ================= 面1：04-G1 题图铭牌（电解电容器外壳铭牌） =================
# 钉死：铭牌读数域＝{2200μF, 80V}，逐项照录定稿题面（「2200μF」电容读数、80V 电压读数）；
# 铭牌只印裸读数——印「额定电压」字样会拆 D 项陷阱（详解：铭牌所标80V为额定电压）。
C_uF, U_V = 2200.0, 80.0
C_F = C_uF * 1e-6
assert abs(C_F - 2.2e-3) < 1e-12, "电容读数崩：2200μF 须为 2.2×10⁻³F"
Q_at_1V = C_F * 1.0                                   # 选项B链：U=1V 时 Q=CU
assert abs(Q_at_1V - 2.2e-3) < 1e-12, "Q=CU 崩（选项B链）"
assert C_F != 2200.0, "选项A陷阱失效：2200μF≠2200F 须保持"
READ_C, READ_U = "$2200\\,\\mu\\mathrm{F}$", "$80\\,\\mathrm{V}$"
assert [READ_C, READ_U] == ["$2200\\,\\mu\\mathrm{F}$", "$80\\,\\mathrm{V}$"], "铭牌读数域崩"
print("04-G1-铭牌 自核：读数域{2200μF, 80V} ✓ Q=CU=2.2×10⁻³C（U=1V，B链）✓ "
      "2200μF=2.2×10⁻³F≠2200F（A陷阱在）✓")

fig, ax = plt.subplots(figsize=(2.8, 3.6))
ax.set_aspect("equal"); ax.axis("off")
# 外壳（浅灰套管）＋顶部套管收口线
ax.add_patch(plt.Rectangle((0, 0), 2.0, 2.6, fc="#ECEFF1", ec="k", lw=LW, zorder=2))
ax.plot([0.06, 1.94], [2.30, 2.30], color="k", lw=1.0, zorder=3)
# 铭牌（白底黑框，承载题给读数）
ax.add_patch(plt.Rectangle((0.30, 0.72), 1.40, 1.34, fc="white", ec="k",
                           lw=1.0, zorder=3))
ax.text(1.0, 1.70, READ_C, ha="center", va="center", fontsize=15, zorder=4)
ax.text(1.0, 1.10, READ_U, ha="center", va="center", fontsize=15, zorder=4)
# 两引线（底部）
ax.plot([0.6, 0.6], [0, -0.72], color="k", lw=1.4, zorder=1)
ax.plot([1.4, 1.4], [0, -0.72], color="k", lw=1.4, zorder=1)
ax.text(1.0, -1.02, "电解电容器", ha="center", va="center", fontsize=11)
ax.set_xlim(-0.45, 2.45); ax.set_ylim(-1.32, 2.88)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\04-G1-题图铭牌.png", dpi=150, facecolor="white")
plt.close(fig)

# ================= 面2：04-G1 C项符号图（可调电容器符号） =================
# 钉死：定稿详解「C项符号为可调电容器符号」→ 图内须含可调箭头（斜箭头过双板），
# C 项辨析由「固定电容 vs 带箭头符号」承载；单选项图面不入字母（试产报告§三-2 口径）。
x1, x2, yb, yt = 1.25, 1.75, 0.55, 1.45                # 双板几何
assert x2 > x1 and yt > yb and abs((yt - yb) - 0.9) < 1e-9, "双板几何崩"
axr_s, axr_e = 0.85, 2.35                              # 可调箭头起讫
ayr_s, ayr_e = 0.30, 1.80
k_arr = (ayr_e - ayr_s) / (axr_e - axr_s)
y_at_p1 = ayr_s + k_arr * (x1 - axr_s)
y_at_p2 = ayr_s + k_arr * (x2 - axr_s)
assert ayr_s < yb and ayr_e > yt, "可调箭头未越过双板"
assert yb < y_at_p1 < yt and yb < y_at_p2 < yt, "箭头未穿过双板区"
print("04-G1-C项 自核：双板平行等长 ✓ 可调箭头过双板 ✓ "
      "（定稿详解：C项符号为可调电容器符号→C错误，答案B唯一）")

fig, ax = plt.subplots(figsize=(3.2, 1.7))
ax.set_aspect("equal"); ax.axis("off")
ax.plot([0, x1], [1, 1], color="k", lw=1.4, solid_capstyle="butt", zorder=3)
ax.plot([x2, 3.0], [1, 1], color="k", lw=1.4, solid_capstyle="butt", zorder=3)
ax.plot([x1, x1], [yb, yt], lw=2.4, color="k", zorder=3)   # 板1
ax.plot([x2, x2], [yb, yt], lw=2.4, color="k", zorder=3)   # 板2
ax.annotate("", xy=(axr_e, ayr_e), xytext=(axr_s, ayr_s),
            arrowprops=dict(arrowstyle="->", color="k", lw=1.4), zorder=2)
ax.set_xlim(-0.15, 3.15); ax.set_ylim(0.15, 1.95)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\04-G1-C项符号图.png", dpi=150, facecolor="white")
plt.close(fig)

# ================= 面3：05-T1 图甲装置（平行板 A/B＋电子＋交变电压 u） =================
# 钉死：装置几何照定稿题面——A/B 双板、板间固定电子（静止、重力不计）、两板接
# 图乙交变电压 u；与已产图乙（F6）同参配对：u=φ_A−φ_B、[0,T/2)=+U₀ 驱电子向A。
xA, xB, ye0, ye1 = 0.0, 3.2, 0.2, 1.8                  # 双板几何（竖直平行）
xe = 1.6                                               # 电子位（板间中点）
T, U0 = 2.0, 1.0                                       # 与已产图乙 F6 同参
u = lambda t: U0 if (t % T) < T / 2 else -U0
assert xA < xe < xB, "电子不在板间"
assert u(T / 8) > 0 and u(5 * T / 8) < 0, "极性链崩：[0,T/2) 须 +U₀（驱电子向A）"
assert u(0.3) == u(T + 0.3), "周期崩（与图乙不同参）"
assert (xB - xA) > (ye1 - ye0), "板距须宽于板高（题面「两板距离足够宽」示意）"
print("05-T1-图甲 自核：A/B 竖直平行板 ✓ 电子居板间 ✓ "
      "u(T/8)=+U₀>0 驱电子向A（与已产图乙同参 T=2、U₀=1）✓")

fig, ax = plt.subplots(figsize=(4.0, 3.1))
ax.set_aspect("equal"); ax.axis("off")
ax.plot([xA, xA], [ye0, ye1], lw=2.4, color="k", zorder=3)     # 板 A
ax.plot([xB, xB], [ye0, ye1], lw=2.4, color="k", zorder=3)     # 板 B
ax.text(-0.24, 1.45, "$A$", fontsize=14, ha="right")
ax.text(xB + 0.24, 1.45, "$B$", fontsize=14, ha="left")
# 电子（板间，静止）
ax.plot(xe, 1.0, "o", ms=6, mfc="k", mec="k", zorder=4)
ax.text(xe, 0.60, "$-e$", fontsize=12, ha="center")
# 板顶引线接交变电压 u（端子小圆＋u 标注；波形即图乙，不重画）
ax.plot([xA, xA], [ye1, 2.35], color="k", lw=1.4, zorder=2)
ax.plot([xA, 1.28], [2.35, 2.35], color="k", lw=1.4, zorder=2)
ax.plot([xB, xB], [ye1, 2.35], color="k", lw=1.4, zorder=2)
ax.plot([xB, 1.92], [2.35, 2.35], color="k", lw=1.4, zorder=2)
ax.plot(1.28, 2.35, "o", ms=6, mfc="white", mec="k", mew=1.3, zorder=4)
ax.plot(1.92, 2.35, "o", ms=6, mfc="white", mec="k", mew=1.3, zorder=4)
ax.text(1.6, 2.64, "$u$", fontsize=14, ha="center")
ax.set_xlim(-0.62, 3.82); ax.set_ylim(-0.12, 3.02)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\05-T1-图甲装置.png", dpi=150, facecolor="white")
plt.close(fig)

print("量产批2 写出：04-G1-题图铭牌.png ＋ 04-G1-C项符号图.png ＋ 05-T1-图甲装置.png")
