# -*- coding: utf-8 -*-
"""S2-A6 执行前 occurrence 重核：ding{51}/ding{55} 剔注释逐行清点＋raw 符号定位。只读。"""
import re, io

def code_part(line):
    """剥未转义 % 之后（含整行注释）。"""
    out = []
    i = 0
    while i < len(line):
        if line[i] == '\\' and i + 1 < len(line):
            out.append(line[i:i+2]); i += 2; continue
        if line[i] == '%':
            break
        out.append(line[i]); i += 1
    return ''.join(out)

BASE = r"C:\提示词\工作区\M3-第2章量产0913\成卷\导学件"
for f in ["课时16-2.7.2抛物线性质/main.tex", "课时17-2.8①压轴综合一/main.tex"]:
    path = BASE + "\\" + f
    lines = io.open(path, encoding="utf-8").read().splitlines()
    n51 = n55 = 0
    hits = []
    for i, l in enumerate(lines, 1):
        c = code_part(l)
        a = len(re.findall(r"ding\{51\}", c)); b = len(re.findall(r"ding\{55\}", c))
        n51 += a; n55 += b
        if a or b:
            hits.append((i, a, b))
    raw = [(i, l.strip()[:60]) for i, l in enumerate(lines, 1)
           if re.search(r"✓|✗|⇒|∎", code_part(l))]
    print(f, "| ding51 剔注释 =", n51, "| ding55 剔注释 =", n55, "| 命中行数 =", len(hits))
    print("  行分布:", hits)
    print("  印面 raw 符号行:", raw if raw else "0")
