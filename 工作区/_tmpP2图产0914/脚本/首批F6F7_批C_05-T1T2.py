# -*- coding: utf-8 -*-
"""首批面 F6/F7：05-T1 图乙方波＋05-T2 图乙单极性方波（各取该行 1 图面；图甲装置面后续量产）。
05-T1 钉死（台账§2.3「极性正负、周期、幅值」）：u 取 φ_A−φ_B，[0,T/2) 为 +U₀（电场驱电子向 A），
幅值 U₀、周期 T；后半周 −U₀。
05-T2 钉死（「单极性方波极性」）：u∈{0, U₀}，[0,t₀) 高电平 U₀、[t₀,2t₀) 为 0，周期 2t₀、幅值恒 U₀。
风格照 P1 figs 先例（青虚线导引线），150dpi。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
OUT = r"C:\提示词\工作区\_tmpP2图产0914"
CYAN = "#29B6F6"

def axes_with_arrows(ax, xlab, ylab, xlim, ylim):
    ax.set_xlim(xlim); ax.set_ylim(ylim)
    ax.annotate("", xy=(xlim[1], 0), xytext=(xlim[0], 0),
                arrowprops=dict(arrowstyle="->", color="k", lw=1.0), zorder=3)
    ax.annotate("", xy=(0, ylim[1]), xytext=(0, ylim[0]),
                arrowprops=dict(arrowstyle="->", color="k", lw=1.0), zorder=3)
    ax.text(xlim[1] - 0.03 * (xlim[1] - xlim[0]), -0.42 * (ylim[1] - ylim[0]) / 5,
            xlab, fontsize=12, ha="right")
    ax.text(-0.03 * (xlim[1] - xlim[0]), ylim[1], ylab,
            fontsize=13, ha="right", va="top")
    ax.axis("off")

# ---------- F6：05-T1 图乙（双极性方波，[0,T/2) 为 +U₀） ----------
T, U0 = 2.0, 1.0
# —— 自核：极性/周期钉死 ——
def u1(t):
    return U0 if (t % T) < T / 2 else -U0
assert u1(T / 8) > 0 and u1(3 * T / 4) < 0, "T1 极性崩：[0,T/2) 须为正（驱电子向A）"
assert u1(0.3) == u1(T + 0.3) and u1(0.3) == -u1(T / 2 + 0.3), "T1 周期/对称崩"
print("05-T1 自核：[0,T/2)=+U₀（驱电子向A）✓ [T/2,T)=−U₀ ✓ 周期 T ✓")

fig, ax = plt.subplots(figsize=(4.8, 2.9))
axes_with_arrows(ax, "$t$", "$u$", (-0.25, 4.55), (-1.75, 1.75))
xs, ys, tt = [0], [U0], 0.0
while tt < 2 * T - 1e-9:
    t2 = min(tt + T / 2, 2 * T)
    xs += [tt, t2]; ys += [ys[-1], ys[-1]]
    tt = t2
    if tt < 2 * T - 1e-9:
        xs.append(tt); ys.append(-ys[-1])
ax.plot(xs, ys, color="k", lw=1.8, zorder=4)
for tv, lab in [(T / 2, "$T/2$"), (T, "$T$"), (3 * T / 2, "$3T/2$"), (2 * T, "$2T$")]:
    ax.plot([tv, tv], [0, -0.09], color="k", lw=1.0)
    ax.text(tv + 0.06, -0.38, lab, ha="left", fontsize=11)
for uv, lab in [(U0, "$U_0$"), (-U0, "$-U_0$")]:
    ax.plot([-0.09, 2 * T], [uv, uv], color=CYAN, lw=0.9, ls="--", zorder=1)
    ax.text(-0.16, uv + 0.13, lab, ha="right", fontsize=12)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\05-T1-图乙方波.png", dpi=150, facecolor="white")
plt.close(fig)

# ---------- F7：05-T2 图乙（单极性方波，[0,t₀) 高电平） ----------
t0 = 1.0
def u2(t):
    return U0 if (t % (2 * t0)) < t0 else 0.0
assert u2(0.5 * t0) == U0 and u2(1.5 * t0) == 0, "T2 单极性崩：高电平须在 [0,t₀)"
assert u2(0.3) == u2(2.3) and set(
    u2(x) for x in [0.1, 0.9, 1.1, 1.9, 2.1, 3.9]) == {U0, 0.0}, "T2 周期 2t₀ 崩"
print("05-T2 自核：单极性 {0,U₀} ✓ 高电平[0,t₀) ✓ 周期 2t₀ ✓")

fig, ax = plt.subplots(figsize=(4.8, 2.9))
axes_with_arrows(ax, "$t$", "$u$", (-0.25, 4.55), (-1.05, 1.75))
xs = [0, 0, t0, t0, 2 * t0, 2 * t0, 3 * t0, 3 * t0, 4 * t0]
ys = [0, U0, U0, 0, 0, U0, U0, 0, 0]
assert ys[1] == U0 and ys[3] == 0, "T2 高电平须钉死在 [0,t₀)"
ax.plot(xs, ys, color="k", lw=1.8, zorder=4)
for tv, lab in [(t0, "$t_0$"), (2 * t0, "$2t_0$"), (3 * t0, "$3t_0$"), (4 * t0, "$4t_0$")]:
    ax.plot([tv, tv], [0, -0.05], color="k", lw=1.0)
    ax.text(tv + 0.06, -0.52, lab, ha="left", fontsize=11)
ax.plot([-0.09, 4 * t0], [U0, U0], color=CYAN, lw=0.9, ls="--", zorder=1)
ax.text(-0.16, U0 + 0.10, "$U_0$", ha="right", fontsize=12)
fig.tight_layout(pad=0.2)
fig.savefig(OUT + r"\05-T2-图乙方波.png", dpi=150, facecolor="white")
plt.close(fig)
print("F6/F7 写出：05-T1-图乙方波.png ＋ 05-T2-图乙方波.png")
