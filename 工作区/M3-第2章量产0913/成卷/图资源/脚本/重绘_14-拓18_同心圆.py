# -*- coding: utf-8 -*-
"""重绘 14-拓18（课时14 例20：两组同心圆找距离差6的点→双曲线）
源：教材 习题2-6 A1（书页156），源件无可用图（盘点页图仅节头 bar），按题面数据重绘。
自验：|rA−rB|=6 的交点逐点核对落在 x²/9−y²/16=1 上。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

A = np.array([-5.0, 0.0])   # |AB|=10
B = np.array([5.0, 0.0])
RMAX = 10                    # 半径 1..10（题面「1，2，3，⋯」开列）

fig, ax = plt.subplots(figsize=(4.6, 4.2))
th = np.linspace(0, 2 * np.pi, 361)
for r in range(1, RMAX + 1):
    ax.plot(A[0] + r * np.cos(th), r * np.sin(th), color="0.62", lw=0.6, zorder=1)
    ax.plot(B[0] + r * np.cos(th), r * np.sin(th), color="0.62", lw=0.6, zorder=1)

# 双曲线 x²/9−y²/16=1（两支）
yy = np.linspace(-7.8, 7.8, 401)
xr = 3 * np.sqrt(1 + yy**2 / 16)
ax.plot(xr, yy, color="k", lw=1.6, zorder=3)
ax.plot(-xr, yy, color="k", lw=1.6, zorder=3)

# 坐标轴（淡）
ax.axhline(0, color="0.3", lw=0.7, zorder=2)
ax.axvline(0, color="0.3", lw=0.7, zorder=2)

ax.plot(*A, "k.", ms=5); ax.plot(*B, "k.", ms=5)
ax.annotate("$A$", A, xytext=(A[0] - 0.15, 0.45), fontsize=13)
ax.annotate("$B$", B, xytext=(B[0] - 0.15, 0.45), fontsize=13)
ax.annotate("$O$", (0, 0), xytext=(-0.65, -0.75), fontsize=13)

ax.set_xlim(-16.2, 16.2); ax.set_ylim(-11.0, 11.0)
ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout(pad=0.2)

# —— 自验：|rA−rB|=6 的交点逐点落方程 ——
pts = []
for r1 in range(1, RMAX + 1):
    for r2 in range(1, RMAX + 1):
        if abs(r1 - r2) != 6:
            continue
        # 交点：到 A 距 r1、到 B 距 r2
        d = np.linalg.norm(B - A)          # 10
        x = (r1**2 - r2**2 + d**2) / (2 * d)
        h2 = r1**2 - x**2
        if h2 < 0:
            continue
        h = np.sqrt(h2)
        for s in (+1, -1):
            pts.append((x - 5.0, s * h))   # 平移：A(-5,0) 原点系 → x-5
errs = []
for (x, y) in pts:
    errs.append(abs(x**2 / 9 - y**2 / 16 - 1))
print("14-拓18 自验：交点数=%d，最大|F|=%.2e（双曲线方程 x²/9−y²/16=1）" % (len(pts), max(errs)))
assert max(errs) < 1e-9, "交点未落双曲线"
assert abs(np.linalg.norm(B - A) - 10) < 1e-12

out = r"C:\提示词\工作区\M3-第2章量产0913\成卷\图资源\14-拓18"
fig.savefig(out + ".png", dpi=300, facecolor="white")
fig.savefig(out + ".pdf", facecolor="white")
print("写出", out + ".png / .pdf")
