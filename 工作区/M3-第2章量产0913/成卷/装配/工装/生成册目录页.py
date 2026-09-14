# -*- coding: utf-8 -*-
# M3 S6 工装④ 生成册目录页.py ——册目录页页码列生成器（装配方案.md §二.1「先内容后页码禁手工维护」）
# 口径：件级行页码＝装配读数.json 实测 start；节级行页码＝该节域首件实测 start（P 前缀统一）；
#   本带（章级）不设页码列（§11 明文）。双档各出一版（main-true.tex／main-false.tex），
#   行/节结构同构、仅页码列换源。工具/节页码定位.py 系 docx 件定位器（Word COM），
#   M3 全 LaTeX 链下同纪律改由本生成器从装配读数同源生成——节行页码零手填。
# 版式零件＝工装③ 册目录页骨架-main.tex 六宏（M2 零改动拷入 册目录页/qp-*.tex）；行序＝装配读数序（C1 源）。
# 编译断言：xelatex×2 三零＋3 页制（降级顺位已登记：页1 留白压缩档）。
# 用法：python 生成册目录页.py [装配输出目录]
import io, sys, os, re, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pypdf import PdfReader

WS = r"C:\提示词\工作区"
ASM = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WS, "M3-第2章量产0913", "成卷", "装配")
TOC = os.path.join(ASM, "册目录页")

# 节域映射（方案 §二.1：衔接→2.1(01)→2.2(02/03/04/05/06/06B)→2.3(07/08/09)→2.4(10)
#   →2.5(11/12)→2.6(13/14)→2.7(15/16)→2.8(17/18)→章末(19)；本一/本二同域）
#   件序名 tex=False 用 fmt（课时号→件名前缀），sec_first＝节域首件（节行页码源）
SECS = [
    ("衔接", "2.8 预备", "衔接节", None),
    ("2.1", "坐标法", "课时01", [("1", "坐标法", "课时01")]),
    ("2.2", "直线的方程", "课时02",
     [("2", "直线的倾斜角与斜率", "课时02"), ("3", "直线的方向向量与法向量", "课时03"),
      ("4", "点斜式与斜截式", "课时04"), ("5", "两点式与一般式", "课时05"),
      ("6", "两条直线的位置关系", "课时06"), ("6B", "点到直线的距离（2.2.4）", "课时06B")]),
    ("2.3", "圆的方程与位置关系", "课时07",
     [("7", "圆的方程", "课时07"), ("8", "直线与圆的位置关系", "课时08"), ("9", "圆与圆的位置关系", "课时09")]),
    ("2.4", "曲线与方程", "课时10", [("10", "曲线与方程", "课时10")]),
    ("2.5", "椭圆", "课时11", [("11", "椭圆的标准方程", "课时11"), ("12", "椭圆的几何性质", "课时12")]),
    ("2.6", "双曲线", "课时13", [("13", "双曲线的标准方程", "课时13"), ("14", "双曲线的性质", "课时14")]),
    ("2.7", "抛物线", "课时15", [("15", "抛物线方程", "课时15"), ("16", "抛物线的性质", "课时16")]),
    ("2.8", "压轴综合", "课时17", [("17", "压轴综合一", "课时17"), ("18", "压轴综合二", "课时18")]),
    ("章末", "总结与复习", "课时19", [("19", "章末总结与复习（章末件）", "课时19")]),
]
KE3 = [  # 本三 非课时件行（label, 题名, 件序名）——滚A 射程照实卷 2.1–2.3（滚A main.tex 头注在案）
    ("拓展册", "上册（2.1～2.6.1 域）", "拓展册/上册"),
    ("拓展册", "下册（2.6.2～2.8 域）", "拓展册/下册"),
    ("测评卷", "单元素养测评卷（二）·第二章", "测评卷"),
    ("滚动卷", "A\\quad 第二章（2.1～2.3）", "滚动卷/滚A"),
    ("滚动卷", "B\\quad 第二章（全章）", "滚动卷/滚B"),
]
BAND = [
    ("01", "本一\\quad 导学本",
     "B\\hspace{0.93em}O\\hspace{0.93em}O\\hspace{0.93em}K\\hspace{1.50em}O\\hspace{0.93em}N\\hspace{0.93em}E"),
    ("02", "本二\\quad 练习本",
     "B\\hspace{0.93em}O\\hspace{0.93em}O\\hspace{0.93em}K\\hspace{1.50em}T\\hspace{0.93em}W\\hspace{0.93em}O"),
    ("03", "本三\\quad 测评拓展本",
     "B\\hspace{0.93em}O\\hspace{0.93em}O\\hspace{0.93em}K\\hspace{1.50em}T\\hspace{0.93em}H\\hspace{0.93em}R\\hspace{0.93em}E\\hspace{0.93em}E"),
]

def starts_of(data, mode):
    out = {}
    for book in data["modes"][mode]["books"]:
        for pc in book["pieces"]:
            out.setdefault(book["book"], {})[pc["name"]] = pc["start"]
    return out

def pick(S, bk, prefix):
    cands = [n for n in S[bk] if n.split("-")[0] == prefix]
    assert len(cands) == 1, f"{bk} 前缀 {prefix} 候选 {cands}"
    return cands[0]

def rows_for(S):
    """按装配读数序生成三页行块；返回 (tex行块list, 读数rows)。页码列全部出自 S（零手填）。"""
    L, rows = [], []
    bk1, bk2, bk3 = "本一导学本", "本二练习本", "本三测评拓展本"
    def sec(no, ti, pg):
        L.append("\\tocsec{%s}{%s}{P%d}" % (no if no == "衔接" else no, ti, pg))
        L[-1] = "\\tocsec{%s}{%s}{P%d}" % ("衔\\,\\,接" if no == "衔接" else no, ti, pg)
        rows.append(["sec", no, ti, pg])
    def lesson(no, ti, pg):
        L.append("\\toclesson{%s}{%s}{%d}" % (no, ti, pg)); rows.append(["lesson", no, ti, pg])
    def link(lb, ti, pg):
        L.append("\\toclink{%s}{%s}{%d}" % (lb, ti, pg)); rows.append(["link", lb, ti, pg])
    # 第 1 页：本一带＋本一 32 行（带上收与页 2/3 同款 -3.29mm；留白压缩 2.0/6.0mm 保 3 页制）
    L += ["\\vspace*{2.0mm}", "\\tocheader", "\\vspace{6.0mm}",
          "\\tocchapter{%s}{%s}{%s}" % BAND[0], "\\vspace{-3.29mm}"]
    for no, ti, first, lessons in SECS:
        sec(no, ti, S[bk1][pick(S, bk1, first)])
        if no == "衔接":
            link("衔\\,\\,接", "初等几何必会（预备位）", S[bk1]["衔接节"])
        else:
            for ln, lt, pf in lessons:
                lesson(ln, lt, S[bk1][pick(S, bk1, pf)])
    # 第 2 页：本二 32 行（纯练件名：一概「配套练习」系）
    L += ["\\newpage", "{\\baselineskip=21.06pt", "\\vspace*{-1.00mm}",
          "\\tocchapter{%s}{%s}{%s}" % BAND[1], "\\vspace{-3.29mm}"]
    for no, ti, first, lessons in SECS:
        sec(no, "配套练习（预备位）" if no == "衔接" else ti, S[bk2][pick(S, bk2, first)])
        if no == "衔接":
            link("衔\\,\\,接", "配套练习（预备位）", S[bk2]["衔接节"])
        else:
            for ln, lt, pf in lessons:
                t2 = "配套练习（2.2.4）" if ln == "6B" else ("配套练习（章末件）" if ln == "19" else "配套练习")
                lesson(ln, t2, S[bk2][pick(S, bk2, pf)])
    # 第 3 页：本三带＋5 件行
    L += ["\\newpage", "\\vspace*{-1.00mm}",
          "\\tocchapter{%s}{%s}{%s}" % BAND[2], "\\vspace{-3.29mm}"]
    for lb, ti, nm in KE3:
        link(lb, ti, S[bk3][nm])
    L.append("\\par}")
    return L, rows

PREAMBLE = r"""\documentclass[fontset=none]{ctexart}
\input{qp-fonts.tex}
\input{qp-layout.tex}
\input{qp-parts.tex}
\input{qp-headfoot.tex}
\input{qp-titles.tex}
\input{qp-blocks.tex}
\pagestyle{empty}
\setlength{\parskip}{0pt}
\definecolor{tocA6}{HTML}{A6A6A6}
\definecolor{tocC7}{HTML}{C7C7C7}
\definecolor{toc144}{HTML}{909090}
\definecolor{toc9D}{HTML}{9D9D9D}
\definecolor{tocB0}{HTML}{B0B0B0}
\definecolor{tocCC}{HTML}{CCCCCC}
\definecolor{toc63}{HTML}{636363}
\definecolor{toc20}{HTML}{202020}
\newfontfamily{\toccont}[Path=C:/提示词/工作区/字替对照-0909/variantF/fonts/]{NSC-w850.ttf}
\newfontfamily{\tocnum}[Path=C:/提示词/工作区/字替对照-0909/variantF/fonts/,Height=0.905,Depth=0.212]{NSC-w600.ttf}
\newfontfamily{\tocreglat}[Path=C:/提示词/工作区/字替对照-0909/variantF/fonts/,Height=0.905,Depth=0.212]{NotoSansSC-Regular.otf}
\newfontfamily{\tocpg}[Path=C:/提示词/工作区/字替对照-0909/variantF/fonts/,Height=0.705,Depth=0.212]{NotoSansSC-Regular.otf}
\setCJKfamilyfont{tocreg}[Path=C:/提示词/工作区/字替对照-0909/variantF/fonts/]{NotoSansSC-Regular.otf}
\setCJKfamilyfont{tocbig}[Path=C:/提示词/工作区/字替对照-0909/variantF/fonts/]{NotoSansSC-Black.otf}
\newcommand{\toczs}{\CJKfamily{tocreg}}
\newcommand{\tocmu}{\CJKfamily{tocbig}}
\newcommand{\tocdots}{\leaders\hbox to 0.99mm{\hss\textcolor{tocCC}{\rule[1.05mm]{0.4mm}{0.4mm}}\hss}\hfill}
\newcommand{\tocrow}[3]{\noindent\hbox to \dimexpr\textwidth-4.7mm\relax{%
  \hskip#1#2\hspace{1.6mm}\tocdots\hspace{1.6mm}\makebox[7.5mm][r]{{\tocpg\fontsize{7.6pt}{8.4pt}\selectfont#3}}}\par}
\newcommand{\tocsec}[3]{\tocrow{16.19mm}{{\tocnum\fontsize{8.8pt}{10pt}\selectfont#1}\hspace{0.62em}{\heizhang\fontsize{8.8pt}{10pt}\selectfont#2}}{#3}}
\newcommand{\toclesson}[3]{\tocrow{29.45mm}{{\toczs\tocreglat\fontsize{7.7pt}{9pt}\selectfont 第\,#1\,课时}\hspace{1.45em}{\toczs\fontsize{7.7pt}{9pt}\selectfont#2}}{#3}}
\newcommand{\toclink}[3]{\tocrow{29.45mm}{{\toczs\tocreglat\fontsize{7.7pt}{9pt}\selectfont#1}\hspace{1.45em}{\toczs\fontsize{7.7pt}{9pt}\selectfont#2}}{#3}}
\newcommand{\tocchapter}[3]{\par\nopagebreak\noindent
  \begin{tikzpicture}[x=1mm,y=1mm,overlay]
    \fill[gray122] (5.23,0) rectangle ++(7.4,7.4);
    \node[anchor=center,inner sep=0pt] at (8.93,3.62)
      {\textcolor{white}{\toccont\fontsize{13.5pt}{14pt}\selectfont#1}};
    \node[anchor=base west,inner sep=0pt] at (15.75,3.3)
      {\color{toc20}\heijie\fontsize{11.8pt}{14pt}\selectfont#2};
    \node[anchor=base west,inner sep=0pt] at (15.08,-0.38)
      {\color{toc63}\numpnum\fontsize{6.4pt}{7pt}\selectfont#3};
    \draw[tocB0,line width=0.15mm,dash pattern=on 0.42mm off 0.29mm] (40.64,1.0) -- (170.9,1.0);
  \end{tikzpicture}\par}
\newcommand{\tocheader}{\par\noindent
  \begin{tikzpicture}[x=1mm,y=1mm,overlay]
    \node[anchor=base west,inner sep=0pt] at (4.45,-1.26)
      {\scalebox{0.710}[1.0]{\toccont\fontsize{70.5pt}{70.5pt}\selectfont{\color{tocA6}CO}{\color{tocC7}NTENTS}}};
    \fill[toc144] (108.29,13.2) rectangle ++(6.3,6.8);
    \fill[tocC7] (100.81,5.4) rectangle ++(8.2,8.5);
    \fill[tocA6] (103.65,3.0) rectangle ++(2.5,2.4);
    \node[anchor=base west,inner sep=0pt] at (113.3,1.3)
      {\color{toc63}\tocmu\fontsize{27.8pt}{30pt}\selectfont 目录};
    \fill[toc9D] (136.3,4.9) rectangle ++(1.7,3.0);
    \node[anchor=base west,inner sep=0pt] at (137.8,4.6)
      {\color{toc144}\heibian\fontsize{9pt}{10pt}\selectfont 套装目录};
  \end{tikzpicture}\par}
\begin{document}
\baselineskip=21.06pt
\lineskiplimit=-1pt
\lineskip=0pt
"""

def main():
    with open(os.path.join(ASM, "装配读数.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    all_rows = {}
    for mode in ("true", "false"):
        S = starts_of(data, mode)
        body, rows = rows_for(S)
        all_rows[mode] = rows
        head = ("%% M3 第2章 套装册目录页（S6 装配轮 2026-09-14 正式件·生成器产出，页码列禁手改）\n"
                "%% 生成源＝" + os.path.join(ASM, "装配读数.json") + "（" + mode + " 档实测 start）\n"
                "%% 生成器＝成卷/装配/工装/生成册目录页.py；版式六宏＝M2 零改动拷入；三级结构；\\pagestyle{empty} 不计页\n"
                "%% 3 页制降级顺位①登记（页1 留白 2.0/6.0mm＋带上收 -5.0mm）\n")
        p = os.path.join(TOC, "main-%s.tex" % mode)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(head + PREAMBLE + "\n".join(body) + "\n\\end{document}\n")
        for _ in range(2):
            r = subprocess.run(["xelatex", "-interaction=nonstopmode", "main-%s.tex" % mode],
                               cwd=TOC, capture_output=True)
        with open(os.path.join(TOC, "main-%s.log" % mode), encoding="utf-8", errors="ignore") as fh:
            txt = fh.read()
        err = len(re.findall(r"^! ", txt, re.M)); ovr = txt.count("Overfull"); mch = txt.count("Missing character")
        n = len(PdfReader(os.path.join(TOC, "main-%s.pdf" % mode)).pages)
        n_sec = sum(1 for x in rows if x[0] == "sec"); n_item = len(rows) - n_sec
        ok = (err == 0 and ovr == 0 and mch == 0 and r.returncode == 0 and n == 3)
        print("[%s] 册目录页 main-%s.pdf %d页 err=%d ovr=%d mch=%d rc=%d %s；行数＝节%d＋件%d"
              % (mode, mode, n, err, ovr, mch, r.returncode, "OK" if ok else "**FAIL**", n_sec, n_item))
        if not ok:
            sys.exit(1)
    with open(os.path.join(TOC, "册目录页读数.json"), "w", encoding="utf-8") as fh:
        json.dump({"source": os.path.join(ASM, "装配读数.json"), "modes": all_rows}, fh, ensure_ascii=False, indent=1)
    print("■ 册目录页读数.json 已落", TOC)

if __name__ == "__main__":
    main()
