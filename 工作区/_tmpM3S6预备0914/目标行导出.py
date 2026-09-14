# -*- coding: utf-8 -*-
"""导出 16/17 全部文读化目标行（ding/Rightarrow/iff）全文。只读。"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
for f in ["课时16-2.7.2抛物线性质/main.tex", "课时17-2.8①压轴综合一/main.tex"]:
    lines = io.open(f, encoding="utf-8").read().splitlines()
    out = io.open(os.path.join(HERE, "文读化目标_" + f[:3] + f.split("-")[1][:1] + ".txt"), "w", encoding="utf-8")
    for i, l in enumerate(lines, 1):
        if re.search(r"ding\{|Rightarrow|iff", l):
            out.write("L%d<<%s>>\n\n" % (i, l))
    out.close()
    print("ok", f)
