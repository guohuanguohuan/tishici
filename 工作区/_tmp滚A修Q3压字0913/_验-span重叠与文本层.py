# -*- coding: utf-8 -*-
"""滚A Q3 选项压字复验：pymupdf 文本层 span 级重叠扫描（旧版 vs 新版对照）。

判据：同一行内相邻 span 的 bbox 若 x 区间相交超过 EPS(pt)，即为压字（重叠）。
向量式完整性：C 项四段（BC/CD/DA/AB）与 D 项两段（BC/BD）须齐全、各自成串。
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

NEW = r"C:\提示词\工作区\M2-第1章量产0911\成卷\滚动卷\滚A\main.pdf"
OLD = r"C:\提示词\工作区\_tmp滚A修Q3压字0913\_probe-旧版\main.pdf"
EPS = 0.5           # 允许 0.5pt 以内的贴边，超出算重叠
MM = 72 / 25.4


def lines_of(pdf, pno=0):
    d = pymupdf.open(pdf)
    pg = d[pno]
    out = []
    for blk in pg.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            spans = [(s["bbox"], s["text"]) for s in ln["spans"]]
            out.append({"y": ln["bbox"][1], "spans": spans})
    d.close()
    return out


def overlaps(line):
    """返回该行内所有 x 区间相交超 EPS 的 span 对。"""
    res = []
    sp = sorted(line["spans"], key=lambda t: t[0][0])
    for i in range(len(sp)):
        for j in range(i + 1, len(sp)):
            a, b = sp[i][0], sp[j][0]
            # 需 y 方向也相交才算真压字
            yov = min(a[3], b[3]) - max(a[1], b[1])
            xov = min(a[2], b[2]) - max(a[0], b[0])
            if xov > EPS and yov > EPS:
                res.append((round(xov / MM, 2), sp[i][1], sp[j][1]))
    return res


def q3_lines(pdf):
    """抓 Q3 选项行：含 A．BD→DA 或 C．BC 的行（栏1，x<130mm）。"""
    d = pymupdf.open(pdf)
    pg = d[0]
    hits = []
    for blk in pg.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            txt = "".join(s["text"] for s in ln["spans"])
            if ("基底" in txt) or (ln["bbox"][0] < 130 * MM and ("．" in txt and any(
                    k in txt for k in ("BD", "AB", "AC", "BC", "CD", "DA")))):
                hits.append((round(ln["bbox"][0] / MM, 1), round(ln["bbox"][1] / MM, 1), txt))
    d.close()
    return hits


for tag, pdf in (("旧版(压字)", OLD), ("新版(修后)", NEW)):
    print("=" * 78)
    print(f"[{tag}] {pdf}")
    ls = lines_of(pdf)
    bad = [(l["y"] / MM, o) for l in ls for o in overlaps(l)]
    print("全页 span 重叠对数 =", len(bad))
    for y, o in bad[:6]:
        print(f"   y={y:.1f}mm  重叠={o[0]}mm  «{o[1][:38]}» × «{o[2][:38]}»")
    print("-- Q3 相关行（x/y 单位 mm，栏1 x≈8.9~129）--")
    for x, y, t in q3_lines(pdf):
        print(f"   x={x:6.1f} y={y:6.1f}  {t}")
