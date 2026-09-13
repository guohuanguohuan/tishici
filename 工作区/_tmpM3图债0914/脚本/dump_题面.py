# -*- coding: utf-8 -*-
"""图债工位：定点抽取 17 处图债题面全文（只读源件）。输出到 源证/题面全文.txt"""
import re, io, os

ROOT = r"C:\提示词\工作区\M3-第2章量产0913\成卷\导学件"
OUT = r"C:\提示词\工作区\_tmpM3图债0914\源证\题面全文.txt"

# (课时目录, 哨行号列表)  ← 图债哨明细.txt 剔注释实测
TARGETS = [
    ("课时02-倾斜角与斜率", [15, 85, 93]),
    ("课时10-2.4曲线与方程", [303]),
    ("课时12-2.5.2椭圆的几何性质", [238]),
    ("课时13-2.6.1双曲线的标准方程", [257]),
    ("课时14-2.6.2双曲线性质", [281, 436, 487, 564, 573, 592, 634]),
    ("课时15-2.7.1抛物线方程", [315]),
    ("课时16-2.7.2抛物线性质", [512]),
    ("课时17-2.8①压轴综合一", [321]),
    ("课时18-2.8②压轴综合二", [268, 292]),
    ("课时19-章末总结与复习", [209, 302]),
]

NEXT_HDR = re.compile(r"\\(tjdnr|liB|bindp|jiancestem|xiaojie|ansblock|zhangmo| subgroup)\b")

buf = []
for d, lines in TARGETS:
    p = os.path.join(ROOT, d, "main.tex")
    with io.open(p, "r", encoding="utf-8") as f:
        src = f.readlines()
    for ln in lines:
        i0 = ln - 1
        # 向下取到下一个题头/结构行为止（题面可能折行）
        j = i0
        end = min(len(src), i0 + 40)
        j = i0 + 1
        while j < end:
            if NEXT_HDR.search(src[j]):
                break
            j += 1
        block = "".join(src[i0:j]).rstrip()
        buf.append(f"===== {d}:{ln} =====")
        buf.append(block)
        buf.append("")

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(buf))
print("written", OUT, len("\n".join(buf)), "chars")
