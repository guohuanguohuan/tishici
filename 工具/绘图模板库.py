# -*- coding: utf-8 -*-
"""绘图模板库 —— 参数化、教材风格的数学绘图模板（公共规则 §7「绘图模板库」条款）

单模块、函数式 API；matplotlib Agg 后端；中文字体 Microsoft YaHei（兜底 SimHei）。
修复原演示件（绘图能力演示/make_demo.py）两处已确认缺陷：
  ① 3D 直角记号原先用手工三段 3D 数据线拼装，在透视投影 + box_aspect 缩放下
     变形脱线（悬空小破框）。本库 mark_right_angle 改为「屏幕空间构造」：
     先把垂足、垂线方向、底面水平方向投影到屏幕，再沿两条投影线方向拼小方块。
     射影变换把 3D 直线映为 2D 直线，故记号两边严格落在垂线与水平方向的投影上
     （贴线由构造保证），尺寸自适应线宽与图幅。
  ② 2D 顶点/焦点标签原先直接压在曲线上。本库 label_curve_point 实现「标签避让」：
     曲线交点处标签沿该点外法线外推偏移（可在切向再平移），并带白底 bbox 防压线。

模板函数
--------
plot_function(f, xmin, xmax, ...)      函数图像（坐标轴过原点、虚线网格、关键点标注）
plot_conic(kind, a, b=None, ...)       椭圆/双曲线/抛物线（焦点、准线可选、顶点标签自动避让）
plot_polyhedron_3d(vertices, ...)      简单立体（可见实线/被遮挡虚线、面淡着色 alpha<=0.12、垂足直角记号）
plot_mindmap(root, children, ...)      思维导图/知识结构（节点框 + 肘形连线，自动排版）
save(fig, path, dpi=150, ...)          统一渲染出口（保存前灰度对比度与线宽/字号审计）

辅助函数
--------
label_curve_point / label_at           标签避让放置（法线外推 + 白底 bbox）
mark_right_angle(ax, foot, dir_horizontal, up, ...)   3D 垂足直角记号（屏幕空间构造）
mark_right_angle_2d(ax, foot, dir1, dir2, ...)        2D 直角记号（同思想）

渲染自检清单（每次出图逐项过目，结论落报告）
------------------------------------------
1. 遮挡关系：3D 图中被遮挡棱必须以虚线绘制，且在所选视点下确实位于实体之后
   ——逐棱检查：被遮挡棱相邻的面是否全部背向视点（无一面朝向观察者）。
2. 标签避让：曲线交点（顶点/零点/极值点）标签沿法线外推（label_curve_point），
   带白底 bbox；核查无压线（文本外沿与曲线像素距离 >= 2px）、无越界（不出图幅）。
3. 直角记号：3D 用 mark_right_angle（屏幕空间构造，两边贴垂线与水平方向），
   2D 用 mark_right_angle_2d；渲染后放大目视，必须贴线，不得悬空成破框。
4. 灰度打印对比度：save() 自动检查 L 通道直方图——墨迹（最深的 5% 墨点）与底色
   灰度对比 >= 0.35，不足则发 PlotQualityWarning（每图只汇总告警一次）。
5. 线宽/字号下限：图内文字 >= 7.35pt（五号 10.5pt 视觉高的 70%），主线宽 >= 0.7；
   save() 自动审计，违例汇总告警一次。

注意事项
--------
* mark_right_angle / mark_right_angle_2d 按调用时刻的视窗投影定形，须在
  视角/坐标范围/图幅全部定稿之后调用（模板内部会先完成一次画布绘制）。
* 3D 顶点标签用 Text3D（数据坐标），直角记号与思维导图连线用屏幕/轴分数坐标，
  因此记号不随后续视角改动重排——再次强调「定稿后调用」。
"""
from __future__ import annotations

import warnings

import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from matplotlib.text import Text
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

__all__ = [
    "PlotQualityWarning", "MIN_FONTSIZE_PT", "MIN_LINEWIDTH", "MIN_GRAY_CONTRAST",
    "plot_function", "plot_conic", "plot_polyhedron_3d", "plot_mindmap", "save",
    "label_curve_point", "label_at", "mark_right_angle", "mark_right_angle_2d",
]

# ----------------------------- 全局风格 -----------------------------
FONT_STACK = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
MIN_FONTSIZE_PT = 7.35      # 五号 10.5pt 视觉高的 70%
MIN_LINEWIDTH = 0.7         # 主线宽下限（pt）
MIN_GRAY_CONTRAST = 0.35    # 灰度墨迹/底色对比下限

plt.rcParams["font.sans-serif"] = FONT_STACK
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "dejavusans"

INK = "#1a1a1a"             # 正文墨色
CURVE = "#1f4e9c"           # 曲线主色（灰度后约 0.30，对比合格）
ACCENT = "#c22b2b"          # 关键点
GREEN = "#217a21"
ORANGE = "#c26a10"
HIDDEN = "0.45"             # 被遮挡棱灰


class PlotQualityWarning(UserWarning):
    """绘图质量自检告警（灰度对比度不足 / 字号或线宽低于下限等）。"""


# ----------------------------- 通用小工具 -----------------------------

def _new_ax(ax=None, figsize=(4.6, 4.0), **subplots_kw):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, **subplots_kw)
    else:
        fig = ax.figure
    return fig, ax


def _style_axes_through_origin(ax, xlim, ylim):
    """坐标轴过原点、去顶右框、虚线网格——教材函数图惯例。"""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines["left"].set_color(INK)
    ax.spines["bottom"].set_color(INK)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.grid(True, ls=(0, (1, 2)), lw=0.7, color="0.72", alpha=0.9, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK, labelsize=9)


def _drop_zero(ticks):
    return [t for t in ticks if abs(t) > 1e-12]


def _screen_dir(ax, p, d):
    """数据空间方向 d（2D）在点 p 处的屏幕单位方向。"""
    tr = ax.transData
    a = np.asarray(tr.transform((float(p[0]), float(p[1]))), float)
    b = np.asarray(tr.transform((float(p[0] + d[0]), float(p[1] + d[1]))), float)
    v = b - a
    n = float(np.hypot(*v))
    return v / n if n > 1e-12 else np.array([0.0, 1.0])


# ----------------------------- 标签避让 -----------------------------

def label_curve_point(ax, x, y, text, *, normal=(0.0, 1.0), tangent=None,
                      offset_pt=12.0, tangent_pt=0.0, fontsize=10.0,
                      color=INK, bbox=True, zorder=8, fontweight="normal",
                      screen=False):
    """曲线交点处标签避让：沿外法线 normal 外推 offset_pt（pt），可再沿切向平移
    tangent_pt（pt）；默认白底 bbox 防压线。normal / tangent 缺省按「数据空间」向量
    解释并投影到屏幕；传 screen=True 时直接按屏幕单位向量解释（与纵横比无关，
    适合非 equal 纵横比的函数图）。
    """
    if screen:
        u_n = np.asarray(normal, float)
        u_n = u_n / np.hypot(*u_n)
        off = u_n * float(offset_pt)
        if tangent is not None and tangent_pt:
            u_t = np.asarray(tangent, float)
            u_t = u_t / np.hypot(*u_t)
            off = off + u_t * float(tangent_pt)
    else:
        off = _screen_dir(ax, (x, y), normal) * float(offset_pt)
        if tangent is not None and tangent_pt:
            off = off + _screen_dir(ax, (x, y), tangent) * float(tangent_pt)
    bbox_kw = dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.92) if bbox else None
    return ax.annotate(
        text, xy=(float(x), float(y)), xytext=off, textcoords="offset points",
        ha="center", va="center", fontsize=fontsize, color=color,
        fontweight=fontweight, bbox=bbox_kw, zorder=zorder)


def label_at(ax, x, y, text, *, off_pt=(0.0, -14.0), fontsize=10.0, color=INK,
             bbox=True, zorder=8, ha="center", va="center", fontweight="normal"):
    """定点标签：按屏幕点偏移 off_pt（pt），带白底 bbox（用于焦点等线外要素）。"""
    bbox_kw = dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.92) if bbox else None
    return ax.annotate(
        text, xy=(float(x), float(y)), xytext=tuple(off_pt), textcoords="offset points",
        ha=ha, va=va, fontsize=fontsize, color=color,
        fontweight=fontweight, bbox=bbox_kw, zorder=zorder)


# ----------------------------- 直角记号 -----------------------------

def _auto_mark_size(fig, ax, lw):
    lw_px = lw * fig.dpi / 72.0
    bb = ax.get_window_extent()
    cap = 0.11 * min(bb.width, bb.height)
    return float(min(max(3.6 * lw_px, 8.0), cap))


def _draw_square(ax, foot_disp, uh, uv, size_px, lw, color, zorder):
    """在屏幕空间沿方向 uh（水平）与 uv（竖直）画三边小方块：
    垂足 -> 水平边端 -> 对角 -> 竖直边端（沿垂线一侧留口，由垂线自身封口）。"""
    d0 = np.asarray(foot_disp, float)
    A = d0 + size_px * uh
    B = A + size_px * uv
    C = d0 + size_px * uv
    inv = ax.transAxes.inverted()
    pts = inv.transform(np.array([d0, A, B, C]))
    artists = []
    for i, j in ((0, 1), (1, 2), (2, 3)):
        ln = mlines.Line2D(pts[[i, j], 0], pts[[i, j], 1], transform=ax.transAxes,
                           color=color, lw=lw, solid_capstyle="butt",
                           solid_joinstyle="miter", zorder=zorder, clip_on=False)
        ax.add_artist(ln)
        artists.append(ln)
    return artists


def mark_right_angle(ax, foot, dir_horizontal, up, *, size=None, lw=1.3,
                     color="0.25", zorder=1000):
    """3D 垂足直角记号（屏幕空间构造，投影下必然贴线）。

    在「垂线方向 up」与「底面内水平方向 dir_horizontal」张成的竖直平面内画小方块：
    两边分别贴垂线与该水平方向的投影线。size 单位为屏幕像素，缺省自适应线宽与图幅
    （3.6*线宽像素，下限 8px，上限 0.11*轴短边）。
    须在视角/坐标范围定稿后调用；返回三条 Line2D 艺术对象。
    """
    fig = ax.figure
    fig.canvas.draw()  # 定稿视窗，保证投影矩阵与窗口范围有效
    M = ax.get_proj()
    f2 = proj3d.proj_transform(float(foot[0]), float(foot[1]), float(foot[2]), M)[:2]
    h2 = proj3d.proj_transform(float(foot[0] + dir_horizontal[0]),
                               float(foot[1] + dir_horizontal[1]),
                               float(foot[2] + dir_horizontal[2]), M)[:2]
    u2 = proj3d.proj_transform(float(foot[0] + up[0]), float(foot[1] + up[1]),
                               float(foot[2] + up[2]), M)[:2]
    d0 = np.asarray(ax.transData.transform(f2), float)
    dh = np.asarray(ax.transData.transform(h2), float)
    du = np.asarray(ax.transData.transform(u2), float)
    uh = dh - d0
    uh = uh / np.hypot(*uh)
    uv = du - d0
    uv = uv / np.hypot(*uv)
    s = float(size) if size is not None else _auto_mark_size(fig, ax, lw)
    return _draw_square(ax, d0, uh, uv, s, lw, color, zorder)


def mark_right_angle_2d(ax, foot, dir1, dir2, *, size=None, lw=1.2,
                        color="0.25", zorder=50):
    """2D 直角记号：与 3D 版同思想，两边贴 dir1、dir2 的屏幕投影方向。"""
    fig = ax.figure
    fig.canvas.draw()
    d0 = np.asarray(ax.transData.transform((float(foot[0]), float(foot[1]))), float)
    u1 = _screen_dir(ax, foot, dir1)
    u2 = _screen_dir(ax, foot, dir2)
    s = float(size) if size is not None else _auto_mark_size(fig, ax, lw)
    return _draw_square(ax, d0, u1, u2, s, lw, color, zorder)


# ----------------------------- 模板 1：函数图像 -----------------------------

def plot_function(f, xmin, xmax, *, ax=None, figsize=(4.6, 4.0), n=900,
                  key_points=None, color=CURVE, lw=2.2,
                  xticks=None, yticks=None, title="", xlim=None, ylim=None,
                  xlabel="$x$", ylabel="$y$", grid=True):
    """函数图像：坐标轴过原点、虚线网格、关键点沿法线外推标注（带白底 bbox）。

    key_points: (x, label) / (x, y, label) / (x, y, label, 切向平移pt) /
                (x, y, label, 切向平移pt, 法线外推pt)；法线在屏幕空间取
                （垂直于投影后曲线、背离 x 轴一侧），标签自动避让曲线（带白底 bbox）。
    """
    fig, ax = _new_ax(ax, figsize)
    xs = np.linspace(float(xmin), float(xmax), int(n))
    try:
        ys = np.asarray(f(xs), float)
        if ys.shape != xs.shape:
            raise ValueError
    except Exception:
        ys = np.asarray([f(t) for t in xs], float)
    pad_x = 0.06 * (xmax - xmin)
    if xlim is None:
        xlim = (xmin - pad_x, xmax + pad_x)
    yr = float(np.nanmax(ys) - np.nanmin(ys))
    pad_y = 0.18 * max(yr, 1e-9)
    if ylim is None:
        ylim = (float(np.nanmin(ys)) - pad_y, float(np.nanmax(ys)) + pad_y)
    _style_axes_through_origin(ax, xlim, ylim)
    if grid:
        ax.grid(True, ls=(0, (1, 2)), lw=0.7, color="0.72", alpha=0.9, zorder=0)
    ax.plot(xs, ys, color=color, lw=lw, zorder=4, solid_capstyle="round")

    # 轴端字母
    ax.text(xlim[1] * 0.985, 0.06 * (ylim[1] - ylim[0]), xlabel,
            fontsize=10, style="italic", color=INK, ha="right", va="bottom")
    ax.text(0.06 * (xlim[1] - xlim[0]), ylim[1] * 0.985, ylabel,
            fontsize=10, style="italic", color=INK, ha="left", va="top")

    if xticks is not None:
        ax.set_xticks(list(xticks))
    if yticks is not None:
        ax.set_yticks(list(yticks))
    # 原点不标 0（教材惯例）
    if 0.0 in list(ax.get_xticks()):
        ax.set_xticks(_drop_zero(ax.get_xticks()))
    if 0.0 in list(ax.get_yticks()):
        ax.set_yticks(_drop_zero(ax.get_yticks()))

    handles = []
    if key_points:
        h = 1e-6
        for kp in key_points:
            if len(kp) == 2:
                x, label, y, tan_pt, off_pt = float(kp[0]), kp[1], None, 0.0, 13.0
            elif len(kp) == 3:
                x, y, label = float(kp[0]), float(kp[1]), kp[2]
                tan_pt, off_pt = 0.0, 13.0
            elif len(kp) == 4:
                x, y, label, tan_pt = float(kp[0]), float(kp[1]), kp[2], float(kp[3])
                off_pt = 13.0
            else:
                x, y, label = float(kp[0]), float(kp[1]), kp[2]
                tan_pt, off_pt = float(kp[3]), float(kp[4])
            if y is None:
                y = float(f(x))
            fp = (f(x + h) - f(x - h)) / (2 * h) if callable(f) else 0.0
            # 法线在「屏幕空间」取（垂直于投影后的曲线切线），避让与纵横比无关；
            # 符号取背离 x 轴一侧。
            u_t = _screen_dir(ax, (x, y), (1.0, float(fp)))
            n_screen = np.array([-u_t[1], u_t[0]])
            if (y >= 0 and n_screen[1] < 0) or (y < 0 and n_screen[1] > 0):
                n_screen = -n_screen
            ax.scatter([x], [y], s=22, color=ACCENT, zorder=6)
            handles.append(label_curve_point(ax, x, y, label, normal=n_screen,
                                             offset_pt=off_pt,
                                             tangent_pt=tan_pt, fontsize=9.5,
                                             screen=True))
    if title:
        ax.set_title(title, fontsize=11.5, color=INK, pad=8)
    fig.canvas.draw()
    return fig, ax


# ----------------------------- 模板 2：二次曲线 -----------------------------

def _conic_axes(ax, xlim, ylim, title):
    _style_axes_through_origin(ax, xlim, ylim)
    if title:
        ax.set_title(title, fontsize=11.5, color=INK, pad=8)


def plot_conic(kind, a, b=None, *, ax=None, figsize=(4.6, 4.0),
               show_focus=True, show_directrix=False, show_vertices=True,
               show_asymptotes=False, point=None, title="",
               xlim=None, ylim=None, color=CURVE, lw=2.2):
    """椭圆 / 双曲线 / 抛物线（教材风格）。

    kind="ellipse":   a=半长轴, b=半短轴 (b<a)；焦点、准线 x=±a²/c 可选；
                      point=参数 t 可画点 P 与两条焦半径（焦点定义）。
    kind="hyperbola": a=实半轴, b=虚半轴；渐近线可选；准线可选。
    kind="parabola":  a=p（y²=2px）；焦点 (p/2,0)、准线 x=-p/2；
                      point=纵坐标 y₀ 可画定义构造 M、K（|MF|=|MK|，K 处 2D 直角记号）。
    顶点标签一律沿外法线外推 + 白底 bbox（标签避让）。
    """
    kind = kind.lower()
    fig, ax = _new_ax(ax, figsize)
    handles = {}

    if kind == "ellipse":
        if b is None:
            raise ValueError("椭圆需要 b")
        c = float(np.sqrt(a * a - b * b))
        t = np.linspace(0, 2 * np.pi, 720)
        cx, cy = a * np.cos(t), b * np.sin(t)
        if xlim is None:
            xlim = (-(a + 1.35), a + 1.35)
        if ylim is None:
            ylim = (-(b + 1.25), b + 1.25)
        _conic_axes(ax, xlim, ylim, title)
        ax.plot([-a, a], [0, 0], ls=(0, (5, 3)), color="0.55", lw=1.0, zorder=2)
        ax.plot([0, 0], [-b, b], ls=(0, (5, 3)), color="0.55", lw=1.0, zorder=2)
        ax.plot(cx, cy, color=color, lw=lw, zorder=4)
        if show_focus:
            for fx, lab in ((-c, r"$F_1(-%g,\,0)$" % c), (c, r"$F_2(%g,\,0)$" % c)):
                ax.scatter([fx], [0], s=26, color=ACCENT, zorder=6)
                handles[lab] = label_at(ax, fx, 0, lab, off_pt=(0, -23), fontsize=9.5)
        if show_directrix:
            for dx in (-a * a / c, a * a / c):
                ax.plot([dx, dx], [ylim[0], ylim[1]], ls=(0, (5, 3)),
                        color="0.4", lw=1.1, zorder=2)
        if show_vertices:
            handles["$A_1$"] = label_curve_point(ax, -a, 0, r"$A_1$", normal=(-1, 0),
                                                 tangent=(0, 1), offset_pt=12,
                                                 tangent_pt=8, fontsize=10)
            handles["$A_2$"] = label_curve_point(ax, a, 0, r"$A_2$", normal=(1, 0),
                                                 tangent=(0, 1), offset_pt=12,
                                                 tangent_pt=8, fontsize=10)
            handles["$B_2$"] = label_curve_point(ax, 0, b, r"$B_2$", normal=(0, 1),
                                                 tangent=(1, 0), offset_pt=12,
                                                 tangent_pt=8, fontsize=10)
            handles["$B_1$"] = label_curve_point(ax, 0, -b, r"$B_1$", normal=(0, -1),
                                                 tangent=(1, 0), offset_pt=12,
                                                 tangent_pt=8, fontsize=10)
        if point is not None:
            tt = float(point)
            px, py = a * np.cos(tt), b * np.sin(tt)
            ax.plot([px, -c], [py, 0], color=GREEN, lw=1.7, zorder=3)
            ax.plot([px, c], [py, 0], color=ORANGE, lw=1.7, zorder=3)
            ax.scatter([px], [py], s=30, color=ACCENT, zorder=7)
            g = np.array([px / (a * a), py / (b * b)])
            g = g / np.hypot(*g)
            handles["$P$"] = label_curve_point(ax, px, py, r"$P$", normal=g,
                                               offset_pt=11, fontsize=11, bbox=False)
            m1 = ((px - c) / 2, py / 2)
            handles["$|PF_1|$"] = label_at(ax, m1[0] - 0.55, m1[1] + 0.42, r"$|PF_1|$",
                                           off_pt=(0, 0), fontsize=9.5, color=GREEN)
            m2 = ((px + c) / 2, py / 2)
            handles["$|PF_2|$"] = label_at(ax, m2[0] + 0.62, m2[1] + 0.18, r"$|PF_2|$",
                                           off_pt=(0, 0), fontsize=9.5, color=ORANGE)

    elif kind == "hyperbola":
        if b is None:
            raise ValueError("双曲线需要 b")
        c = float(np.sqrt(a * a + b * b))
        u = np.linspace(-2.1, 2.1, 400)
        if xlim is None:
            xlim = (-(a + 2.6), a + 2.6)
        if ylim is None:
            ylim = (-(b * 1.9), b * 1.9)
        _conic_axes(ax, xlim, ylim, title)
        if show_asymptotes:
            xs0 = np.array(xlim)
            for sgn in (1, -1):
                ax.plot(xs0, sgn * b / a * xs0, ls=(0, (5, 3)), color="0.6",
                        lw=1.0, zorder=2)
        for sgn in (1, -1):
            ax.plot(sgn * a * np.cosh(u), sgn * b * np.sinh(u), color=color,
                    lw=lw, zorder=4)
        ax.plot([-a, a], [0, 0], ls=(0, (5, 3)), color="0.55", lw=1.0, zorder=2)
        if show_focus:
            for fx, lab in ((-c, r"$F_1$"), (c, r"$F_2$")):
                ax.scatter([fx], [0], s=26, color=ACCENT, zorder=6)
                handles[lab] = label_at(ax, fx, 0, lab, off_pt=(0, -15), fontsize=10)
        if show_directrix:
            for dx in (-a * a / c, a * a / c):
                ax.plot([dx, dx], [ylim[0], ylim[1]], ls=(0, (5, 3)),
                        color="0.4", lw=1.1, zorder=2)
        if show_vertices:
            handles["$A_1$"] = label_curve_point(ax, -a, 0, r"$A_1$", normal=(-1, 0),
                                                 tangent=(0, 1), offset_pt=11,
                                                 tangent_pt=7, fontsize=10)
            handles["$A_2$"] = label_curve_point(ax, a, 0, r"$A_2$", normal=(1, 0),
                                                 tangent=(0, 1), offset_pt=11,
                                                 tangent_pt=7, fontsize=10)

    elif kind == "parabola":
        p = float(a)                       # y² = 2p x
        u = np.linspace(-np.sqrt(2 * p * 4.6), np.sqrt(2 * p * 4.6), 720)
        cx, cy = u * u / (2 * p), u
        if xlim is None:
            xlim = (-p / 2 - 1.15, float(np.nanmax(cx)) + 0.75)
        if ylim is None:
            ylim = (float(np.nanmin(cy)) - 0.85, float(np.nanmax(cy)) + 0.85)
        _conic_axes(ax, xlim, ylim, title)
        if show_directrix:
            ax.plot([-p / 2, -p / 2], [ylim[0], ylim[1]], ls=(0, (5, 3)),
                    color="0.4", lw=1.2, zorder=2)
            handles["directrix"] = label_at(ax, -p / 2, ylim[1] - 0.28,
                                            r"准线 $l:\ x=-%g$" % (p / 2),
                                            off_pt=(0, -6), fontsize=9.5)
        ax.plot(cx, cy, color=color, lw=lw, zorder=4)
        if show_focus:
            ax.scatter([p / 2], [0], s=26, color=ACCENT, zorder=6)
            handles["focus"] = label_at(ax, p / 2, 0, r"$F(%g,\,0)$" % (p / 2),
                                        off_pt=(0, -15), fontsize=9.5)
        if show_vertices:
            handles["vertex"] = label_curve_point(ax, 0, 0, r"$O$", normal=(-1, 0),
                                                  tangent=(0, 1), offset_pt=10,
                                                  tangent_pt=5, fontsize=10,
                                                  bbox=False)
        if point is not None:
            y0 = float(point)
            mx = y0 * y0 / (2 * p)
            kx = -p / 2
            ax.plot([p / 2, mx], [0, y0], color=GREEN, lw=1.7, zorder=3)   # MF
            ax.plot([mx, kx], [y0, y0], color=ORANGE, lw=1.7, zorder=3)    # MK
            ax.scatter([mx], [y0], s=24, color=ACCENT, zorder=7)
            ax.scatter([kx], [y0], s=13, color=INK, zorder=7)
            # M 标签放曲线凹侧（切线屏幕方向顺时针转 90°），避开曲线与两条焦半径
            u_t = _screen_dir(ax, (mx, y0), (y0 / 2.0, 1.0))
            n_concave = np.array([u_t[1], -u_t[0]])
            handles["$M$"] = label_curve_point(ax, mx, y0, r"$M$", normal=n_concave,
                                               offset_pt=12, fontsize=10.5,
                                               screen=True)
            handles["$K$"] = label_at(ax, kx, y0, r"$K$", off_pt=(-14, -12),
                                      fontsize=10.5)
            mark_right_angle_2d(ax, (kx, y0), (1, 0), (0, -1), size=11.0, lw=1.2)
            handles["eq"] = label_at(ax, (mx + kx) / 2 - 0.1,
                                     y0 + 0.40 * (1 if y0 > 0 else -1),
                                     r"$|MF|=|MK|$", off_pt=(0, 0), fontsize=9.5)
    else:
        raise ValueError("kind 须为 ellipse / hyperbola / parabola")

    ax.set_aspect("equal", adjustable="box")
    fig.canvas.draw()
    return fig, ax, handles


# ----------------------------- 模板 3：简单立体 -----------------------------

def plot_polyhedron_3d(vertices, edges_visible, edges_hidden=(), *, faces=None,
                       labels=None, extra_labels=(), extra_lines=(), ax=None,
                       figsize=(4.8, 4.4), elev=18, azim=-58, box_aspect=None,
                       lims=None, title="", mark_right=None,
                       lw_visible=1.8, lw_hidden=1.1, label_fontsize=11):
    """简单立体（教材惯例）：可见棱实线、被遮挡棱虚线、面淡着色（alpha<=0.12）。

    vertices: {名称: (x,y,z)}
    edges_visible / edges_hidden: [(名称, 名称), ...]
    faces: [(名称列表, 颜色, alpha<=0.12), ...]
    labels: {名称: (dx,dy,dz)} 可手工指定标签偏移；缺省按「离开形心」自动偏移
    extra_labels: [(x,y,z, 文本, 是否白底), ...]（如垂足 O）
    extra_lines: [((x0,y0,z0),(x1,y1,z1), 颜色, 线宽), ...]（如体对角线）
    mark_right: dict(foot=..., up=..., size=None,
                     dir_horizontal=... 或 "auto") 垂足直角记号。
                     dir_horizontal 须取底面内「与视线方位垂直」的水平方向（投影为屏幕
                     水平方向）；若取指向观察者的方向，其投影与“上”共线，方块会退化
                     成一条线——"auto" 按当前 azim 自动取正确方向。
    """
    fig, ax = _new_ax(ax, figsize, subplot_kw={"projection": "3d"})
    V = {k: np.asarray(v, float) for k, v in vertices.items()}

    def seg(u, v, style, color_, lw_):
        ax.plot([V[u][0], V[v][0]], [V[u][1], V[v][1]], [V[u][2], V[v][2]],
                linestyle=style, color=color_, lw=lw_)

    for u, v in edges_hidden:
        seg(u, v, (0, (5, 3)), HIDDEN, lw_hidden)
    for u, v in edges_visible:
        seg(u, v, "-", INK, lw_visible)
    for p0, p1, color_, lw_ in extra_lines:
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]],
                "-", color=color_, lw=lw_, zorder=6)

    if faces:
        for names, fc, alpha_ in faces:
            alpha_ = min(float(alpha_), 0.12)   # 硬性上限
            poly = Poly3DCollection([[V[n] for n in names]], alpha=alpha_,
                                    facecolor=fc, linewidth=0)
            ax.add_collection3d(poly)

    if lims:
        (x0, x1), (y0, y1), (z0, z1) = lims
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_zlim(z0, z1)
    if box_aspect:
        ax.set_box_aspect(box_aspect)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()

    centroid = np.mean(list(V.values()), axis=0)
    lbl_kw = dict(fontsize=label_fontsize, color=INK,
                  bbox=dict(fc="white", ec="none", alpha=0.78, pad=1.6))
    if labels is None:
        labels = {}
    for name, v in V.items():
        off = labels.get(name)
        if off is None:
            d = v - centroid
            n = float(np.linalg.norm(d))
            off = (d / n * 0.17) if n > 1e-9 else np.array([0.0, 0.0, 0.15])
        ax.text(v[0] + off[0], v[1] + off[1], v[2] + off[2], name, **lbl_kw)
    for item in extra_labels:
        x, y, z, txt = item[:4]
        with_bbox = item[4] if len(item) > 4 else True
        kw = dict(fontsize=label_fontsize - 1, color=INK)
        if with_bbox:
            kw["bbox"] = dict(fc="white", ec="none", alpha=0.8, pad=1.4)
        ax.text(x, y, z, txt, **kw)

    if mark_right:
        dh = mark_right.get("dir_horizontal")
        if dh is None or (isinstance(dh, str) and dh == "auto"):
            # 缺省取底面内与视线方位垂直的水平方向：其投影恰为屏幕水平方向，
            # 记号两边分别贴垂线（屏幕竖直）与该方向（屏幕水平），不退化。
            dh = (-np.sin(np.radians(azim)), np.cos(np.radians(azim)), 0.0)
        mark_right_angle(ax, foot=mark_right["foot"], dir_horizontal=dh,
                         up=mark_right["up"],
                         size=mark_right.get("size"), lw=mark_right.get("lw", 1.3))
    if title:
        ax.set_title(title, fontsize=11.5, color=INK, pad=2)
    fig.canvas.draw()
    return fig, ax


# ----------------------------- 模板 4：思维导图 -----------------------------

def plot_mindmap(root, children, *, ax=None, figsize=(4.8, 4.2), title=None,
                 fontsize=9.5, root_fontsize=11.5, gap_px=30.0, gap2_px=26.0,
                 margin_px=10.0, slot_pad_px=13.0,
                 fc_root="#dbe6f6", fc_l1="#efefef", fc_leaf="#ffffff",
                 ec="#3f3f3f", edge_color="#8a9099"):
    """思维导图/知识结构（左→右树形布局，节点框 + 总干线/鱼骨连线）。

    children: [文本] 或 [文本, [子文本, ...]] 混合列表，最多两级。
    布局在轴分数坐标系内按像素实测文本框宽高排版，自动收缩字号保证不越界。
    """
    fig, ax = _new_ax(ax, figsize)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_axis_off()
    items = []          # (level, text, parent_id or None)
    for ch in children:
        if isinstance(ch, (tuple, list)) and len(ch) == 2:
            items.append(("L1", ch[0], None, ch[1]))
        else:
            items.append(("L1", ch, None, []))

    def mk_text(txt, level, fs):
        fc = fc_root if level == "root" else (fc_l1 if level == "L1" else fc_leaf)
        t = ax.text(0.5, 0.5, txt, transform=ax.transAxes, ha="center", va="center",
                    fontsize=fs, color=INK, zorder=3,
                    bbox=dict(boxstyle="round,pad=0.42", fc=fc, ec=ec, lw=1.0))
        return t

    root_t = mk_text(root, "root", root_fontsize)
    l1_ts, leaf_ts, leaf_owner = [], [], []
    for i, (lv, txt, _, subs) in enumerate(items):
        l1_ts.append((i, mk_text(txt, "L1", fontsize)))
        for s in (subs or []):
            leaf_ts.append(mk_text(s, "leaf", fontsize))
            leaf_owner.append(i)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    axbb = ax.get_window_extent(renderer)
    W, H = axbb.width, axbb.height

    def wpx(t):
        return t.get_window_extent(renderer).width

    def hpx(t):
        return t.get_window_extent(renderer).height

    # 字号自适应：若列宽超界则整体收缩（下限 MIN_FONTSIZE_PT）
    for _ in range(6):
        need = (wpx(root_t) + max(wpx(t) for _, t in l1_ts) +
                (max(wpx(t) for t in leaf_ts) if leaf_ts else 0.0) +
                gap_px + gap2_px + 2 * margin_px)
        if need <= W or fontsize <= MIN_FONTSIZE_PT + 1e-9:
            break
        ratio = max(0.82, W / need)
        fontsize *= ratio
        root_fontsize = max(MIN_FONTSIZE_PT, root_fontsize * ratio)
        for _, t in l1_ts + [(None, leaf_t) for leaf_t in leaf_ts]:
            t.set_fontsize(fontsize)
        root_t.set_fontsize(root_fontsize)
        fig.canvas.draw()

    # 垂直布局：叶子均分槽位
    n_leaf = len(leaf_ts) if leaf_ts else len(l1_ts)
    slot = (H - 2 * margin_px) / max(n_leaf, 1)
    y_of_leaf = {}
    for i in range(n_leaf):
        y_of_leaf[i] = H - margin_px - slot * (i + 0.5)
    box_h = max(hpx(t) for t in leaf_ts) if leaf_ts else 0.0
    if slot < box_h + slot_pad_px:
        slot = box_h + slot_pad_px          # 防挤压（可能越界，由 save 审计兜底）

    def frac(px, py):
        return px / W, py / H

    def line(x0, y0, x1, y1):
        fx, fy = frac(np.array([x0, x1]), np.array([y0, y1]))
        ln = mlines.Line2D(fx, fy, transform=ax.transAxes, color=edge_color,
                           lw=1.2, zorder=1, solid_capstyle="round", clip_on=False)
        ax.add_artist(ln)

    # L1 纵坐标：有叶子的取叶均值，无叶子的占用独立槽
    solo_slots = []
    l1_y = {}
    for i, t in l1_ts:
        own = [k for k, o in enumerate(leaf_owner) if o == i]
        if own:
            l1_y[i] = sum(y_of_leaf[k] for k in own) / len(own)
        else:
            solo_slots.append(i)
    n_solo = len(solo_slots)
    if n_solo:
        all_y = [y_of_leaf[k] for k in range(n_leaf)]
        span_lo, span_hi = min(all_y), max(all_y)
        step = (span_hi - span_lo) / (n_solo + 1)
        for j, i in enumerate(solo_slots):
            l1_y[i] = span_hi - step * (j + 1)
    # 列的 x 坐标（像素）：一级列右对齐、叶子列左对齐，衔接总干线
    w_root = wpx(root_t)
    w_l1_max = max(wpx(t) for _, t in l1_ts)
    w_l2_max = max((wpx(t) for t in leaf_ts), default=0.0)
    x_root = margin_px + w_root / 2
    x_l1_right = x_root + w_root / 2 + gap_px + w_l1_max
    x_bus = x_l1_right + gap2_px * 0.5
    x_l2_left = x_l1_right + gap2_px
    y_root = sum(l1_y.values()) / len(l1_y)

    root_t.set_position(frac(x_root, y_root))
    for i, t in l1_ts:
        t.set_ha("right")
        t.set_position(frac(x_l1_right, l1_y[i]))

    # 总干线（鱼骨）设计：竖直总线 + 各节点水平支线
    ys_all = list(l1_y.values()) + [y_of_leaf[k] for k in range(n_leaf)]
    line(x_bus, min(ys_all), x_bus, max(ys_all))          # 总线
    line(x_root + w_root / 2, y_root, x_bus, y_root)      # 根干
    for i, t in l1_ts:
        line(x_l1_right, l1_y[i], x_bus, l1_y[i])
    for k, t in enumerate(leaf_ts):
        y = y_of_leaf[k]
        t.set_ha("left")
        t.set_position(frac(x_l2_left, y))
        line(x_bus, y, x_l2_left, y)
    if title:
        ax.set_title(title, fontsize=11.5, color=INK, pad=6)
    fig.canvas.draw()
    return fig, ax


# ----------------------------- 统一渲染出口 -----------------------------

def save(fig, path, *, dpi=150, grayscale_check=True, quality_audit=True,
         bbox_inches=None, facecolor="white"):
    """统一渲染出口：绘制 -> 质量审计（灰度对比度 / 字号 / 线宽，汇总至多告警一次）
    -> 保存。返回质量报告 dict。低质量项以 PlotQualityWarning 告警（不阻断保存）。"""
    fig.canvas.draw()
    issues = []
    report = {"path": str(path), "dpi": dpi, "gray_contrast": None, "issues": issues}

    if quality_audit:
        renderer = fig.canvas.get_renderer()
        small = []
        for t in fig.findobj(Text):
            try:
                if not t.get_visible() or not t.get_text().strip():
                    continue
                if t.get_fontsize() < MIN_FONTSIZE_PT - 1e-9:
                    small.append(f"{t.get_text()[:12]!r}@{t.get_fontsize():.2f}pt")
            except Exception:
                continue
        if small:
            issues.append("字号低于下限 %gpt: %s" % (MIN_FONTSIZE_PT, small[:6]))
        thin = []
        for ax in fig.axes:
            for ln in getattr(ax, "lines", []):
                try:
                    if str(ln.get_linestyle()) in ("None", "none", ""):
                        continue
                    al = ln.get_alpha()
                    if al is not None and al < 0.5:
                        continue
                    if ln.get_linewidth() < MIN_LINEWIDTH - 1e-9:
                        thin.append(round(ln.get_linewidth(), 2))
                except Exception:
                    continue
        if thin:
            issues.append("线宽低于下限 %g: %s" % (MIN_LINEWIDTH, thin[:6]))

    if grayscale_check:
        buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        L = (0.299 * buf[:, :, 0] + 0.587 * buf[:, :, 1] + 0.114 * buf[:, :, 2])
        Li = np.rint(L).astype(np.int32).ravel()
        hist = np.bincount(Li, minlength=256)
        bg = int(hist.argmax())
        ink = Li < (bg - 30)
        report["gray_bg"] = bg
        if ink.sum() >= max(50, 5e-4 * Li.size):
            text_L = float(np.percentile(Li[ink], 5))
            contrast = (bg - text_L) / 255.0
            report["gray_contrast"] = round(float(contrast), 3)
            report["gray_ink_frac"] = round(float(ink.mean()), 5)
            if contrast < MIN_GRAY_CONTRAST:
                issues.append("灰度对比度不足: 墨迹最深处 L=%.0f vs 底色 L=%d, "
                              "对比 %.2f < %.2f（灰度打印易糊）"
                              % (text_L, bg, contrast, MIN_GRAY_CONTRAST))
        else:
            report["gray_ink_frac"] = round(float(ink.mean()), 6)

    if issues:
        warnings.warn("绘图质量自检(" + str(path) + "): " + "；".join(issues),
                      PlotQualityWarning, stacklevel=2)

    fig.savefig(str(path), dpi=dpi, bbox_inches=bbox_inches, facecolor=facecolor)
    return report
