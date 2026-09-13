# -*- coding: utf-8 -*-
r"""栏高成本-页几何分析：逐栏「栏底/余量」＋「每题回嵌成本」＋越右界明细

`\.jpcol` 是 \raisebox{0pt}[0pt][0pt]{\vtop{…}}（声明高/深均 0pt），
TeX 看不见栏高 → 溢出永不报 Overfull，只能量 PDF 坐标。
本脚本出三张读数表：
  T1 逐页逐栏：原印面栏底 / 印本档栏底 / 增量 / 距版心下沿余量（mm）
  T2 越右界明细（块底超本栏 x 上沿 >3pt 的块，标注是否答案块）
  T3 单个回嵌块的平均栏高成本（增量 ÷ 该栏回嵌键数）
"""
import io, os, re, sys, json
import pymupdf as fitz
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
MM = 72.0 / 25.4
TEXT_BOT = (284.2 - 17.6) * MM
FOOT_Z = 762.0
COLS = [(8.9, 128.9), (139.9, 259.9), (270.9, 390.9)]
BOOKS = [("测评卷", r"测评卷\main.pdf", 19), ("滚动卷A", r"滚动卷\滚A\main.pdf", 16),
         ("滚动卷B", r"滚动卷\滚B\main.pdf", 16)]
out = []


def blocks(doc):
    r = []
    for pno, pg in enumerate(doc, 1):
        for b in pg.get_text("blocks"):
            x0, y0, x1, y1, t = b[0], b[1], b[2], b[3], b[4]
            xc = (x0 + x1) / 2
            col = next((i for i, (a, z) in enumerate(COLS, 1) if a * MM - 8 <= xc <= z * MM + 8), 0)
            r.append({"p": pno, "c": col, "x0": x0, "x1": x1, "y0": y0, "y1": y1,
                      "t": re.sub(r"\s+", "", t)})
    return r


def bottoms(bl):
    d = {}
    for b in bl:
        if b["y0"] >= FOOT_Z or b["c"] == 0:
            continue
        k = (b["p"], b["c"])
        d[k] = max(d.get(k, 0.0), b["y1"])
    return d


for label, rel, nkeys in BOOKS:
    o = fitz.open(os.path.join(SRC, rel))
    m = fitz.open(os.path.join(HERE, label, "main.pdf"))
    p = fitz.open(os.path.join(HERE, label, "main-pure.pdf"))
    bo, bm, bp = blocks(o), blocks(m), blocks(p)
    to, tm, tp = bottoms(bo), bottoms(bm), bottoms(bp)
    out.append("\n## %s（%d 键）\n" % (label, nkeys))
    out.append("### T1 逐栏栏底与余量（pt／余量 mm）\n")
    out.append("| 页:栏 | 原印面 | 纯题档 | 印本档 | 回嵌增量 | 印本档距版心余量 |")
    out.append("|---|---|---|---|---|---|")
    tot_inc = {}
    for k in sorted(set(list(to) + list(tm))):
        a, b2, c = to.get(k, 0), tp.get(k, 0), tm.get(k, 0)
        inc = c - a
        head = (TEXT_BOT - c) / MM
        out.append("| %d:%d | %.0f | %.0f | %.0f | +%.0f | %.1fmm |" % (k[0], k[1], a, b2, c, inc, head))
    out.append("")
    out.append("- 栏底最高（印本档）：p%d:%d = %.0fpt，余 %.1fmm；纯题档栏底最高 p%d:%d = %.0fpt，余 %.1fmm"
               % (*max(tm, key=tm.get), max(tm.values()), (TEXT_BOT - max(tm.values())) / MM,
                  *max(tp, key=tp.get), max(tp.values()), (TEXT_BOT - max(tp.values())) / MM))
    # T2 越右界
    out.append("\n### T2 越右界明细（块右 x1 > 本栏 mm 上界 + 3pt）\n")
    out.append("| 面 | 页:栏 | x1(pt) | 出界(mm) | 块首 16 字 |")
    out.append("|---|---|---|---|---|")
    for tag, bl in (("原印面", bo), ("印本档", bm)):
        for b in bl:
            if b["c"] == 0 or b["y0"] >= FOOT_Z:
                continue
            lim = COLS[b["c"] - 1][1] * MM
            if b["x1"] > lim + 3:
                out.append("| %s | %d:%d | %.0f | +%.2f | %s |"
                           % (tag, b["p"], b["c"], b["x1"], (b["x1"] - lim) / MM, b["t"][:16]))
    # T3 回嵌成本
    ncol = {}
    for k in sorted(set(list(to) + list(tm))):
        ncol[k] = tm.get(k, 0) - to.get(k, 0)
    worst = max(ncol, key=ncol.get)
    out.append("\n### T3 回嵌栏高成本\n")
    out.append("- 全卷栏高增量合计 %.0fpt（= %.1fmm 栏高），最大单栏 p%d:%d +%.0fpt（%.1fmm）"
               % (sum(ncol.values()), sum(ncol.values()) / MM, worst[0], worst[1], ncol[worst], ncol[worst] / MM))
    out.append("- 粗算单键平均成本 %.1fpt（增量合计 ÷ %d 键）；含解析的解答题按 T1 最大栏实测另计"
               % (sum(ncol.values()) / nkeys, nkeys))
    for d in (o, m, p):
        d.close()

txt = "# 测评本试迁·栏高成本与页几何读数\n" + "\n".join(out) + "\n"
open(os.path.join(HERE, "栏高成本读数.md"), "w", encoding="utf-8").write(txt)
print(txt)
