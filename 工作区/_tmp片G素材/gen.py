# -*- coding: utf-8 -*-
"""由 geom.json + params.json 生成 image2 重绘 TikZ 片段与预览壳。
   坐标映射：px → mm，k = 42.0mm / 764px（源排印宽 42.0mm、画布 764×764px）；
   Y_mm = (764 - y_px) * k（位图 y 向下 → TikZ y 向上）。"""
import json, io, os
G = json.load(open("geom.json", encoding="utf-8"))
DJ = json.load(open("dot.json", encoding="utf-8"))
P = json.load(open("params.json", encoding="utf-8"))
K = 42.0/764.0
def X(px): return px*K
def Y(px): return (764.0-px)*K
def xy(p): return "(%.3f,%.3f)" % (X(p[0]), Y(p[1]))

V = G["V"]
A   = V["A"]; B = V["B"]; A1 = V["A1"]; B1 = V["B1"]
C   = V["C"]; C1 = V["C1"]; D = V["D"]; D1 = V["D1"]
E   = DJ["E"]
# E 精确取"两线交点"，落在线 A1C1 上
dotr_mm = DJ["dot"][2]*K

fs   = P["fontsize_pt"]
lw   = P["linewidth_mm"]
dash_on, dash_off = P["dash_on_mm"], P["dash_off_mm"]
LO   = P["label_offset_px"]        # 标签微调（px，位图系：+x 右、+y 下）
def lab(name):
    dx, dy = LO.get(name, [0.0,0.0])
    return "(%.3f,%.3f)" % (X(name2px[name][0]+dx), Y(name2px[name][1]+dy))
name2px = {  # 标签墨迹 bbox 中心（源图实测，px）
 "A":[79.5,721.0], "B":[523.5,725.0], "C":[726.5,512.5], "D":[216.0,496.0], "E":[310.5,147.0],
 "A1":[49.0,231.0], "B1":[582.5,287.0], "C1":[713.0,59.0], "D1":[244.0,47.5]}

body = r"""%% ============================================================
%% image2 重绘（探三例1 · 正方体 ABCD-A_1B_1C_1D_1，E 在 A_1C_1 上）——TikZ 矢量片段
%% 仅依赖 tikz。源自位图：工作区/字替对照-0909/variantF/media/media/image2.png（764×764px）
%% 源排印宽 42.0mm ⇒ 1px = 42/764 = %.6f mm（本片段 x=1mm,y=1mm，坐标已按此折算）
%% 线宽：源图实测 5.5~5.75px（竖/横各向异性）取 5.6px ⇒ %.4f mm ≈ %.2f pt
%% 虚线：源图实测 on 22px / off 15.5px ⇒ on %.3fmm off %.3fmm（周期 %.3fmm）
%% 点 E：源图实心圆 r=8.58px ⇒ r=%.3fmm（直径 %.2fmm），圆心落在 A_1C_1 上
%% 标签：源自全品图=Times 系斜体变量＋直立下标；本片 $\mathit{X}_{\mathrm{1}}$（\mathit 走主字体斜体＝
%%       Times New Roman Italic、\mathrm 走主字体直立数字，贴源图观感）；字号 %.2fpt（源图大写 A 高
%%       63px⇒%.3fmm，已写入 every node 的 font=，宿主无需另设字号）。若宿主数学体本身即 Times 系
%%       （unicode-math+Termes/XITS），可整体换回惯用的 $X_{1}$；下标比例差见核对表§偏差
%% 注：题面 A_1E=¼A_1C_1，而源位图实测 E 落在 t=0.315（绘图不精确）；本片按位图复刻 t=0.315。
%%       若须贴题面精确 ¼：把 \coordinate (E) 改为 ($(A1)!0.25!(C1)$)。
%% 顶点（源图像素，子像素实测）：A(%.2f,%.2f) B(%.2f,%.2f) A1(%.2f,%.2f) B1(%.2f,%.2f)
%%        C(%.2f,%.2f) C1(%.2f,%.2f) D(%.2f,%.2f) D1(%.2f,%.2f) E(%.2f,%.2f)
%% 实线：AB BC CC1 C1B1 B1B BA1 A1A A1D1 D1C1 A1C1 ；虚线：AD DC DD1 AE
%% ============================================================
\begin{tikzpicture}[x=1mm,y=1mm,line width=%.3fmm,line cap=butt,line join=miter,
                    every node/.style={font=\fontsize{%spt}{%spt}\selectfont}]
%% ---- 坐标（mm，原点=位图左上角，y 向上） ----
\coordinate (A)  at %s;\coordinate (B)  at %s;
\coordinate (A1) at %s;\coordinate (B1) at %s;
\coordinate (C)  at %s;\coordinate (C1) at %s;
\coordinate (D)  at %s;\coordinate (D1) at %s;
\coordinate (E)  at %s;   %% E = 线 A1C1 ∩ 线 AE（源图 t=0.315，见核对表）
%% ---- 虚线（隐藏棱 AD、DC、DD1 与辅助线 AE）----
\def\qon{%.3fmm}\def\qoff{%.3fmm}
\draw[dash pattern=on \qon off \qoff, dash phase=%.3fmm] (A)--(D);    %% 首段墨迹距 A 36.9px
\draw[dash pattern=on \qon off \qoff, dash phase=%.3fmm] (D)--(C);    %% 自 D 起 22.5px 起墨
\draw[dash pattern=on \qon off \qoff, dash phase=%.3fmm] (D)--(D1);   %% 相位按 dash 中心拟合（自 D 起第1段中心 30.25px）
\draw[dash pattern=on \qon off \qoff, dash phase=%.3fmm] (A)--(E);    %% 首段墨迹距 A 36.6px
%% ---- 实线：前面 ABB1A1、右面 BCC1B1、上面 A1B1C1D1、对角线 A1C1 ----
\draw (A)--(B)--(C)--(C1)--(B1)--(A1)--(A)--cycle;   %% 外轮廓：A-B、B-C、C-C1、C1-B1、B1-A1、A1-A
\draw (B)--(B1);                                     %% 前面右竖棱 B-B1
\draw (A1)--(D1)--(C1);                              %% 上面后两条可见棱
\draw (A1)--(C1);                                    %% 上面对角线（E 所在）
%% ---- 点 E（实心圆）----
\fill (E) circle[radius=%.3fmm];
%% ---- 标签 ----
\node at %s {$\mathit{A}$};
\node at %s {$\mathit{B}$};
\node at %s {$\mathit{C}$};
\node at %s {$\mathit{D}$};
\node at %s {$\mathit{E}$};
\node at %s {$\mathit{A}_{\mathrm{1}}$};
\node at %s {$\mathit{B}_{\mathrm{1}}$};
\node at %s {$\mathit{C}_{\mathrm{1}}$};
\node at %s {$\mathit{D}_{\mathrm{1}}$};
%% ---- 外框＝源排印幅面 42x42mm（与源位图 764x764px 同幅；不含图形，只定画布大小，
%%      比节点自然外框（44.7x43.5mm）更贴源幅面。集成方若要“紧框”，删掉这两行即可） ----
\pgfresetboundingbox
\path[use as bounding box] (0,0) rectangle (42,42);
\end{tikzpicture}
""" % (K, lw, lw/0.35146, dash_on, dash_off, dash_on+dash_off, dotr_mm, 2*dotr_mm,
       fs, 62.3*K,
       A[0],A[1], B[0],B[1], A1[0],A1[1], B1[0],B1[1],
       C[0],C[1], C1[0],C1[1], D[0],D[1], D1[0],D1[1], E[0],E[1],
       lw, fs, fs*1.2,
       xy(A), xy(B), xy(A1), xy(B1), xy(C), xy(C1), xy(D), xy(D1), xy(E),
       dash_on, dash_off, (37.5-36.9)*K, (37.5-22.5)*K, 7.25*K, (37.5-36.6)*K,
       dotr_mm,
       lab("A"), lab("B"), lab("C"), lab("D"), lab("E"), lab("A1"), lab("B1"), lab("C1"), lab("D1"))
open("image2_重绘.tex","w",encoding="utf-8").write(body)
json.dump({k:[X(v[0]), Y(v[1])] for k,v in list(V.items())+[("E",E)]} | {"_K":K},
          open("coords.json","w",encoding="utf-8"), indent=1)

wrap = r"""%% 预览壳（仅为出样/对照用；集成时不需要）
\documentclass[border=0pt]{standalone}
\usepackage{fontspec}\setmainfont{Times New Roman}
\usepackage{tikz}
\begin{document}
\input{image2_重绘.tex}\unskip   % \unskip 吃掉片段文件末尾换行产生的空格（仅预览壳需要）
\end{document}
"""
open("image2_重绘_预览壳.tex","w",encoding="utf-8").write(wrap)
print("生成 image2_重绘.tex / image2_重绘_预览壳.tex")
