# -*- coding: utf-8 -*-
"""绘图模板库 v2 —— 双后端参数化绘图模板（公共规则 §7「绘图模板库」条款，2026-08-30 双后端定案）

后端定案（见公共规则 §7）
------------------------
* 主力后端＝LaTeX/TikZ 体系（xelatex + standalone + ctex）：物理图族（电路/受力/光路/
  运动图像）与平面数学图族一律走 TikZ——circuitikz 电路、tkz-euclide 几何与受力、
  pgfplots 函数/运动图像；中文标签由 ctex 直接排版。
* 立体几何族＝Asymptote（真 3D 遮挡引擎，TikZ 的 3D 遮挡系手工、精度不足）。
* matplotlib 版已改名 ``绘图模板库_mpl.py`` 降级为过渡期函数/统计图辅助，非本库依赖。

模板函数（一律返回 spec 字典，纯文本生成、不做任何 I/O）
--------------------------------------------------------
TikZ 后端：
  circuit_voltammetry(...)   伏安法电路（circuitikz；教材惯例布局：电源→开关→A 与 Rx
                             串联、V 并联在 Rx 两端，V 水平放置保证表盘字母正立）
  force_incline(...)         斜面滑块受力（tkz-euclide；θ 角、mg/N/f 三箭头自滑块中心、
                             接触点与底角两处直角记号、斜面阴影短线）
  motion_graph(...)          运动图像（pgfplots；两段折线 v-t，轴端物理量/单位标注如
                             v/(m·s⁻¹)，折点虚线引导线）
  optics_refraction(...)     折射光路（TikZ；界面/法线/入射折射光线，折射角按
                             sinθ₂=sinθ₁/n 实算并标角度弧，计算过程写入源码注释）
  mindmap_tree(root, tree)   思维导图/知识结构（TikZ 树：根/一级/二级节点框+连线，
                             叶槽均分布局，node-to-node 连线自然落在边框间）
  tikz_raw(source)           透传接口：给 tikzpicture 正文自动包标准导言区；
                             给完整 \\documentclass 文档则原样编译
Asymptote 后端：
  polyhedron_3d(...)         简单立体（vertices+visible/hidden 边列表；遮挡层次由
                             引擎处理；半透明面可选；垂足直角记号 mark_right——
                             屏幕等效构造）

统一渲染出口
------------
  render(spec, out_png, dpi=150)  写源文件（.tex/.asy 存 out_png 同级 sources/ 子目录，
  源码即图、可入 git）→ ASCII 中转文件名编译（xelatex / asy）→ gswin64c PDF→PNG
  → 灰度对比度检查（PIL L 通道：墨迹最深处与底色对比 <0.35 发 PlotQualityWarning）
  → 以最终文件名落盘。返回 out_png 路径；质量数据写入模块变量 LAST_REPORT。

  * 编译一律用 ASCII 中转文件名（坑：cmd 传中文文件名会被 GBK 截断），产出 PNG 后
    再以中文名落盘——对调用方完全透明。
  * 工具链解析：优先 PATH，回退绝对路径（TinyTeX bin / tlgs / Asymptote 安装目录），
    并在进程级自动补 GS_LIB / ASYMPTOTE_DIR / ASYMPTOTE_GS（不改系统设置）。

渲染自检清单（双后端口径；每次出图逐项过目，结论落报告）
--------------------------------------------------------
1. 符号正确性：物理量符号/下标/单位标注与题面一致；电路表盘字母（A/V）随导线方向
   正立不倒置（仪表保持水平放置）；力学箭头方向与力名对应；折射角数值与
   sinθ₂=sinθ₁/n 计算一致——TikZ 模板的实算值同时写进源码注释，便于对账；渲染后
   放大目检。
2. 遮挡关系：3D 图遮挡层次由 Asymptote 引擎处理，但 visible/hidden 边列表仍是人工
   判定——逐棱核对：被遮挡棱相邻面须全部背向视点方为真遮挡，虚线不得标到可见棱上。
3. 标签避让：标签不压线、不压节点、不出图幅；顶点标签缺省取离形心 compass 八向，
   投影极值点（最右/最下）手工内收；思维导图节点由叶槽均分保证不重叠——放大目检。
4. 直角记号：两边必须贴线不悬空。Asy 立体图用「屏幕等效构造」：竖直边取 Z 向、水平
   边取底面内垂直于视线方位的方向（正交投影+up=Z 下二者投影恰为屏幕水平/竖直且互相
   垂直，记号不退化——禁止取指向观察者的方向）；平面图 tkzMarkRightAngle 须核对
   顶点顺序（中点为直角顶）与尺寸；渲染后放大目检贴线。
5. 灰度打印对比度：render() 自动检查 PNG L 通道——底色取直方图众数，墨迹（L<底色−30）
   最深 5% 分位与底色对比 ≥0.35，不足发 PlotQualityWarning（每图一次，不阻断落盘）。
6. 图内字号：模板统一 \\small（10pt 基准下 9pt；dpi=150 下约 19px，为五号 10.5pt
   视觉高的 86%）；下限＝五号视觉高的 70%≈7.35pt，模板不得用 \\footnotesize 以下，
   违例改图而非缩字号。

使用示例
--------
>>> import 绘图模板库 as tpl
>>> spec = tpl.circuit_voltammetry()
>>> tpl.render(spec, r"D:\\图\\伏安法电路.png", dpi=150)   # doctest: +SKIP
"""
from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import tempfile
import uuid
import warnings
from pathlib import Path

import numpy as np

__all__ = [
    "PlotQualityWarning", "MIN_GRAY_CONTRAST", "LAST_REPORT",
    "circuit_voltammetry", "force_incline", "motion_graph", "optics_refraction",
    "mindmap_tree", "tikz_raw", "polyhedron_3d",
    "render", "check_grayscale",
]

MIN_GRAY_CONTRAST = 0.35     # 灰度墨迹/底色对比下限（与 mpl 版口径一致）
LAST_REPORT: dict = {}       # 最近一次 render() 的质量数据


class PlotQualityWarning(UserWarning):
    """绘图质量自检告警（灰度对比度不足等）。不阻断落盘。"""


# =========================================================================
# 工具链定位与环境（TinyTeX / tlgs / Asymptote，全部用户级安装）
# =========================================================================

_APPDATA = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
_LOCAL = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
_TINYTEX = _APPDATA / "TinyTeX"
_TEXBIN = _TINYTEX / "bin" / "windows"
_TLGS = _TINYTEX / "tlpkg" / "tlgs"
_ASY_DIR = _LOCAL / "Programs" / "Asymptote"


def _resolve(name: str, fallbacks) -> Path:
    """按 PATH → 绝对回退清单解析可执行文件；找不到抛 RuntimeError。"""
    hit = shutil.which(name)
    if hit:
        return Path(hit)
    for cand in fallbacks:
        if Path(cand).exists():
            return Path(cand)
    raise RuntimeError("找不到可执行文件 %r，且回退路径均不存在: %s" % (name, fallbacks))


def _tool_env() -> dict:
    """子进程环境：补 PATH、GS_LIB、ASYMPTOTE_DIR、ASYMPTOTE_GS（进程级，不改系统）。"""
    env = dict(os.environ)
    add = []
    if _TEXBIN.exists():
        add.append(str(_TEXBIN))
    if _ASY_DIR.exists():
        add.append(str(_ASY_DIR))
    if add:
        env["PATH"] = ";".join(add + [env.get("PATH", "")])
    gs = _resolve("gswin64c", [_TLGS / "bin" / "gswin64c.exe"])
    if "GS_LIB" not in env and _TLGS.exists():
        env["GS_LIB"] = ";".join(str(_TLGS / sub) for sub in
                                 ("Resource\\Init", "lib", "Resource", "fonts", "kanji"))
    env.setdefault("ASYMPTOTE_GS", str(gs))
    env.setdefault("ASYMPTOTE_DIR", str(_ASY_DIR))
    return env


def _run(cmd, cwd: Path, env: dict, timeout: int):
    p = subprocess.run([str(c) for c in cmd], cwd=str(cwd), env=env,
                       capture_output=True, timeout=timeout)
    out = (p.stdout or b"") + (p.stderr or b"")
    return p.returncode, out.decode("utf-8", errors="replace")


def _tail(text: str, lines: int = 14) -> str:
    rows = [ln for ln in text.splitlines() if ln.strip()]
    return "\n".join(rows[-lines:])


def _compile_xelatex(tex_path: Path, env: dict, timeout: int) -> Path:
    xelatex = _resolve("xelatex", [_TEXBIN / "xelatex.exe"])
    code, txt = _run([xelatex, "-interaction=nonstopmode", "-halt-on-error",
                      tex_path.name], cwd=tex_path.parent, env=env, timeout=timeout)
    pdf = tex_path.with_suffix(".pdf")
    if code != 0 or not pdf.exists():
        log = ""
        logf = tex_path.with_suffix(".log")
        if logf.exists():
            log = _tail(logf.read_text(encoding="utf-8", errors="replace"))
        raise RuntimeError("xelatex 编译失败 (%s):\n%s\n%s"
                           % (tex_path.name, _tail(txt), log))
    return pdf


def _compile_asy(asy_path: Path, env: dict, timeout: int) -> Path:
    asy = _resolve("asy", [_ASY_DIR / "asy.exe"])
    # 坑：asy 的 -o 会自动追加扩展名（-o x.pdf → x.pdf.pdf），故只传主名；
    # GS_LIB 必须在环境里（asy 子进程调 Ghostscript 处理标签）。
    code, txt = _run([asy, "-f", "pdf", "-o", asy_path.stem, asy_path.name],
                     cwd=asy_path.parent, env=env, timeout=timeout)
    pdf = asy_path.with_suffix(".pdf")
    if code != 0 or not pdf.exists():
        raise RuntimeError("Asymptote 编译失败 (%s):\n%s"
                           % (asy_path.name, _tail(txt)))
    return pdf


def _pdf_to_png(pdf: Path, png: Path, dpi: int, env: dict, timeout: int) -> None:
    gs = _resolve("gswin64c", [_TLGS / "bin" / "gswin64c.exe"])
    code, txt = _run([gs, "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=png16m",
                      "-r%d" % dpi, "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4",
                      "-sOutputFile=%s" % png.name, pdf.name],
                     cwd=pdf.parent, env=env, timeout=timeout)
    if code != 0 or not png.exists():
        raise RuntimeError("gswin64c PDF→PNG 失败 (%s):\n%s" % (pdf.name, _tail(txt)))


# =========================================================================
# 灰度对比度检查（PIL L 通道）
# =========================================================================

def check_grayscale(png_path) -> dict:
    """L 通道灰度检查：底色=直方图众数；墨迹=L<底色−30 的像素；文字区取墨迹最深
    5% 分位；对比=(底色−墨深)/255 <0.35 发 PlotQualityWarning（每图一次）。
    返回 dict(bg, text_L, contrast, ink_frac)。"""
    from PIL import Image
    arr = np.asarray(Image.open(str(png_path)).convert("L"))
    hist = np.bincount(arr.ravel(), minlength=256)
    bg = int(hist.argmax())
    ink = arr < (bg - 30)
    rep = {"bg": bg, "text_L": None, "contrast": None,
           "ink_frac": round(float(ink.mean()), 5)}
    if ink.sum() >= max(50, 5e-4 * arr.size):
        text_L = float(np.percentile(arr[ink], 5))
        contrast = (bg - text_L) / 255.0
        rep["text_L"] = round(text_L, 1)
        rep["contrast"] = round(contrast, 3)
        if contrast < MIN_GRAY_CONTRAST:
            warnings.warn("灰度对比度不足(%s): 墨迹最深处 L=%.0f vs 底色 L=%d, "
                          "对比 %.2f < %.2f（灰度打印易糊）"
                          % (Path(png_path).name, text_L, bg, contrast, MIN_GRAY_CONTRAST),
                          PlotQualityWarning, stacklevel=2)
    return rep


# =========================================================================
# spec 构造：TikZ 后端
# =========================================================================

_TIKZ_PREAMBLE_HEAD = r"""\documentclass[border=8pt]{standalone}
\usepackage{ctex}
\usepackage{amsmath}
"""
_TIKZ_PREAMBLE_TAIL = "\n\\begin{document}\n"


def _tikz_spec(kind: str, packages, body: str, libraries=()) -> dict:
    """把 tikzpicture 正文包进标准导言区，返回 spec 字典。"""
    libs = ("\\usetikzlibrary{%s}\n" % ",".join(libraries)) if libraries else ""
    doc = (_TIKZ_PREAMBLE_HEAD + "\n".join("\\usepackage{%s}" % p for p in packages)
           + ("\n" + libs if libs else "") + _TIKZ_PREAMBLE_TAIL
           + body.rstrip() + "\n\\end{document}\n")
    return {"backend": "tikz", "kind": kind, "source": doc}


def _fmt(x: float) -> str:
    """浮点 → 紧凑数字串（去掉多余尾零，供注入 TikZ/Asy 坐标）。"""
    s = ("%.4f" % float(x)).rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


# ----------------------------- ① 伏安法电路 -----------------------------

def circuit_voltammetry(*, src_label="电源", switch_label="开关",
                        ammeter_label="$A$", rx_label="$R_x$",
                        voltmeter_label="$V$", show_switch=True,
                        line_width="0.9pt", font=r"\small") -> dict:
    """伏安法测电阻电路（circuitikz，教材惯例布局）。

    布局：电源（左侧竖直）→ 开关 → 电流表 A（顶边串联）→ 待测电阻 Rx（右侧竖直），
    电压表 V 水平并联在 Rx 两端（水平放置保证表盘字母正立——circuitikz 仪表字母随
    导线方向旋转，竖直放置会倒置）。
    """
    sw = "to[nos, l_=%s] " % switch_label if show_switch else ""
    body = r"""\begin{circuitikz}[line width=%s, font=%s]
  %% 主回路：电源 → 开关 → A → Rx
  \draw (0,0) to[battery1, l_=%s, invert] (0,3.6);
  \draw (0,3.6) %s(2.4,3.6);
  \draw (2.4,3.6) to[ammeter, l_=%s] (4.9,3.6);
  \draw (4.9,3.6) -- (6.6,3.6);
  \draw (6.6,3.6) to[R, l_=%s] (6.6,0);
  \draw (6.6,0) -- (0,0);
  %% 电压表 V 水平并联在 Rx 两端
  \draw (6.6,3.6) -- (8.6,3.6) to[voltmeter, l_=%s] (10.6,3.6) -- (10.6,0) -- (6.6,0);
\end{circuitikz}""" % (line_width, font, src_label, sw, ammeter_label,
                       rx_label, voltmeter_label)
    return _tikz_spec("circuit_voltammetry", ["circuitikz"], body)


# ----------------------------- ② 斜面滑块受力 -----------------------------

def force_incline(*, base=6.0, height=2.5, block_pos=0.38, block_w=1.5, block_h=0.9,
                  theta_label=r"$\theta$", f_gravity=r"$mg$", f_normal=r"$N$",
                  f_friction=r"$f$", show_hatch=True, font=r"\small") -> dict:
    """斜面滑块受力分析（tkz-euclide）。

    斜面直角三角形 A(左下)-B(右下,直角)-C(右上)；滑块贴合斜面，自滑块中心 S 出发
    三箭头：mg 竖直向下、N 垂直斜面斜向上、f 沿斜面向上；直角记号两处（底角 B、
    接触点 M 处——画在斜面下侧避免压滑块）；倾角 θ 标在 A 处（斜面与底面夹角）。
    """
    tx, ty = float(base), float(height)
    incli = math.degrees(math.atan2(ty, tx))
    hatch = r"""  %% 斜面阴影短线（沿 AC 均布）
  \foreach \t in {0.08,0.18,...,0.92}{
    \tkzDefPointOnLine[pos=\t](A,C)\tkzGetPoint{Ht}
    \draw (Ht) -- ++({\incli+270}:0.22);
  }""" if show_hatch else "  %% （无斜面阴影）"
    body = r"""\begin{tikzpicture}[scale=1.0, font=%s, >=Stealth]
  \tkzDefPoints{0/0/A, %s/0/B, %s/%s/C}
  \pgfmathsetmacro{\incli}{%s} %% 斜面倾角（度）
  \tkzDrawPolygon[thick](A,B,C)
%s
  %% θ 角（斜面与底面夹角，A 处；普通弧+标签，不用 tkzMarkAngle——
  %% 其 size/mark 键在本版本下会画出整圆，见调试记录）
  \draw[thin] ($(A)+(0:1.3)$) arc[start angle=0, end angle=\incli, radius=1.3];
  \node at ($(A)+({\incli/2}:1.8)$) {%s};
  %% 滑块（沿斜面旋转的矩形），S=滑块中心
  \tkzDefPointOnLine[pos=%s](A,C)\tkzGetPoint{M}
  \begin{scope}[rotate around={\incli:(M)}]
    \draw[thick, fill=gray!25] (M) rectangle ++(%s,%s);
    \coordinate (S) at ($(M)+(%s,%s)$);
  \end{scope}
  %% 三力自滑块中心 S：mg 竖直向下 / N 垂直斜面 / f 沿斜面向上
  \draw[->, thick] (S) -- ++(-90:2.3) node[below]{%s};
  \draw[->, thick] (S) -- ++({\incli+90}:2.0) node[above left]{%s};
  \draw[->, thick] (S) -- ++(\incli:1.9) node[above right]{%s};
  %% 直角记号：接触点 M 处（画在斜面下侧，不压滑块）
  \coordinate (Pq1) at ($(M)+(\incli:0.62)$);
  \coordinate (Pq2) at ($(M)+(\incli-90:0.62)$);
  \tkzMarkRightAngle[size=0.24](Pq1,M,Pq2);
  %% 直角记号：底角 B
  \tkzMarkRightAngle[size=0.3](A,B,C);
\end{tikzpicture}""" % (font, _fmt(tx), _fmt(tx), _fmt(ty), _fmt(incli),
                        hatch, theta_label, _fmt(block_pos), _fmt(block_w),
                        _fmt(block_h), _fmt(block_w / 2), _fmt(block_h / 2),
                        f_gravity, f_normal, f_friction)
    return _tikz_spec("force_incline", ["tkz-euclide"], body)


# ----------------------------- ③ 运动图像 -----------------------------

def motion_graph(points=((0, 0), (4, 8), (5.5, 8)), *,
                 xlabel=r"$t/\mathrm{s}$",
                 ylabel=r"$v/(\mathrm{m\cdot s^{-1}})$",
                 xticks=None, yticks=None, guides=True,
                 guide_label=None, line_width="1.6pt", font=r"\small") -> dict:
    """运动图像（pgfplots 两段折线 v-t，教材惯例）。

    points: 折线顶点 [(t,v),...]（两段＝3 点；更多点同样支持）。坐标轴过原点带箭头，
    轴端标物理量/单位（如 v/(m·s⁻¹)）；折线内点自动画虚线引导线到两轴。
    guide_label: (t, v, 文本) 可在折点旁加注（如状态说明）。
    """
    pts = [(float(t), float(v)) for t, v in points]
    tmax = max(t for t, _ in pts)
    vmax = max(v for _, v in pts)
    xmax, ymax = round(tmax * 1.18, 3), round(vmax * 1.3, 3)
    if xticks is None:
        xticks = sorted({t for t, _ in pts if 0 < t and float(t).is_integer()}
                        | {int(xmax)}) if xmax <= 10 else None
    if yticks is None:
        step = 2 if vmax > 5 else 1
        yticks = list(range(step, int(ymax), step))
    coords = " ".join("(%s, %s)" % (_fmt(t), _fmt(v)) for t, v in pts)
    guide_lines = []
    if guides:
        for t, v in pts[1:-1]:
            if t > 0:
                guide_lines.append(
                    r"\draw[dashed, black!45, thin] (axis cs:%s,0) -- (axis cs:%s,%s);"
                    % (_fmt(t), _fmt(t), _fmt(v)))
            if v > 0:
                guide_lines.append(
                    r"\draw[dashed, black!45, thin] (axis cs:0,%s) -- (axis cs:%s,%s);"
                    % (_fmt(v), _fmt(t), _fmt(v)))
    label_lines = []
    if guide_label:
        lt, lv, ltxt = guide_label
        label_lines.append(r"\node[anchor=west, font=%s] at (axis cs:%s,%s) {%s};"
                           % (font, _fmt(lt), _fmt(lv), ltxt))
    xt = ("xtick={%s}, " % ",".join(_fmt(t) for t in xticks)) if xticks else ""
    yt = ("ytick={%s}, " % ",".join(_fmt(v) for v in yticks)) if yticks else ""
    body = r"""\pgfplotsset{compat=1.18} %% 不设 compat 会落入兼容模式，轴端标签不显示
\begin{tikzpicture}[font=%s]
\begin{axis}[
  width=7.6cm, height=6.0cm,
  axis lines=middle,
  xmin=0, xmax=%s, ymin=0, ymax=%s,
  xlabel={%s}, ylabel={%s},
  %s%s
  tick label style={font=%s},
  label style={font=%s},
  every axis x label/.style={at={(current axis.right of origin)}, anchor=west},
  every axis y label/.style={at={(current axis.above origin)}, anchor=south},
  clip=false,
]
  \addplot[line width=%s, black] coordinates {%s};
%s
%s
\end{axis}
\end{tikzpicture}""" % (font, _fmt(xmax), _fmt(ymax), xlabel, ylabel, xt, yt,
                        font, font, line_width, coords,
                        ("\n".join(guide_lines)) if guide_lines else "% 无引导线",
                        ("\n".join(label_lines)) if label_lines else "% 无折点标注")
    return _tikz_spec("motion_graph", ["pgfplots"], body)


# ----------------------------- ④ 折射光路 -----------------------------

def optics_refraction(*, n=1.5, theta1_deg=40.0, medium1="空气", medium2="玻璃",
                      ray_len=3.1, half_width=4.0, depth=2.6,
                      show_labels=True, font=r"\small") -> dict:
    """折射光路（TikZ；折射角按 sinθ₂=sinθ₁/n 实算并标角度弧）。

    界面水平、法线竖直虚线；入射光自左上入射到界面上 O 点，折射光进入下方介质；
    θ₁/θ₂ 角度弧与标签、介质名称标注。折射角在 Python 侧实算（斯涅尔定律），
    数值同时写入源码注释（源码即图，可对账）。
    """
    th1 = float(theta1_deg)
    if not (0 < th1 < 90):
        raise ValueError("theta1_deg 须在 (0,90)")
    s2 = math.sin(math.radians(th1)) / float(n)
    if s2 >= 1.0:
        raise ValueError("sinθ1/n = %.4f ≥ 1，发生全反射，无折射角" % s2)
    th2 = math.degrees(math.asin(s2))
    L = float(ray_len)
    ix, iy = -L * math.sin(math.radians(th1)), L * math.cos(math.radians(th1))
    rx, ry = L * math.sin(math.radians(th2)), -L * math.cos(math.radians(th2))

    def polar(deg, r):
        return "(%s, %s)" % (_fmt(r * math.cos(math.radians(deg))),
                             _fmt(r * math.sin(math.radians(deg))))

    arc1_a = polar(90, 0.85)
    arc2_a = polar(270, 0.75)
    lab1 = polar(90 + th1 / 2, 1.18)
    lab2 = polar(270 + th2 / 2, 1.05)
    mid_i = "(%s, %s)" % (_fmt(ix * 0.52), _fmt(iy * 0.52))     # 入射光箭头位置
    mid_r = "(%s, %s)" % (_fmt(rx * 0.60), _fmt(ry * 0.60))     # 折射光箭头位置
    normal_top = "(0, %s)" % _fmt(L * math.cos(math.radians(th1)) + 0.55)
    normal_bot = "(0, %s)" % _fmt(-depth - 0.35)

    med_nodes = ""
    if show_labels:
        med_nodes = r"""  \node at (%s, 0.36) {%s};
  \node at (%s, -0.42) {%s};
""" % (_fmt(-half_width + 0.55), medium1, _fmt(half_width - 0.55), medium2)

    body = r"""\begin{tikzpicture}[scale=1.0, font=%s, >=Stealth]
  %% 实算：sinθ2 = sinθ1/n = sin(%s°)/%s = %s → θ2 = %s°（斯涅尔定律，已核）
  %% 下方介质淡色填充 + 界面
  \fill[black!6] (%s, 0) rectangle (%s, %s);
  \draw[thick] (%s,0) -- (%s,0);
%s  %% 法线（竖直虚线）
  \draw[dashed, black!60] %s -- %s node[above]{法线};
  %% 入射光线（自左上到 O，箭头置于中段）
  \draw[thick, ->] (%s, %s) -- %s;
  \draw[thick] %s -- (0,0);
  %% 折射光线（自 O 进入下方介质）
  \draw[thick] (0,0) -- (%s, %s);
  \draw[thick, ->] (0,0) -- %s;
  %% 入射角 θ1 弧（法线上侧，90°→90°+θ1）
  \draw[thin] %s arc[start angle=90, end angle=%s, radius=0.85];
  \node at %s {$\theta_1$};
  %% 折射角 θ2 弧（法线下侧，270°→270°+θ2）
  \draw[thin] %s arc[start angle=270, end angle=%s, radius=0.75];
  \node at %s {$\theta_2$};
  %% 入射点 O
  \fill (0,0) circle (1.6pt);
\end{tikzpicture}""" % (font, _fmt(th1), _fmt(n), _fmt(round(s2, 4)),
                        _fmt(round(th2, 2)),
                        _fmt(-half_width), _fmt(half_width), _fmt(-depth),
                        _fmt(-half_width), _fmt(half_width),
                        med_nodes if med_nodes else "",
                        normal_bot, normal_top,
                        _fmt(ix), _fmt(iy), mid_i, mid_i,
                        _fmt(rx), _fmt(ry), mid_r,
                        arc1_a, _fmt(90 + th1), lab1,
                        arc2_a, _fmt(270 + th2), lab2)
    return _tikz_spec("optics_refraction", ["tikz"], body, libraries=["arrows.meta"])


# ----------------------------- ⑤ 思维导图 -----------------------------

def mindmap_tree(root, tree, *, font=r"\small", root_font=None,
                 slot=1.15, x_l1=4.9, x_l2=10.6, root_x=3.4,
                 root_fill="blue!12", l1_fill="gray!12", l2_fill="white",
                 root_draw="black!70", l1_draw="black!60", l2_draw="black!45",
                 l1_text_width=None, l2_text_width=None, root_anchor="center",
                 l1_font=None, l2_font=None, extra_defs="") -> dict:
    """思维导图/知识结构（TikZ 树：节点框 + 连线，两级）。

    root: 根文本；tree: [(一级文本, [二级文本,...]) 或 一级文本, ...]。
    节点文本按 LaTeX 语法解释（支持 $...$ 数学式）。布局在 Python 侧计算：二级叶子
    （及无子项的一级）纵向均分槽位，一级节点取其子叶 y 均值；连线画在节点之前、
    node-to-node（TikZ 自动落边框），节点不透明填充盖住线头。

    2026-08-31 T5 扩参（章知识结构图生成.py 用，默认值＝原字面输出、零行为变化）：
    root_fill/l1_fill/l2_fill 与 root_draw/l1_draw/l2_draw＝三级节点的填充/边框色
    （xcolor 表达式或 \\definecolor 定义的名，配合 extra_defs 注入定义行）；
    l1_text_width/l2_text_width＝一级/二级节点定宽换行（cm，None＝不定宽）；
    root_anchor＝根节点锚点（"east" 时根从 root_x 向左展开，容纳长节名）；
    l1_font/l2_font＝各级字号覆盖；extra_defs＝置于 tikzpicture 首部的定义行。
    """
    root_font = root_font or font
    l1_font = l1_font or font
    l2_font = l2_font or font
    items = []           # (l1_text, [l2,...])
    for ch in tree:
        if isinstance(ch, (tuple, list)) and len(ch) == 2 \
                and isinstance(ch[1], (list, tuple)):
            items.append((str(ch[0]), [str(s) for s in ch[1]]))
        else:
            items.append((str(ch), []))
    # 槽位分配（自顶向下）
    n_slots = sum(max(1, len(subs)) for _, subs in items)
    total_h = slot * n_slots
    y = total_h
    leaf_y = []          # (owner_index, y)
    solo_y = {}          # owner_index -> y（无子项的一级）
    for i, (_, subs) in enumerate(items):
        if not subs:
            y -= slot
            solo_y[i] = y - slot / 2
        else:
            for _ in subs:
                y -= slot
                leaf_y.append((i, y - slot / 2))
    y_of_l1 = {}
    for i, (_, subs) in enumerate(items):
        if subs:
            y_of_l1[i] = sum(yy for (o, yy) in leaf_y if o == i) / len(subs)
        else:
            y_of_l1[i] = solo_y[i]
    y_root = sum(y_of_l1.values()) / len(y_of_l1)

    L = []
    if extra_defs:
        L.append(extra_defs.rstrip())      # \definecolor 等定义行须在环境外
    L.append(r"\begin{tikzpicture}[")
    L.append(r"  mmroot/.style={draw=%s, line width=1.0pt, rounded corners=3.5pt, fill=%s, inner sep=5pt, font=%s}," % (root_draw, root_fill, root_font))
    tw1 = (", text width=%scm" % _fmt(float(l1_text_width))) if l1_text_width else ""
    tw2 = (", text width=%scm" % _fmt(float(l2_text_width))) if l2_text_width else ""
    L.append(r"  mml1/.style={draw=%s, line width=0.9pt, rounded corners=2.5pt, fill=%s, inner sep=4.5pt, font=%s, align=left%s}," % (l1_draw, l1_fill, l1_font, tw1))
    L.append(r"  mml2/.style={draw=%s, line width=0.8pt, rounded corners=2pt, fill=%s, inner sep=4pt, font=%s, align=left%s}," % (l2_draw, l2_fill, l2_font, tw2))
    L.append(r"]")
    # 连线先画：从父节点名到子节点名（TikZ node-to-node 自动落在边框上）。
    # 由于父节点尚不存在，先用坐标连线（父中心→子中心），节点后画、不透明填充
    # 盖住线头，可见段自然落在边框之间。
    L.append(r"  %% 连线：根 → 一级 → 二级（节点填充不透明，盖住线头）")
    for i, (_, subs) in enumerate(items):
        L.append(r"  \draw[black!55, line width=0.9pt] (%s, %s) -- (%s, %s);"
                 % (_fmt(root_x), _fmt(y_root), _fmt(x_l1 + 0.2), _fmt(y_of_l1[i])))
        for (o, yy) in leaf_y:
            if o == i:
                L.append(r"  \draw[black!55, line width=0.9pt] (%s, %s) -- (%s, %s);"
                         % (_fmt(x_l1 + 0.2), _fmt(y_of_l1[i]),
                            _fmt(x_l2 + 0.2), _fmt(yy)))
    # 节点（后画，盖住线头）
    L.append(r"  %% 节点")
    L.append(r"  \node[mmroot%s] at (%s, %s) {%s};"
             % ("" if root_anchor == "center" else ", anchor=%s" % root_anchor,
                _fmt(root_x), _fmt(y_root), root))
    for i, (t1, subs) in enumerate(items):
        L.append(r"  \node[mml1, anchor=west] at (%s, %s) {%s};"
                 % (_fmt(x_l1), _fmt(y_of_l1[i]), t1))
        for j, s2 in enumerate(subs):
            yy = [yy for (o, yy) in leaf_y if o == i][j]
            L.append(r"  \node[mml2, anchor=west] at (%s, %s) {%s};"
                     % (_fmt(x_l2), _fmt(yy), s2))
    return _tikz_spec("mindmap_tree", ["tikz"], "\n".join(L) + "\n\\end{tikzpicture}")


# ----------------------------- ⑥ tikz 透传 -----------------------------

def tikz_raw(source: str) -> dict:
    """TikZ 透传接口：source 含 \\documentclass 则原样编译；否则包标准导言区
    （standalone + ctex + amsmath + tikz，并载入 arrows.meta 库）。"""
    if "\\documentclass" in source:
        return {"backend": "tikz", "kind": "tikz_raw", "source": source}
    return _tikz_spec("tikz_raw", ["tikz"], source, libraries=["arrows.meta"])


# =========================================================================
# spec 构造：Asymptote 后端（立体几何族）
# =========================================================================

_COMPASS8 = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]


def polyhedron_3d(vertices, edges_visible, edges_hidden=(), *, faces=None,
                  labels=None, extra_labels=(), extra_lines=(), mark_right=None,
                  eye=(5, 4, 2), up="Z", size_cm=7.0) -> dict:
    """简单立体（Asymptote 真遮挡引擎）。

    vertices: {名称: (x,y,z)}（名称即标签文本，建议自带字母；自动转合法 asy 变量名）
    edges_visible / edges_hidden: [(名称, 名称), ...]——hidden 由调用方按视点人工判定
    （相邻面全背向视点方为真遮挡；面/棱遮挡层次由 Asy 引擎处理）。
    faces: [(名称列表, 颜色, 透明度<=0.3), ...] 半透明面。
    labels: {名称: "N"/"SW"/... compass 或 (dx,dy,dz) 偏移}；缺省取顶点相对形心的
            xy 方向 compass 八向。
    extra_labels: [(坐标, 文本, compass 或偏移), ...]（如垂足 O）。
    extra_lines: [((p0),(p1), "solid"/"dashed", 线宽), ...]（如高线 PO）。
    mark_right: dict(foot=..., up=(0,0,1), size=0.14, dir_horizontal=None,
                dashed=True) 垂足直角记号——「屏幕等效构造」：竖直边取 Z 向，水平边
                取底面内垂直于视线方位的方向（正交投影 + up=Z 下二者投影恰为屏幕
                水平/竖直且互相垂直，记号不退化、两边贴线；dir_horizontal 缺省自动
                按 eye 计算，禁止取指向观察者的方向——投影与 up 共线会退化成线段）。
    eye: 视点三元组（正交投影）；up: "Z"。
    """
    names = list(vertices.keys())
    V = {k: tuple(float(c) for c in v) for k, v in vertices.items()}
    cx = sum(v[0] for v in V.values()) / len(V)
    cy = sum(v[1] for v in V.values()) / len(V)
    names_asy = {n: _asyname(n) for n in names}

    def trpl(p):
        return "(%s, %s, %s)" % tuple(_fmt(c) for c in p)

    L = []
    L.append("import three;")
    L.append("settings.render = 0;              // 矢量输出")
    L.append('settings.tex = "pdflatex";')
    L.append("size(%scm, 0);" % _fmt(size_cm))
    ex, ey, ez = (float(c) for c in eye)
    L.append("currentprojection = orthographic(%s, %s, %s, up=%s);"
             % (_fmt(ex), _fmt(ey), _fmt(ez), up))
    L.append("")
    L.append("// 顶点")
    for n in names:
        L.append("triple %s = %s;" % (names_asy[n], trpl(V[n])))
    if faces:
        L.append("")
        L.append("// 半透明面（遮挡层次由引擎处理）")
        for nlist, color, alpha in faces:
            alpha = min(float(alpha), 0.3)
            poly = "--".join(names_asy[t] for t in nlist) + "--cycle"
            L.append("draw(surface(%s), %s + opacity(%s));"
                     % (poly, color, _fmt(alpha)))
    if edges_hidden:
        L.append("")
        L.append("// 被遮挡棱（相邻面全背向视点，人工核对）→ 虚线")
        L.append("pen hiddenEdge = linewidth(1.0) + dashed;")
        L.append("draw(%s, hiddenEdge);" % " ^^ ".join(
            "%s--%s" % (names_asy[a], names_asy[b]) for a, b in edges_hidden))
    if edges_visible:
        L.append("")
        L.append("// 可见棱 → 实线")
        L.append("pen solidEdge = linewidth(1.1);")
        L.append("draw(%s, solidEdge);" % " ^^ ".join(
            "%s--%s" % (names_asy[a], names_asy[b]) for a, b in edges_visible))
    if extra_lines:
        L.append("")
        L.append("// 附加线段")
        for p0, p1, style, lw in extra_lines:
            pen = "linewidth(%s)" % _fmt(lw)
            if style == "dashed":
                pen += " + dashed"
            L.append("draw((%s)--(%s), %s);" % (trpl(p0), trpl(p1), pen))
    if mark_right:
        L.append("")
        L.append("// 垂足直角记号（屏幕等效构造：竖直边取 Z、水平边取⊥视线方位的底面方向）")
        foot = tuple(float(c) for c in mark_right["foot"])
        upv = tuple(float(c) for c in mark_right.get("up", (0, 0, 1)))
        s = float(mark_right.get("size", 0.14))
        dh = mark_right.get("dir_horizontal")
        if dh is None:
            # 视线方位角 phi=atan2(ey,ex)；屏幕右方向 = (-sin phi, cos phi, 0)，
            # 正交投影+up=Z 下其投影恰为屏幕水平方向 → 记号两边贴线不退化。
            phi = math.atan2(ey, ex)
            dh = (-math.sin(phi), math.cos(phi), 0.0)
        dh = tuple(float(c) for c in dh)
        nl = math.hypot(*dh)
        dh = (dh[0] / nl, dh[1] / nl, dh[2] / nl)
        pA = tuple(foot[k] + s * dh[k] for k in range(3))
        pB = tuple(foot[k] + s * (dh[k] + upv[k]) for k in range(3))
        pC = tuple(foot[k] + s * upv[k] for k in range(3))
        pen = "linewidth(0.9)"
        if mark_right.get("dashed", True):
            pen += " + dashed"
        L.append("draw((%s)--(%s) ^^ (%s)--(%s) ^^ (%s)--(%s), %s);"
                 % (trpl(pA), trpl(pB), trpl(pB), trpl(pC),
                    trpl(pC), trpl(foot), pen))
    L.append("")
    L.append("// 顶点标注")
    labels = labels or {}
    for n in names:
        d = labels.get(n)
        if d is None:
            d = _compass_dir(V[n][0] - cx, V[n][1] - cy)
        if isinstance(d, str):
            L.append('label("$%s$", %s, %s);' % (n, names_asy[n], d))
        else:
            L.append('label("$%s$", %s + (%s, %s, %s));'
                     % (n, names_asy[n], _fmt(d[0]), _fmt(d[1]), _fmt(d[2])))
    for item in extra_labels:
        p, txt = item[0], item[1]
        d = item[2] if len(item) > 2 else "SW"
        if isinstance(d, str):
            L.append('label("$%s$", (%s, %s, %s), %s);'
                     % (txt, _fmt(p[0]), _fmt(p[1]), _fmt(p[2]), d))
        else:
            L.append('label("$%s$", (%s, %s, %s) + (%s, %s, %s));'
                     % (txt, _fmt(p[0]), _fmt(p[1]), _fmt(p[2]),
                        _fmt(d[0]), _fmt(d[1]), _fmt(d[2])))
    return {"backend": "asy", "kind": "polyhedron_3d", "source": "\n".join(L) + "\n"}


def _asyname(n: str) -> str:
    """顶点字典键 → 合法 asy 变量名（剥掉 $ 与非法字符）。"""
    m = re.sub(r"[^0-9A-Za-z]", "", n)
    if not m or m[0].isdigit():
        m = "v" + m
    if m in ("three", "triple", "pen", "draw", "label", "surface"):
        m += "_"
    return m


def _compass_dir(dx, dy) -> str:
    """xy 平面方向 → compass 八向（用于缺省标签方向）。"""
    oct_ = int(round(math.atan2(dy, dx) / (math.pi / 4))) % 8
    return _COMPASS8[oct_]


# =========================================================================
# 统一渲染出口
# =========================================================================

def render(spec, out_png, *, dpi=150, grayscale_check=True, timeout=300,
           keep_pdf=False):
    """统一出口：写源文件（sources/ 子目录，源码即图可入 git）→ ASCII 中转名编译
    → gswin64c 转 PNG → 灰度检查 → 中文名落盘。返回 Path(out_png)。

    spec: 模板函数返回的字典（backend=tikz/asy + source）。
    质量数据（bg/text_L/contrast/ink_frac/源文件路径）写入模块变量 LAST_REPORT。
    keep_pdf=True 时另把编译产物 PDF 复制为 out_png 同名 .pdf（2026-08-31 T5 增参，
    供矢量再导出；默认 False 保持原行为）。
    """
    out = Path(out_png)
    backend = spec["backend"]
    source = spec["source"]
    ext = ".tex" if backend == "tikz" else ".asy"
    out.parent.mkdir(parents=True, exist_ok=True)
    sources_dir = out.parent / "sources"
    sources_dir.mkdir(exist_ok=True)
    src_final = sources_dir / (out.stem + ext)          # 中文名源码（git 友好）
    src_final.write_text(source, encoding="utf-8")

    env = _tool_env()
    with tempfile.TemporaryDirectory(prefix="plotv2_") as td:
        stem = "fig_" + uuid.uuid4().hex[:10]           # ASCII 中转名（GBK 坑）
        sp = Path(td) / (stem + ext)
        sp.write_text(source, encoding="utf-8")
        if backend == "tikz":
            pdf = _compile_xelatex(sp, env, timeout)
        elif backend == "asy":
            pdf = _compile_asy(sp, env, timeout)
        else:
            raise ValueError("未知 backend: %r" % backend)
        png_tmp = sp.with_suffix(".png")
        _pdf_to_png(pdf, png_tmp, dpi, env, timeout)
        rep = check_grayscale(png_tmp) if grayscale_check else {}
        shutil.copyfile(str(png_tmp), str(out))         # 中文最终名（Python 层改名，安全）
        if keep_pdf:
            shutil.copyfile(str(pdf), str(out.with_suffix(".pdf")))

    LAST_REPORT.clear()
    LAST_REPORT.update(rep)
    LAST_REPORT.update({"path": str(out), "dpi": dpi, "source": str(src_final),
                        "backend": backend, "kind": spec.get("kind")})
    return out
