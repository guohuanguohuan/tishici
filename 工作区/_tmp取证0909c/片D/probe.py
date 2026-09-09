# -*- coding: utf-8 -*-
"""片D 0909c 标定探针：变式标签双字重候选（w700 变 + w450/w500 式）＋w400 现状参照。
口径沿 C组 bianshi.py（zoom5=14.1732px/mm 二值众数＋AA积分；逐字列切分）。"""
import os, subprocess, json
import numpy as np
import pymupdf
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
FONTS = r"C:/提示词/工作区/字替对照-0909/variantF/fonts"
PX5 = 360 / 25.4   # 14.1732 px/mm
EM_MM = 12.03 * 25.4 / 72

TEX = r"""\documentclass[fontset=none]{ctexart}
\usepackage[a4paper,margin=15mm]{geometry}
\setmainfont{Times New Roman}
\xeCJKsetup{CheckSingle=false}
\setCJKfamilyfont{libianb}[Path=fonts/,BoldFont=FY-w700BEVL100.ttf]{FY-w700BEVL100.ttf}
\setCJKfamilyfont{libians}[Path=fonts/,BoldFont=FY-w450BEVL100.ttf]{FY-w450BEVL100.ttf}
\setCJKfamilyfont{libianu}[Path=fonts/,BoldFont=FY-w500BEVL100.ttf]{FY-w500BEVL100.ttf}
\setCJKfamilyfont{libian}[Path=fonts/,BoldFont=FY-w400BEVL100.ttf]{FY-w400BEVL100.ttf}
\newcommand{\libianb}{\CJKfamily{libianb}}
\newcommand{\libians}{\CJKfamily{libians}}
\newcommand{\libianu}{\CJKfamily{libianu}}
\newcommand{\libian}{\CJKfamily{libian}}
\newfontfamily{\libianslat}[Path=fonts/]{FY-w450BEVL100.ttf}
\newfontfamily{\libianulat}[Path=fonts/]{FY-w500BEVL100.ttf}
\newfontfamily{\libianlat}[Path=fonts/]{FY-w400BEVL100.ttf}
% 宏层拆分试验：\liBsplit 以 \liBstop 为界取首字「变」+余部「式N」
\def\liBsplit#1#2\liBstop{{\libianb #1}{\libians\libianslat #2}}
\newcommand{\liBt}[4]{\par\addvspace{6pt}\noindent{\fontsize{12.03pt}{15pt}\selectfont\liBsplit#1\liBstop}%
  \hspace{2.7mm}#2\hspace{2.2mm}#3#4\par}
\newcommand{\liBu}[4]{\par\addvspace{6pt}\noindent{\fontsize{12.03pt}{15pt}\selectfont{\libianb #1}{\libianu\libianulat #2}}%
  \hspace{2.7mm}#3\hspace{2.2mm}#4\par}
\newcommand{\liBw}[4]{\par\addvspace{6pt}\noindent{\fontsize{12.03pt}{15pt}\selectfont{\libian #1}{\libian\libianlat #2}}%
  \hspace{2.7mm}#3\hspace{2.2mm}#4\par}
\begin{document}
\liBt{变式\textbf{1}}{简单(知识点一)}{}{探针A w700+w450 第一行}
\liBt{变式\textbf{1}}{简单(知识点一)}{}{探针A w700+w450 第二行}
\liBu{变}{式\textbf{1}}{简单(知识点一)}{探针B w700+w500 第一行}
\liBu{变}{式\textbf{1}}{简单(知识点一)}{探针B w700+w500 第二行}
\liBw{变}{式\textbf{1}}{简单(知识点一)}{探针C w400 现状参照 第一行}
\liBw{变}{式\textbf{1}}{简单(知识点一)}{探针C w400 现状参照 第二行}
\end{document}
"""

open(OUT + "/probe.tex", "w", encoding="utf-8").write(TEX)
# 字体复制到本目录（临时产物），cwd=片D＋相对文件名——绕开命令行中文路径编码坑
import shutil
os.makedirs(OUT + "/fonts", exist_ok=True)
for fn in ("FY-w700BEVL100.ttf", "FY-w450BEVL100.ttf", "FY-w500BEVL100.ttf", "FY-w400BEVL100.ttf"):
    shutil.copy(f"{FONTS}/{fn}", f"{OUT}/fonts/{fn}")
for i in (1, 2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", "probe.tex"],
                       cwd=OUT, capture_output=True, text=True)
    print(f"pass{i} rc={r.returncode}")
    if r.returncode:
        print((r.stdout + r.stderr)[-1500:]); raise SystemExit(1)

# ---------------- 测量 ----------------
def stroke_stats(gray, bbox, tag):
    """C组口径：bbox=墨迹框；竖笔宽＝二值 run 中位众数＋AA积分中位（行取字高中段）"""
    x0, y0, x1, y1 = bbox
    h, w = y1 - y0 + 1, x1 - x0 + 1
    dark = gray < 128
    runs = []
    for y in range(y0 + int(0.25 * h), y1 - int(0.2 * h)):
        row = dark[y, x0:x1 + 1]
        d = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
        ss, ee = np.where(d == 1)[0], np.where(d == -1)[0]
        for s, e in zip(ss, ee):
            ln = e - s
            if 2 <= ln <= 0.45 * w:
                runs.append((y, x0 + s, x0 + e, ln))
    rep = {'nrun': len(runs)}
    if runs:
        lens = np.array([r[3] for r in runs])
        mode = int(np.median(lens))
        sel = [r for r in runs if abs(r[3] - mode) <= 1]
        ints = []
        for (y, xs, xe, ln) in sel:
            prof = 1.0 - gray[y, max(0, xs - 3):xe + 3].astype(np.float64) / 255.0
            ints.append(prof.sum())
        rep['mode'] = mode
        rep['int'] = float(np.median(ints))
    core = gray[y0:y1 + 1, x0:x1 + 1]
    dk = core[core < 128]
    rep['min_gray'] = int(core.min())
    rep['dens'] = float(dark[y0:y1 + 1, x0:x1 + 1].mean())
    rep['ink_h'] = h
    rep['ink_w'] = w
    print(f"  {tag}: 墨{w}x{h}px mode={rep.get('mode')}px int={rep.get('int', 0):.2f}px "
          f"({rep.get('int', 0)/PX5:.3f}mm={rep.get('int', 0)/PX5/EM_MM:.4f}em) "
          f"dens={rep['dens']:.3f} min={rep['min_gray']}")
    return rep

doc = pymupdf.open(OUT + "/probe.pdf")
page = doc[0]
d = page.get_text('dict')
# 收集每个「变」/「式」span 的 bbox（按 y 分行）
items = []
for bl in d['blocks']:
    for ln in bl.get('lines', []):
        for sp in ln['spans']:
            t = sp['text'].strip()
            if t in ('变', '式') or t.startswith('变'):
                items.append((round(sp['bbox'][1], 1), sp['bbox'][0], t, sp['font'], sp['size'], sp['bbox']))
items.sort()
print('spans:', [(i[0], i[2], i[3]) for i in items])

Z = 5.0
pix = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csGRAY)
g5 = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).copy()
Z2 = 12.0
pix2 = page.get_pixmap(matrix=pymupdf.Matrix(Z2, Z2), colorspace=pymupdf.csGRAY)
g12 = np.frombuffer(pix2.samples, dtype=np.uint8).reshape(pix2.height, pix2.width).copy()

def ink_bbox(g, x0, y0, x1, y1):
    X0, Y0 = max(0, int(x0 * (g.shape[1] / page.rect.width)) - 2), max(0, int(y0 * (g.shape[0] / page.rect.height)) - 2)
    X1, Y1 = min(g.shape[1], int(x1 * (g.shape[1] / page.rect.width)) + 3), min(g.shape[0], int(y1 * (g.shape[0] / page.rect.height)) + 3)
    sub = g[Y0:Y1, X0:X1]
    dk = sub < 128
    ys, xs = np.where(dk)
    if len(xs) == 0:
        return None
    return (X0 + xs.min(), Y0 + ys.min(), X0 + xs.max(), Y0 + ys.max())

def char_boxes(label, gap=3):
    """按列空隙切字符（C组 bianshi.py 同法）"""
    colink = label.any(axis=0)
    xs = np.where(colink)[0]
    if len(xs) == 0:
        return []
    boxes, s, p = [], xs[0], xs[0]
    for v in xs[1:]:
        if v - p > gap:
            boxes.append((s, p)); s = v
        p = v
    boxes.append((s, p))
    out = []
    for x0, x1 in boxes:
        sub = label[:, x0:x1 + 1]
        ys = np.where(sub.any(axis=1))[0]
        out.append((x0, ys.min(), x1, ys.max()))
    return out

results = {}
for (ytop, xleft, t, font, size, bb) in items:
    for g, z, scale in ((g5, 5.0, PX5), (g12, 12.0, 72 * 12 / 25.4)):
        ib = ink_bbox(g, bb[0], bb[1], bb[2], bb[3])
        if ib is None:
            continue
        X0, Y0, X1, Y1 = ib
        sub = g[max(0, Y0 - 2):Y1 + 3, max(0, X0 - 2):X1 + 3]
        cbs = char_boxes(sub < 128)
        for i, cb in enumerate(cbs):
            rep = stroke_stats(sub, cb, f"{t} 字{i}@{z}x y={ytop}")
            rep['px_at_5'] = rep.get('int', 0) * PX5 / scale
            results.setdefault((ytop, t, i), {})[z] = rep
doc.close()
json.dump({f"{k[0]}_{k[1]}_{k[2]}": v for k, v in results.items()},
          open(OUT + "/probe_result.json", "w"), ensure_ascii=False, indent=1, default=float)

print("\n==== 汇总（zoom5 口径 = 14.1732px/mm；字0=变 字1=式 字2=1） ====")
for (ytop, t, i), v in sorted(results.items()):
    r5 = v.get(5.0, {})
    r12 = v.get(12.0, {})
    print(f"y={ytop} {t} 字{i}: zoom5 mode={r5.get('mode')}px int={r5.get('int',0):.2f}px "
          f"| zoom12 int→5x口径={r12.get('px_at_5',0):.2f}px")
