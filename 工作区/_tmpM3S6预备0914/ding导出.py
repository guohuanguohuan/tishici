# -*- coding: utf-8 -*-
"""导出 16/17 片 ding 命中行原文（注释行标 @），供逐处文读化。只读。"""
import io, os

BASE = r"C:\提示词\工作区\M3-第2章量产0913\成卷\导学件"
FILES = ["课时16-2.7.2抛物线性质/main.tex", "课时17-2.8①压轴综合一/main.tex"]
out = io.open(os.path.dirname(os.path.abspath(__file__)) + r"\ding命中行.txt", "w", encoding="utf-8")
for f in FILES:
    tag = f.split("-")[0] + f.split("-")[1][:2]
    for i, l in enumerate(io.open(os.path.join(BASE, f), encoding="utf-8"), 1):
        if "ding{" in l:
            mark = "@" if l.lstrip().startswith("%") else " "
            out.write("%s:%d:%s %s" % (f[:3] + f.split("-")[1][:1], i, mark, l.rstrip()[:280]) + "\n")
out.close()
print("ok")
