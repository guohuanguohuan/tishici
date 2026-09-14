# -*- coding: utf-8 -*-
"""首批面 F5：05-G2（债行〔05-G2〕1处）三板几何图。
题面：三块平行带电薄板 A、B、C 中央各开小孔，孔位于 O、M、P；电子由 O 静止释放恰至 P；
C 板左移至 P′。答案 D 判据：三板脱离电源、C 左移⟹B、C 间距减小⟹U_MP′＜U_MP⟹电子过 P′ 继续前进。
钉死规格（台账§2.3）：三板间距与小孔对齐关系——O、M、P（含 P′）同轴共线；P′ 位于 M、P 之间；
C 左移后 B–C 间距减小。风格照 P1 figs 先例（青虚线辅助、尺寸箭头），150dpi。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
OUT = r"C:\提示词\工作区\_tmpP2图产0914"
CYAN = "#29B6F6"

xa, xb, xc, xcp = 0.0, 1.5, 2.7, 2.2      # A、B、C 及 C 左移位（P′）
H, hO = 1.3, 0.17                          # 板半高、孔半宽
# —— 题-图-答三方一致性自核（编码化）——
assert xa < xb < xcp < xc, "对齐关系崩：P′ 应位于 M、P 之间（C 左移）"
assert (xc - xb) > (xcp - xb), "C 左移后 B–C 间距未减小（U_MP′＜U_MP 判据崩）"
print("05-G2 自核：O/M/P/P′ 同轴 y=0 ✓ P′∈(M,P) ✓ d_BC: %.2f→%.2f 减小 ✓"
      % (xc - xb, xcp - xb))

fig, ax = plt.subplots(figsize=(4.9, 3.2))
ax.set_aspect("equal"); ax.axis("off")
def plate(xx, style="-", label=None, lx=None):
    for y0, y1 in [(hO, H), (-H, -hO)]:
        ax.plot([xx, xx], [y0, y1], color="k", lw=2.3, linestyle=style, zorder=4)
    if label:
        ax.text(lx if lx is not None else xx, H + 0.16, label,
                ha="center", fontsize=13, style="normal")
plate(xa, label="$A$")
plate(xb, label="$B$")
plate(xc, label="$C$")
plate(xcp, style="--", label="$C'$")       # 左移后位置（青虚线示平移）
# 小孔点 O、M、P、P′（同轴；标签置孔点左侧，避让板线）
for xx, lab in [(xa, "$O$"), (xb, "$M$"), (xcp, "$P'$"), (xc, "$P$")]:
    ax.plot(xx, 0, "k.", ms=6, zorder=5)
    ax.text(xx - 0.13, 0.0, lab, ha="right", va="center", fontsize=13)
# 电子由 O 静止释放（箭头＋标注）
ax.annotate("", xy=(0.52, 0), xytext=(0.06, 0),
            arrowprops=dict(arrowstyle="-|>", color="k", lw=1.4))
ax.text(0.29, 0.16, "$e$", ha="center", fontsize=12)
# 间距尺寸线（P1 先例：青色双箭头）
for x0, x1, lab in [(xa, xb, "$d_1$"), (xb, xcp, "$d_2$")]:
    ax.annotate("", xy=(x1, -H - 0.30), xytext=(x0, -H - 0.30),
                arrowprops=dict(arrowstyle="<->", color=CYAN, lw=1.3))
    ax.text((x0 + x1) / 2, -H - 0.62, lab, ha="center", fontsize=12)
ax.set_xlim(-0.45, 3.25); ax.set_ylim(-2.25, 1.75)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\05-G2-三板几何.png", dpi=150, facecolor="white")
print("F5 写出：05-G2-三板几何.png")
