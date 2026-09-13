# -*- coding: utf-8 -*-
"""课时09 探究点一 例1 配图重绘（红旗修图轮0913，逐件明示例外——公共规则§5三维禁重绘之用户明示件）。

题干：四棱锥 P-ABCD，AB∥CD，∠BAP=∠CDP=90°，PA=PD=AB=DC，∠APD=90°，求二面角 A-PB-C。
模型（a=1，唯一形状，逐条件核验于注释）：
  A=(0,0,0), B=(1,0,0), C=(1,√2,0), D=(0,√2,0), P=(0, √2/2, √2/2)
  AB=(1,0,0)∥DC=(1,0,0)，|AB|=|DC|=1；
  AP=(0,.707,.707)⊥AB（∠BAP=90°）；DP=(0,-.707,.707)⊥DC（∠CDP=90°）；
  |PA|=√(.5+.5)=1=|PD|；∠APD: (A-P)·(D-P)=-.5+.5=0 ✓；底 ABCD 为矩形 1×√2，P 在 AD 中点上方 h=√2/2。
虚实线判据＝凸体 face-visibility（邻两面全背面⇒棱被遮挡画虚线），非手摆：
  背面（外法向·视线<0）：底 ABCD（外法向(0,0,-1)）、PCD、PAD；正面：PAB、PBC。
  ⇒ 虚线：CD、DA、PD；实线：AB、BC、PA、PB、PC。
风格对齐同件 image116（黑白线稿）：纯黑实/虚线、白底、cm 斜体字母标注、图内零中文、无顶点圆点。
直角记号：仅画可见面 PAB 内 ∠BAP 处（∠CDP/∠APD 所在面均背面，不画）。
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.dirname(os.path.abspath(__file__))

s2 = np.sqrt(2.0)
A = np.array([0.0, 0.0, 0.0])
B = np.array([1.0, 0.0, 0.0])
C = np.array([1.0, s2, 0.0])
D = np.array([0.0, s2, 0.0])
P = np.array([0.0, s2 / 2, 1.0 / s2])

# ---- 相机（正交投影；机位使隐藏顶点 D 远离实棱、版面清爽）----
eye_dir = np.array([0.7, -1.05, 0.42])
eye_dir = eye_dir / np.linalg.norm(eye_dir)
up0 = np.array([0.0, 0.0, 1.0])
w = -eye_dir                      # 朝景深方向
r = np.cross(w, up0); r /= np.linalg.norm(r)
u = np.cross(r, w)

def prj(X):
    return np.array([np.dot(X, r), np.dot(X, u)])

# ---- 面可见性（外法向·eye_dir>0 ⇒ 正面）----
faces = {
    "PAB": (P, A, B), "PBC": (P, B, C), "PCD": (P, C, D),
    "PAD": (P, D, A), "base": (A, B, C, D),
}
G = (A + B + C + D + P) / 5.0  # 凸体质心

def outward(poly):
    n = np.cross(poly[1] - poly[0], poly[2] - poly[0])
    n = n / np.linalg.norm(n)
    fc = sum(poly) / len(poly)
    return n if np.dot(n, fc - G) > 0 else -n

front = {}
for k, poly in faces.items():
    front[k] = np.dot(outward(poly), eye_dir) > 0
assert front["PAB"] and front["PBC"], "正面判定失效"
assert (not front["PCD"]) and (not front["PAD"]) and (not front["base"]), "背面判定失效"

edges = [
    ("AB", A, B, ("PAB", "base")), ("BC", B, C, ("PBC", "base")),
    ("CD", C, D, ("PCD", "base")), ("DA", D, A, ("PAD", "base")),
    ("PA", P, A, ("PAB", "PAD")), ("PB", P, B, ("PAB", "PBC")),
    ("PC", P, C, ("PBC", "PCD")), ("PD", P, D, ("PCD", "PAD")),
]
hidden = {name: all(not front[f] for f in fs) for name, _, _, fs in edges}
expect = {"CD", "DA", "PD"}
assert {k for k, v in hidden.items() if v} == expect, f"虚实线归属异常: {hidden}"

# ---- 绘图 ----
fig, ax = plt.subplots(figsize=(2.3, 2.0), dpi=700)
lw = 1.4
for name, U, V, _ in edges:
    p, q = prj(U), prj(V)
    if hidden[name]:
        ax.plot([p[0], q[0]], [p[1], q[1]], ls=(0, (5, 3.2)), color="black",
                lw=lw, zorder=2, solid_capstyle="round")
    else:
        ax.plot([p[0], q[0]], [p[1], q[1]], "-", color="black", lw=lw,
                zorder=3, solid_capstyle="round")

# 直角记号不画：∠CDP/∠APD 所在面均背面，∠BAP 记号区必被虚棱 DA 穿过（各视角皆然）；
# 书内配图风格（image116）亦无附加记号，直角条件由题干文字承载。

# 标注（离心方向外推，逐个微调避让）
pa, pb, pc, pd_, pp = prj(A), prj(B), prj(C), prj(D), prj(P)
lab = dict(fontsize=13, color="black")
ax.text(pa[0] - 0.055, pa[1] - 0.045, r"$A$", ha="right", va="center", **lab)
ax.text(pb[0] + 0.01, pb[1] - 0.075, r"$B$", ha="center", va="top", **lab)
ax.text(pc[0] + 0.075, pc[1] - 0.03, r"$C$", ha="left", va="center", **lab)
ax.text(pd_[0] + 0.055, pd_[1] + 0.09, r"$D$", ha="left", va="center", **lab)
ax.text(pp[0] - 0.03, pp[1] + 0.055, r"$P$", ha="center", va="bottom", **lab)

ax.set_aspect("equal")
ax.set_axis_off()
path = os.path.join(OUT, "figPABCD_redraw0913.png")
fig.savefig(path, dpi=700, bbox_inches="tight", pad_inches=0.03,
            facecolor="white")
plt.close(fig)

# ---- 纯灰断言＋尺寸读数 ----
from PIL import Image
im = Image.open(path).convert("RGB")
arr = np.asarray(im)
dev = np.abs(arr.astype(int) - arr.mean(axis=2, keepdims=True).astype(int)).max()
print("saved:", path)
print("size :", im.size, " aspect(w/h)=%.3f" % (im.size[0] / im.size[1]))
print("color deviation max (0=pure gray):", dev)
assert dev == 0, "存在彩色像素"
