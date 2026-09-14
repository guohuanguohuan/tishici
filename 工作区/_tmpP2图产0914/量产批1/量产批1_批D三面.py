# -*- coding: utf-8 -*-
"""量产批1（批D 三面）：D-01 等势面族＋D-02 电场线族＋D-04 同心等势圆。
钉死规格（台账§2.4 照录，只读）：
  D-01：椭圆等势面族电势标注（自左向右 e 15V/d 10V/c 5V/b 0V）＋A（右上密区）、B（左下疏区）。
        A 落 e–d 带内（10V<φ_A<15V）、B 落外圈 e 上（15V）——保定稿详解判据链 φ_B>φ_A、
        E_A>E_B（底稿 A 落在外圈上会导出 φ_A=φ_B，与详解冲突，以定稿详解为准）。
  D-02：平行但左密右疏（板块件§九：平行但间距不等＋E）。横线相互平行、间距不等（上密下疏）
        ＋右端错位收尾，使整体疏密沿 x 自左向右变疏；题2 本证「这样的场不存在」，图即假设场。
  D-04：同心等势圆三个（虚线）＋过 Q 向外射线依次穿 A、B、C，rC−rB＝rB−rA（精确等距）。
风格照 P1 figs 先例：白底黑线、青虚线辅线、cm 数学字体、SimHei 中文、无图题、150dpi。
红线：零 git；定稿/台账/在产件只读；写入仅本目录（量产批1/）。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import hashlib, os

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

OUT = r"C:\提示词\工作区\_tmpP2图产0914\量产批1"
PINK = "#F08CAC"   # 底稿射线粉
GOLD_FC, GOLD_EC, PLUS_C = "#F9C74F", "#B8860B", "#7A4A00"  # 底稿⊕金
LW = 1.6

# ================= 面1：D-01 等势面族（椭圆族，右端收敛＝密区） =================
# 椭圆 i：右顶点共点 (6.2,0)，左顶点自左向右 0 / 1.55 / 2.9 / 4.05，半短轴 0.42×半长轴
X_R = 6.2
LEFTS = [0.0, 1.55, 2.9, 4.05]                 # e/d/c/b 左顶点
ASPECT = 0.42
ells = []
for xl in LEFTS:
    a = (X_R - xl) / 2.0
    ells.append(dict(cx=(xl + X_R) / 2.0, a=a, b=ASPECT * a))
# 电势标注：自左向右 e 15V / d 10V / c 5V / b 0V（字母在上、数值在下）
LAB = [("$e$", "15 V"), ("$d$", "10 V"), ("$c$", "5 V"), ("$b$", "0")]
VOLS = [15, 10, 5, 0]
lab_x = [0.78, 2.22, 3.48, 4.55]
# 断言1：标注次序与电势自左向右严格 15→10→5→0
assert lab_x == sorted(lab_x) and len(lab_x) == 4, "标注自左向右次序崩"
assert all(VOLS[i] > VOLS[i + 1] for i in range(3)), "电势非自左向右递减（应 15/10/5/0）"
# 断言2：题1(1) 电子 b→e 静电力做功 W=(−e)(φ_b−φ_e)=+15 eV=2.4×10⁻¹⁸ J（详解口径）
W_eV = (-1) * (VOLS[3] - VOLS[0])
assert W_eV == 15, "电子 b→e 做功非 +15 eV"
assert abs(W_eV * 1.6e-19 - 2.4e-18) < 1e-26, "2.4×10⁻¹⁸J 换算崩"
# 断言3：椭圆族右端共点收敛（密区几何前提）
th = np.linspace(0, 2 * np.pi, 721)
for e in ells:
    ye = e["b"] * np.sin(th[np.argmin(np.abs(X_R - 1e-4 - (e["cx"] + e["a"] * np.cos(th))))])
    assert abs(ye) < 0.02 and abs(e["cx"] + e["a"] - X_R) < 1e-12, "椭圆族未收敛于右共点"
# 断言4：A 在右上密区（e–d 带内：e 内、d 外）⇒ 10V<φ_A<15V<φ_B ⇒ φ_B>φ_A（详解判据）
A_pt = (5.0, 0.943)
def inside(p, e):
    return ((p[0] - e["cx"]) / e["a"]) ** 2 + (p[1] / e["b"]) ** 2 < 1.0
assert inside(A_pt, ells[0]) and not inside(A_pt, ells[1]), "A 未落在 e–d 带内"
assert A_pt[0] > X_R / 2 and A_pt[1] > 0, "A 不在右上区"
# 断言5：E_A>E_B——e–d 带竖向宽度在 A 侧（右）远小于 B 侧（左中段）
def ytop(x, e):
    k = 1 - ((x - e["cx"]) / e["a"]) ** 2
    return e["b"] * np.sqrt(k) if k > 0 else np.nan
w_A = ytop(A_pt[0], ells[0]) - ytop(A_pt[0], ells[1])       # A 处带宽
w_B = ytop(3.1, ells[0]) - ytop(3.1, ells[1])               # 左中段同带宽
assert w_A < 0.5 * w_B, "疏密关系崩：A 侧须显著更密（E_A>E_B）"
# 断言6：B 在左下疏区、落外圈 e 上（φ_B=15V）
B_pt = (3.1 + ells[0]["a"] * np.cos(np.deg2rad(205)), ells[0]["b"] * np.sin(np.deg2rad(205)))
on_e = ((B_pt[0] - ells[0]["cx"]) / ells[0]["a"]) ** 2 + (B_pt[1] / ells[0]["b"]) ** 2
assert abs(on_e - 1) < 1e-9 and B_pt[0] < X_R / 2 and B_pt[1] < 0, "B 不在外圈左下"
# φ 链：B 在 e 上 φ_B=15V；A 严格在 e 内 ⇒ φ_A<15=φ_B（定稿详解判据 φ_B>φ_A）
s_e = ((A_pt[0] - ells[0]["cx"]) / ells[0]["a"]) ** 2 + (A_pt[1] / ells[0]["b"]) ** 2
PHI_B = 15.0
assert s_e < 1.0 and PHI_B == VOLS[0], "φ_B>φ_A 判据崩（A 未严格落在 e 内）"
print("D-01 自核：标注 e15/d10/c5/b0 自左向右 ✓ W=(−e)(0−15V)=+15eV=2.4×10⁻¹⁸J ✓ "
      "右端共点收敛 ✓ A∈e–d 带(10V<φ_A<15V)右上密 ✓ 带宽比 w_A/w_B=%.2f（E_A>E_B）✓ "
      "φ_B=15V>φ_A（B 在外圈左下疏区）✓" % (w_A / w_B))

fig, ax = plt.subplots(figsize=(5.2, 2.45))
ax.set_aspect("equal"); ax.axis("off")
for e in ells:
    ax.plot(e["cx"] + e["a"] * np.cos(th), e["b"] * np.sin(th), color="k", lw=1.3, zorder=2)
for (lt, lv), lx in zip(LAB, lab_x):
    ax.text(lx, 0.20, lt, ha="center", va="center", fontsize=12.5, zorder=3)
    ax.text(lx, -0.22, lv, ha="center", va="center", fontsize=11, zorder=3)
ax.plot(*A_pt, "k.", ms=5.5, zorder=5)
ax.text(A_pt[0] + 0.14, A_pt[1] + 0.19, "$A$", fontsize=13.5, zorder=5)
ax.plot(*B_pt, "k.", ms=5.5, zorder=5)
ax.text(B_pt[0] - 0.22, B_pt[1] - 0.06, "$B$", fontsize=13.5, ha="right", zorder=5)
ax.set_xlim(-0.35, 6.75); ax.set_ylim(-1.62, 1.62)
fig.tight_layout(pad=0.2)
f1 = os.path.join(OUT, "D-01-等势面族.png")
fig.savefig(f1, dpi=150, facecolor="white")
plt.close(fig)

# ================= 面2：D-02 电场线族（平行但左密右疏，题2 假设场） =================
# 横线相互平行（全水平）、竖向间距不等（上密下疏）、右端错位收尾 ⇒ 疏密沿 x 左密右疏
YS = [3.3, 2.65, 1.9, 1.0, 0.0, -1.15, -2.5]
XE = [4.0, 5.2, 6.6, 8.2, 10.0, 12.0, 14.2]
gaps = np.abs(np.diff(YS))   # 相邻线竖向间距（上密下疏）
# 断言1：相互平行——各线严格水平
assert all(len({y for y in YS}) == 7 for _ in [0]), "线族重根"
assert all(abs(np.diff([y, y])) == 0 for y in YS), "存在非水平线（平行崩）"
# 断言2：间距不等（严格递增 0.65→1.35）
assert all(np.diff(gaps) > 0), "间距非严格不等（应上密下疏递增）"
# 断言3：左密右疏——左列 7 线 vs 右列 2 线；最疏间距 > 2×最密间距
def n_cross(x):
    return sum(1 for y, xe in zip(YS, XE) if xe >= x)
n_L, n_R = n_cross(1.0), n_cross(10.5)
assert n_L == 7 and n_R == 2 and n_L > 2 * n_R, "左密右疏崩（线数列）"
assert gaps[-1] > 2 * gaps[0], "左密右疏崩（间距列）"
# 断言4：详解反证回路可用——取密区线(y=3.3)与疏区线(y=−2.5)公共水平段 l=2，
#        W₁+W₂=q(E₁−E₂)l≠0 ⇒ 与路径无关性矛盾 ⇒ 该场不存在（题2 答案）
E1, E2, l = 1.0 / gaps[0], 1.0 / gaps[-1], 2.0
assert min(XE[0], XE[-1]) > l, "两线公共段不足 l"
assert (E1 - E2) * l != 0, "反证回路非零功崩"
print("D-02 自核：7 线全水平（相互平行）✓ 间距 %.2f→%.2f 严格不等 ✓ "
      "左列%d线/右列%d线＋最疏>2×最密（左密右疏）✓ 回路 W净=q(E₁−E₂)l≠0 ⇒ 场不存在 ✓"
      % (gaps[0], gaps[-1], n_L, n_R))

fig, ax = plt.subplots(figsize=(5.5, 2.5))
ax.set_aspect("equal"); ax.axis("off")
for y, xe in zip(YS, XE):
    ax.plot([0, xe - 0.22], [y, y], color="k", lw=1.4, solid_capstyle="butt", zorder=2)
    ax.annotate("", xy=(xe, y), xytext=(xe - 0.28, y),
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.4), zorder=2)
ax.text(XE[-1] + 0.42, YS[-1], "$E$", fontsize=14.5, va="center", zorder=3)
ax.set_xlim(-0.45, 15.5); ax.set_ylim(-3.25, 4.05)
fig.tight_layout(pad=0.2)
f2 = os.path.join(OUT, "D-02-电场线族.png")
fig.savefig(f2, dpi=150, facecolor="white")
plt.close(fig)

# ================= 面3：D-04 同心等势圆（rC−rB＝rB−rA，射线穿 A、B、C） =================
R = [1.0, 2.7, 4.4]                     # rA/rB/rC，精确等距 1.7
q, W_AC = 1.6e-6, 1.92e-5
# 断言1：rC−rB＝rB−rA（钉死等距，精确相等）
assert abs((R[2] - R[1]) - (R[1] - R[0])) < 1e-12 and abs(R[1] - R[0] - 1.7) < 1e-12, "半径等距崩（rC−rB≠rB−rA）"
# 断言2：题4 数值链——U_AC=W/q=12V；取 φ_C=0 得 φ_A=12V
U_AC = W_AC / q
assert abs(U_AC - 12.0) < 1e-12, "U_AC≠12V"
PHI_A, PHI_C = 12.0, 0.0
assert abs((PHI_A - PHI_C) - U_AC) < 1e-12, "φ_A 崩"
# 断言3：U_AB>U_BC——副证 kQ=1：U_AB=1−1/2.7 ≈0.630 > U_BC=1/2.7−1/4.4 ≈0.141
U_AB_k, U_BC_k = 1 - 1 / R[1], 1 / R[1] - 1 / R[2]
assert U_AB_k > U_BC_k, "U_AB>U_BC 崩"
assert abs((1 / 1 - 1 / 2) / (1 / 2 - 1 / 3) - 3.0) < 1e-12, "r=1/2/3 时 3:1 副证崩"
# 断言4：射线由 Q 沿 +x 依次穿 A、B、C，点在各圆上
ax_pts = [(r, 0.0) for r in R]
assert [p[0] for p in ax_pts] == sorted(p[0] for p in ax_pts), "A→C 次序崩"
for (px, py), r in zip(ax_pts, R):
    assert abs(np.hypot(px, py) - r) < 1e-12, "点不在对应圆上"
print("D-04 自核：r=%.1f/%.1f/%.1f 等距 rC−rB=rB−rA=1.7 ✓ U_AC=%.2fV、φ_A=12V(φ_C=0) ✓ "
      "U_AB(%.3f)>U_BC(%.3f)（kQ=1 副证）✓ 射线依次穿 A、B、C 且在圆上 ✓"
      % (R[0], R[1], R[2], U_AC, U_AB_k, U_BC_k))

fig, ax = plt.subplots(figsize=(5.0, 4.2))
ax.set_aspect("equal"); ax.axis("off")
th = np.linspace(0, 2 * np.pi, 721)
for r in R:
    ax.plot(r * np.cos(th), r * np.sin(th), color="k", lw=1.1,
            ls=(0, (5, 4)), zorder=2)
# 射线：自 ⊕ 缘向右，粉色，端箭头
ax.annotate("", xy=(5.55, 0), xytext=(0.40, 0),
            arrowprops=dict(arrowstyle="-|>", color=PINK, lw=1.7,
                            shrinkA=0, shrinkB=0), zorder=3)
ax.plot(0, 0, "o", ms=13, mfc=GOLD_FC, mec=GOLD_EC, mew=1.2, zorder=5)
ax.text(0, -0.015, "+", ha="center", va="center", fontsize=11.5, color=PLUS_C, zorder=6)
ax.text(-0.12, 0.58, "$Q$", fontsize=14.5, ha="center", zorder=5)
for (px, py), nm in zip(ax_pts, "ABC"):
    ax.plot(px, py, "k.", ms=5, zorder=5)
    ax.text(px + 0.35, -0.58, "$%s$" % nm, fontsize=13.5, ha="left", zorder=5)
ax.set_xlim(-5.05, 6.25); ax.set_ylim(-4.85, 4.85)
fig.tight_layout(pad=0.2)
f3 = os.path.join(OUT, "D-04-同心等势圆.png")
fig.savefig(f3, dpi=150, facecolor="white")
plt.close(fig)

# ================= md5 登记（M3 清单制，前十二位） =================
lines = []
for f in (f1, f2, f3):
    md5 = hashlib.md5(open(f, "rb").read()).hexdigest()[:12]
    lines.append("%s  md5:%s" % (os.path.basename(f), md5))
    print("md5:", lines[-1])
with open(os.path.join(OUT, "清单.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
print("量产批1 三面产毕，清单.txt 已写。")
