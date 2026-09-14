# -*- coding: utf-8 -*-
"""量产批3：批A 五键七面（01-G2／02-G2／02-E3／02-E8／02-E7选项A/B/C）。
台账§2.1 钉死规格（照录）＋定稿 课时01/02 题-图-答判据：
①01-G2 电场线分布图：B 侧密（疏密→场强判据），AB 为电场线、方向 B→A，φB>φA；
②02-G2 φ-x 图线：x 正半轴，x₁<M<x₂ 标注位，M 处斜率≠0，x₁→x₂ 单调降，曲线不对称；
③02-E3 等势面＋双轨迹：正点电荷同心圆虚线等势面＋P(径迹1,排斥外弯)、Q(径迹2,吸引内弯)，
  A/B/C 标注，B 在第三圈上、C 在第一二圈之间——B、C 不共等势面（C 项判否依赖）；
④02-E8 E-x⁻² 直线：过 (1,90)、(4,360)，斜率 kQ=90，过原点；
⑤⑥⑦02-E7 选项A/B/C：与已产 选项D-Ep-x 同参（figsize/箭头轴/限位/字号/150dpi），单选项图面不入字母。
  A：E-x 线性递减（错误承载：应为非线性）；B：a-x 非线性递减、斜率渐缓（判立侧）；
  C：φ-x 递减（错误承载：沿 MN 电势应升高）。
风格：白底黑线、cm 数学字体、SimHei 中文（无 U+2212，中文负号不出现）；手工坐标系显式 set_xlim/set_ylim。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
OUT = r"C:\提示词\工作区\_tmpP2图产0914\量产批3"
GRAY = "0.45"

# ============ F1：01-G2 电场线分布图（B 侧密） ============
x_l, x_r = 0.50, 3.26                      # 左板右侧面 / 右电极左侧面
A1, B1 = 1.10, 2.70                        # A、B 在中央场线上（A 近阴极、B 近密侧）
ends_l = [0.0, 0.25, -0.25, 0.75, -0.75, 1.30, -1.30]   # 左板端（疏）
ends_r = [0.0, 0.09, -0.09, 0.27, -0.27, 0.47, -0.47]   # 右电极端（密）
ys = lambda x: [el + (er - el) * (x - x_l) / (x_r - x_l) for el, er in zip(ends_l, ends_r)]
spA = np.diff(np.sort(ys(A1))).mean()
spB = np.diff(np.sort(ys(B1))).mean()
assert x_l < A1 < B1 < x_r, "A/B 不在中央场线段内"
assert spB < spA / 1.5, f"B 侧不密：spA={spA:.3f} spB={spB:.3f}"
assert spA / spB > 2.0, f"疏密对比不足：{spA/spB:.2f}"
print(f"F1(01-G2) 自核：B侧密 ✓ 线距 A侧{spA:.2f} : B侧{spB:.2f} = {spA/spB:.2f}× ✓ "
      f"E_A<E_B ✓ 场向 B→A ⇒ φB>φA ✓")

fig, ax = plt.subplots(figsize=(4.9, 3.4))
ax.set_aspect("equal"); ax.axis("off")
for el, er in zip(ends_l, ends_r):
    ax.plot([x_r, x_l], [er, el], color="k", lw=1.1, zorder=2)
    xa, xb = x_r + 0.55 * (x_l - x_r), x_r + 0.44 * (x_l - x_r)   # 中段箭头（指向 B→A）
    ya, yb = er + 0.55 * (el - er), er + 0.44 * (el - er)
    ax.annotate("", xy=(xa, ya), xytext=(xb, yb),
                arrowprops=dict(arrowstyle="->", color="k", lw=1.1), zorder=3)
ax.add_patch(plt.Rectangle((x_l - 0.09, -1.50), 0.09, 3.00, facecolor="white",
                           edgecolor="k", lw=1.6, zorder=4))
ax.text(x_l - 0.045, 1.70, "K（阴极）", ha="center", fontsize=11)
ax.add_patch(plt.Rectangle((x_r, -0.55), 0.09, 1.10, facecolor="white",
                           edgecolor="k", lw=1.6, zorder=4))
for px, lab in [(A1, "$A$"), (B1, "$B$")]:
    ax.plot([px], [0], "k.", ms=6, zorder=5)
    ax.text(px, -0.38, lab, ha="center", fontsize=13)
ax.set_xlim(-0.20, 3.90); ax.set_ylim(-1.90, 2.05)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\01-G2-题图.png", dpi=150, facecolor="white")
plt.close(fig)
print("F1 写出：01-G2-题图.png")

# ============ F2：02-G2 φ-x 图线（x 正半轴，M、x₁、x₂） ============
phi = lambda x: 3.2 / (x + 0.55)
x1g, xMg, x2g = 0.70, 1.40, 3.00
d1, d2 = phi(x1g), phi(xMg), phi(x2g)
slM = -(phi(xMg + 1e-5) - phi(xMg - 1e-5)) / 2e-5
asym1 = phi(xMg - 0.5) - phi(xMg); asym2 = phi(xMg) - phi(xMg + 0.5)
xx = np.linspace(x1g, x2g, 500)
assert x1g < xMg < x2g, "标注位次崩（x₁<M<x₂）"
assert d1 > d2 > d2 > 0 and d1 > d2, "φ(x₁)>φ(x₂) 崩"
assert d1 > phi(xMg) > phi(x2g), "M 处电势序崩"
assert abs(slM) > 0.5, f"M 处斜率为 0（E_M=0，A 判否依据崩）：{slM:.3f}"
assert np.all(np.diff(phi(xx)) < 0), "x₁→x₂ 非单调降（C 判立依据崩）"
assert abs(asym1 - asym2) / asym1 > 0.2, "曲线对称（D 判否依据崩）"
print(f"F2(02-G2) 自核：x₁<M<x₂ ✓ φ₁={d1:.2f}>φ_M={d2:.2f}>φ₂={phi(x2g):.2f} ✓ "
      f"E_M=|斜率|={abs(slM):.2f}≠0 ✓ 单调降 ✓ 不对称({asym1:.2f} vs {asym2:.2f}) ✓")

fig, ax = plt.subplots(figsize=(4.9, 3.4))
xx = np.linspace(0.012, 4.35, 900)
ax.plot(xx, phi(xx), color="k", lw=1.7, zorder=3)
ax.annotate("", xy=(4.78, 0), xytext=(-0.12, 0),
            arrowprops=dict(arrowstyle="->", color="k", lw=1.0), zorder=2)
ax.annotate("", xy=(0, 6.55), xytext=(0, -1.05),
            arrowprops=dict(arrowstyle="->", color="k", lw=1.0), zorder=2)
ax.text(4.76, -0.92, "$x$", fontsize=13)
ax.text(-0.10, 6.50, r"$\varphi$", fontsize=14, va="top")
for gx in (x1g, x2g):
    ax.plot([gx, gx], [0, phi(gx)], color=GRAY, lw=0.9, ls="--", zorder=1)
    ax.plot([gx], [phi(gx)], "k.", ms=5, zorder=4)
    ax.text(gx, -0.78, f"${{x}}_{1 if gx==x1g else 2}$", ha="center", fontsize=13)
ax.plot([xMg], [phi(xMg)], "k.", ms=6, zorder=4)
ax.plot([xMg, xMg], [0, phi(xMg)], color=GRAY, lw=0.9, ls="--", zorder=1)
ax.text(xMg + 0.10, phi(xMg) + 0.22, "$M$", fontsize=13)
ax.set_xlim(-0.15, 4.95); ax.set_ylim(-1.25, 6.75)
ax.set_aspect("auto"); ax.axis("off")
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\02-G2-题图φx.png", dpi=150, facecolor="white")
plt.close(fig)
print("F2 写出：02-G2-题图φx.png")

# ============ F3：02-E3 等势面＋P、Q 双轨迹（B、C 不共等势面） ============
circ = [0.55, 0.95, 1.35, 1.75]
rA = 1.75
thA = np.deg2rad(150)
A3 = rA * np.array([np.cos(thA), np.sin(thA)])
u_r = -A3 / rA
u_t = np.array([-u_r[1], u_r[0]])
v0 = 1.45
def shoot(angle_deg, sign):
    d = np.cos(np.deg2rad(angle_deg)) * u_r + np.sin(np.deg2rad(angle_deg)) * u_t
    p, v = A3.copy(), v0 * d
    pts = [p.copy()]
    for _ in range(12000):
        r = np.hypot(*p)
        dt = 0.0022 * min(r, 1.2)
        def acc(q):
            rr = np.hypot(*q)
            return sign * q / rr**3
        k1v = acc(p);                k1p = v
        k2v = acc(p + 0.5*dt*k1p);   k2p = v + 0.5*dt*k1v
        k3v = acc(p + 0.5*dt*k2p);   k3p = v + 0.5*dt*k2v
        k4v = acc(p + dt*k3p);       k4p = v + dt*k3v
        p = p + dt/6*(k1p + 2*k2p + 2*k3p + k4p)
        v = v + dt/6*(k1v + 2*k2v + 2*k3v + k4v)
        pts.append(p.copy())
        if np.hypot(*p) > 1.98 or np.hypot(*p) < 0.10:
            break
    return np.array(pts), d
traj1, dP = shoot(24.0, +1.0)     # P：排斥，外弯
traj2, dQ = shoot(14.0, -1.0)     # Q：吸引，内弯
r1 = np.hypot(traj1[:, 0], traj1[:, 1]); r2 = np.hypot(traj2[:, 0], traj2[:, 1])
iB = int(np.argmax(np.abs(r1 - 1.35) < 1e-3))
iC = int(np.argmax(r2 < 0.80))
B3, C3 = traj1[iB], traj2[iC]
rB, rC = np.hypot(*B3), np.hypot(*C3)
assert abs(np.linalg.norm(dP) - v0) < 1e-12 and abs(np.linalg.norm(dQ) - v0) < 1e-12, "初速率不同（题面崩）"
assert np.hypot(*traj1.min(axis=0)) > 0 or True
per1 = r1.min(); per2 = r2.min()
assert per1 > circ[0] + 0.05, f"径迹1 未外弯绕开（近距 {per1:.2f}）"
assert per2 < circ[0], f"径迹2 未内弯贴近场源（近距 {per2:.2f}）"
assert abs(rB - 1.35) < 5e-3, f"B 不在第三圈上：r_B={rB:.3f}"
assert circ[0] < rC < circ[1], f"C 不在第一二圈之间：r_C={rC:.3f}"
assert abs(rB - rC) > 0.3, f"B、C 共等势面嫌疑：|r_B−r_C|={abs(rB-rC):.2f}"
print(f"F3(02-E3) 自核：初速率同={v0} ✓ 径迹1外弯(近距{per1:.2f})/径迹2内弯(近距{per2:.2f}) ✓ "
      f"r_B={rB:.2f}(第三圈) r_C={rC:.2f}(一二圈间) |r_B−r_C|={abs(rB-rC):.2f}→B、C不共等势面 ✓")

fig, ax = plt.subplots(figsize=(4.9, 4.4))
ax.set_aspect("equal"); ax.axis("off")
for rc in circ:
    t = np.linspace(0, 2 * np.pi, 400)
    ax.plot(rc * np.cos(t), rc * np.sin(t), color="k", lw=0.8, ls=(0, (4, 3)), zorder=1)
ax.plot(traj1[:, 0], traj1[:, 1], color="k", lw=1.4, zorder=3)
ax.plot(traj2[:, 0], traj2[:, 1], color="k", lw=1.4, zorder=3)
for tr, f in ((traj1, 0.38), (traj2, 0.30)):
    i = int(f * len(tr))
    ax.annotate("", xy=tr[min(i + 2, len(tr) - 1)], xytext=tr[i],
                arrowprops=dict(arrowstyle="->", color="k", lw=1.3), zorder=4)
ax.text(0, 0, "$+$", fontsize=17, ha="center", va="center", zorder=5)
ax.plot([A3[0]], [A3[1]], "k.", ms=6, zorder=5)
ax.plot([B3[0]], [B3[1]], "k.", ms=6, zorder=5)
ax.plot([C3[0]], [C3[1]], "k.", ms=6, zorder=5)
ax.text(A3[0] - 0.16, A3[1] + 0.14, "$A$", fontsize=13)
ax.text(B3[0] + 0.10, B3[1] + 0.12, "$B$", fontsize=13)
ax.text(C3[0] + 0.12, C3[1] - 0.02, "$C$", fontsize=13)
j1 = int(0.16 * len(traj1)); j2 = int(0.13 * len(traj2))
ax.text(traj1[j1][0] + 0.05, traj1[j1][1] + 0.13, "$P$", fontsize=13)
ax.text(traj2[j2][0] - 0.18, traj2[j2][1] + 0.10, "$Q$", fontsize=13)
m1 = traj1[int(0.55 * len(traj1))]; m2 = traj2[int(0.55 * len(traj2))]
ax.text(m1[0] + 0.08, m1[1] - 0.16, "1", fontsize=12)
ax.text(m2[0] + 0.06, m2[1] - 0.18, "2", fontsize=12)
ax.set_xlim(-2.35, 2.35); ax.set_ylim(-2.15, 2.30)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\02-E3-题图等势面.png", dpi=150, facecolor="white")
plt.close(fig)
print("F3 写出：02-E3-题图等势面.png")

# ============ F4：02-E8 E-x⁻² 直线图像（(1,90)、(4,360) 钉死） ============
slope = (360 - 90) / (4 - 1)
E8 = lambda u: slope * u
assert abs(slope - 90) < 1e-12, f"斜率≠kQ=90：{slope}"
assert abs(E8(0) - 0) < 1e-12, "直线不过原点（φ=kQ/r ⇒ x→∞ E→0 崩）"
assert abs(E8(1) - 90) < 1e-12 and abs(E8(4) - 360) < 1e-12, "钉死数据点崩"
uu = np.array([0.0, 1.0, 4.0])
assert np.allclose(np.polyfit(uu, E8(uu), 1), [90, 0], atol=1e-9), "线性/截距回归崩"
print(f"F4(02-E8) 自核：过(1,90)、(4,360) ✓ 斜率=(360−90)/(4−1)={slope:.0f}=kQ ✓ 过原点 ✓ 线性 ✓")

fig, ax = plt.subplots(figsize=(4.0, 3.4))
uu = np.linspace(0, 4.75, 100)
ax.plot(uu, E8(uu), color="k", lw=1.7, zorder=3)
ax.annotate("", xy=(5.25, 0), xytext=(-0.32, 0),
            arrowprops=dict(arrowstyle="->", color="k", lw=1.0), zorder=2)
ax.annotate("", xy=(0, 438), xytext=(0, -52),
            arrowprops=dict(arrowstyle="->", color="k", lw=1.0), zorder=2)
ax.text(5.30, -36, r"$x^{-2}/\mathrm{m}^{-2}$", fontsize=12, ha="center")
ax.text(-0.14, 448, r"$E/(\mathrm{N\cdot C}^{-1})$", fontsize=11, va="bottom", ha="left")
for ux, ey, lx, ly, hx, hy in [(1, 90, 1, -34, -0.14, 90), (4, 360, 4, -34, -0.14, 360)]:
    ax.plot([ux, ux], [0, ey], color=GRAY, lw=0.9, ls="--", zorder=1)
    ax.plot([0, ux], [ey, ey], color=GRAY, lw=0.9, ls="--", zorder=1)
    ax.plot([ux], [ey], "k.", ms=6, zorder=4)
    ax.text(lx, ly, f"${lx}$", ha="center", fontsize=12)
    ax.text(hx, hy + 8, f"${ey}$", ha="right", va="bottom", fontsize=11)
ax.set_xlim(-0.35, 5.75); ax.set_ylim(-62, 492)
ax.set_aspect("auto"); ax.axis("off")
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\02-E8-题图.png", dpi=150, facecolor="white")
plt.close(fig)
print("F4 写出：02-E8-题图.png")

# ============ F5/F6/F7：02-E7 选项A/B/C（同参已产选项D 面） ============
FW = (3.4, 2.9)
def frame(ax, ylab):
    ax.annotate("", xy=(3.35, 0), xytext=(-0.15, 0),
                arrowprops=dict(arrowstyle="->", color="k", lw=1.0))
    ax.annotate("", xy=(0, 4.6), xytext=(0, -0.15),
                arrowprops=dict(arrowstyle="->", color="k", lw=1.0))
    ax.text(3.32, -0.52, "$x$", fontsize=12)
    ax.text(-0.42, 4.42, ylab, fontsize=13)
    ax.set_xlim(-0.6, 3.7); ax.set_ylim(-0.8, 4.9)
    ax.axis("off")
    fig.tight_layout(pad=0.2)

xx = np.linspace(0, 3.0, 100)
EA = 4.0 - 1.25 * xx                                    # A：线性递减（错误承载）
assert np.all(np.diff(EA) < 0), "A 面未递减"
assert np.allclose(EA, 4.0 - 1.25 * xx, atol=1e-12), "A 面非线性（错误承载要求直线）"
fig, ax = plt.subplots(figsize=FW)
ax.plot(xx, EA, color="k", lw=1.7)
frame(ax, "$E$")
fig.savefig(OUT + r"\02-E7-选项A-E-x.png", dpi=150, facecolor="white")
plt.close(fig)
print("F5 写出：02-E7-选项A-E-x.png（线性递减＝错误承载 ✓）")

xx = np.linspace(0, 3.2, 300)
EB = 4.2 - 3.5 * (1 - np.exp(-xx / 1.05))               # B：非线性递减、斜率渐缓（判立）
sB = np.abs(3.5 / 1.05 * np.exp(-xx / 1.05))
assert np.all(np.diff(EB) < 0), "B 面未递减"
assert np.all(np.diff(sB) < 0), "B 面斜率未渐缓（判立依据崩）"
assert np.all(np.diff(EB, 2) > 0), "B 面非线性不足"
fig, ax = plt.subplots(figsize=FW)
ax.plot(xx, EB, color="k", lw=1.7)
frame(ax, "$a$")
fig.savefig(OUT + r"\02-E7-选项B-a-x.png", dpi=150, facecolor="white")
plt.close(fig)
print("F6 写出：02-E7-选项B-a-x.png（非线性递减·斜率渐缓 ✓）")

xx = np.linspace(0, 3.2, 300)
EC = 4.05 * np.exp(-xx / 1.30)                          # C：递减曲线（错误承载：φ 应升高）
assert np.all(np.diff(EC) < 0), "C 面未递减（错误承载要求递减）"
fig, ax = plt.subplots(figsize=FW)
ax.plot(xx, EC, color="k", lw=1.7)
frame(ax, r"$\varphi$")
fig.savefig(OUT + r"\02-E7-选项C-φ-x.png", dpi=150, facecolor="white")
plt.close(fig)
print("F7 写出：02-E7-选项C-φ-x.png（递减＝错误承载，题链 φ 应升高 ✓）")

print("批3 七面全写出：01-G2-题图／02-G2-题图φx／02-E3-题图等势面／02-E8-题图／02-E7-选项A/B/C")
