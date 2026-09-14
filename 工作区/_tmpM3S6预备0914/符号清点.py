# -*- coding: utf-8 -*-
"""16/17 印面 ⇒/⟺/∎ 清点＋头注全文导出。只读。"""
import io, re

for f in ["课时16-2.7.2抛物线性质/main.tex", "课时17-2.8①压轴综合一/main.tex"]:
    L = io.open(f, encoding="utf-8").read().splitlines()
    code = [l.split("%")[0] for l in L]
    arr = sum(len(re.findall(r"Rightarrow", l)) for l in code)
    iff = sum(len(re.findall(r"iff", l)) for l in code)
    blk = sum(len(re.findall(r"∎", l)) for l in code)
    print(f[:9], "| Rightarrow:", arr, "| iff:", iff, "| ∎:", blk)

print()
for f in ["课时16-2.7.2抛物线性质/main.tex", "课时17-2.8①压轴综合一/main.tex"]:
    L = io.open(f, encoding="utf-8").read().splitlines()
    for i in range(10, 30):
        if i <= len(L) and L[i-1].lstrip().startswith("%"):
            print(f[:3], i, ":", L[i-1].rstrip()[:170])
    for i in range(74, 82):
        if i <= len(L) and L[i-1].lstrip().startswith("%"):
            print(f[:3], i, ":", L[i-1].rstrip()[:170])
    print()
