# -*- coding: utf-8 -*-
"""首批面 F1/F2：02-E7（E-11）题图＋选项D图像。
题面：正金属板—负放电极电场线分布；电子 M→N 沿直线；放电极＝x 轴原点、MN 为正方向。
答案链钉死：近放电极场线密（E_M>E_N）、E 非线性递减（A 判否）、沿 MN 电势升高（C 判否）、
Ep-x 斜率绝对值＝电场力渐减（D 判立）。
物理建模：接地导体板（镜像法）——板 x=d 处置 −Q 于原点，镜像 +Q 于 (2d,0)；板面恰为 φ=0 等势面，
场线自板面出发会聚于放电极尖端，近尖端自然变密。风格照 P1 figs 先例，150dpi。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
OUT = r"C:\提示词\工作区\_tmpP2图产0914"
CYAN = "#29B6F6"

d = 1.0
def Efield(p):
    x, y = p
    r1 = np.hypot(x, y)                      # 至放电极（−Q）
    dx, dy = x - 2 * d, y
    r2 = np.hypot(dx, dy)                    # 至镜像（+Q）
    return np.array([-x / r1**3 + dx / r2**3, -y / r1**3 + dy / r2**3])

def trace(seed_y):
    p = np.array([d, seed_y], float)
    pts = [p.copy()]
    for _ in range(4000):
        k1 = Efield(p); n1 = np.linalg.norm(k1)
        if n1 == 0: break
        k1 /= n1
        k2 = Efield(p + 0.004 * k1); k2 /= np.linalg.norm(k2)
        k3 = Efield(p + 0.0025 * k1 + 0.0025 * k2); k3 /= np.linalg.norm(k3)
        step = 0.004 if np.hypot(*p) > 0.25 else 0.0012
        p = p + step / 3 * (k1 + 2 * k2 + k3)
        pts.append(p.copy())
        if np.hypot(*p) < 0.075 or p[0] < -0.02:
            break
    return np.array(pts)

# —— 题-图-答三方一致性自核（编码化）——
Ex = lambda x: 1.0 / x**2 - 1.0 / (2 * d - x)**2      # 轴线上场强幅值（x<d）
M, N = 0.28, 0.72
assert Ex(M) > Ex(N) > 0, "判据崩：E_M 不大于 E_N（疏密→答案链）"
xs = np.linspace(0.15, 0.95, 200)
assert np.all(np.diff(Ex(xs)) < 0), "E 沿 x 非单调递减"
mid = 0.5 * (Ex(M) + Ex(N))
assert abs(Ex(0.5) - mid) / mid > 0.02, "E-x 非线性未体现（A 判据）"
phi = lambda x: -1.0 / x + 1.0 / (2 * d - x)
assert phi(N) > phi(M), "沿 MN 电势未升高（C 判否依据）"
lines = {sy: trace(sy) for sy in (0.28, 0.55, 0.85, 1.15, 1.38)}
for sy, arr in lines.items():
    assert np.hypot(*arr[-1]) < 0.09, f"场线 y={sy} 未会聚放电极"
    assert abs(arr[0][0] - d) < 1e-9, "场线起点不在板面"
print("02-E7 自核：E_M=%.2f>E_N=%.2f ✓ 非线性偏差%.0f%% ✓ φ_N>φ_M ✓ 场线5+5+轴会聚 ✓"
      % (Ex(M), Ex(N), abs(Ex(0.5) - mid) / mid * 100))

# ---------- F1 题图 ----------
fig, ax = plt.subplots(figsize=(4.9, 3.6))
ax.set_aspect("equal"); ax.axis("off")
for sy, arr in lines.items():
    for sgn in (+1, -1):
        a = arr.copy(); a[:, 1] *= sgn
        ax.plot(a[:, 0], a[:, 1], color="k", lw=1.1, zorder=2)
ax.plot([0.05, 0.93], [0, 0], color="k", lw=1.1, zorder=2)     # 轴上那根场线
# 金属板（右，白底黑框竖板）
ax.add_patch(plt.Rectangle((d - 0.035, -1.5), 0.07, 3.0, facecolor="white",
                           edgecolor="k", lw=1.6, zorder=4))
ax.text(d, 1.66, "金属板（＋）", ha="center", fontsize=11)# 放电极（左，实心尖锥，尖端在原点）
ax.add_patch(plt.Polygon([[-0.58, -0.075], [-0.58, 0.075], [-0.015, 0]],
                         closed=True, facecolor="k", zorder=4))
ax.text(-0.30, -0.34, "放电极（－）", ha="center", fontsize=11)
# x 轴（原点＝放电极尖端，MN 为正方向）
ax.annotate("", xy=(0.94, 0), xytext=(0.06, 0),
            arrowprops=dict(arrowstyle="->", color="k", lw=1.0), zorder=3)
ax.text(0.86, 0.16, "$x$", fontsize=13)
for px, lab in [(M, "$M$"), (N, "$N$")]:
    ax.plot([px], [0], "k.", ms=5, zorder=5)
    ax.text(px, -0.52, lab, ha="center", fontsize=13)
ax.set_xlim(-0.85, 1.55); ax.set_ylim(-1.75, 1.95)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\02-E7-题图.png", dpi=150, facecolor="white")
plt.close(fig)

# ---------- F2 选项D：E_p-x 图线（斜率渐缓递减） ----------
Eps = lambda x: 4.0 - 3.2 * (1 - np.exp(-x / 0.9))
xx = np.linspace(0, 3, 400)
sl = np.abs(3.2 / 0.9 * np.exp(-xx / 0.9))
assert np.all(np.diff(sl) < 0), "Ep-x 斜率绝对值未渐减（D 判据）"
assert np.all(np.diff(Eps(xx)) < 0), "Ep 未递减"
fig, ax = plt.subplots(figsize=(3.4, 2.9))
ax.annotate("", xy=(3.35, 0), xytext=(-0.15, 0),
            arrowprops=dict(arrowstyle="->", color="k", lw=1.0))
ax.annotate("", xy=(0, 4.6), xytext=(0, -0.15),
            arrowprops=dict(arrowstyle="->", color="k", lw=1.0))
ax.plot(xx, Eps(xx), color="k", lw=1.7)
ax.text(3.32, -0.52, "$x$", fontsize=12)
ax.text(-0.42, 4.42, "$E_p$", fontsize=13)
ax.set_xlim(-0.6, 3.7); ax.set_ylim(-0.8, 4.9)
ax.axis("off")
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\02-E7-选项D-Ep-x.png", dpi=150, facecolor="white")
plt.close(fig)
print("F1/F2 写出：02-E7-题图.png ＋ 02-E7-选项D-Ep-x.png（斜率渐减核 ✓）")
