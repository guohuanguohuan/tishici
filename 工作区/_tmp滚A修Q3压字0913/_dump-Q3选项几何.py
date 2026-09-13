# -*- coding: utf-8 -*-
"""滚A 第1页 栏1 Q3 选项区 span 逐条几何 dump（旧版 vs 新版）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

NEW = r"C:\提示词\工作区\M2-第1章量产0911\成卷\滚动卷\滚A\main.pdf"
OLD = r"C:\提示词\工作区\_tmp滚A修Q3压字0913\_probe-旧版\main.pdf"
MM = 72 / 25.4
Y0, Y1 = 100.0, 132.0          # Q3 题干＋选项所在 y 带（mm）
X1 = 132.0                      # 栏1 右界（mm）


def dump(tag, pdf):
    d = pymupdf.open(pdf)
    pg = d[0]
    print("=" * 76)
    print(f"[{tag}]")
    rows = []
    for blk in pg.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            if not (Y0 <= ln["bbox"][1] / MM <= Y1):
                continue
            for s in ln["spans"]:
                if s["bbox"][0] / MM > X1:
                    continue
                rows.append((round(s["bbox"][1] / MM, 1), round(s["bbox"][0] / MM, 2),
                             round(s["bbox"][2] / MM, 2), s["text"]))
    for y, x0, x1, t in sorted(rows):
        print(f"  y={y:6.1f}  x=[{x0:6.2f} → {x1:6.2f}]  w={x1-x0:5.2f}mm  «{t}»")
    # 真压字判据：同 y 带内、相邻 span x 区间相交 > 1.0mm（排除组合字符上标）
    print("  --- 同 y 带 x 区间相交对（>1.0mm）---")
    n = 0
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            if abs(a[0] - b[0]) > 1.5:
                continue
            ov = min(a[2], b[2]) - max(a[1], b[1])
            if ov > 1.0:
                n += 1
                print(f"    y≈{a[0]} 重叠={ov:.2f}mm «{a[3][:24]}» × «{b[3][:24]}»")
    print("  相交对数 =", n)
    d.close()


dump("旧版（压字红旗）", OLD)
dump("新版（修后）", NEW)
