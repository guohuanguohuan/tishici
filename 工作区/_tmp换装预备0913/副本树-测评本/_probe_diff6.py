# -*- coding: utf-8 -*-
"""只读探查：测评卷六宏 vs 导学件课时01 六宏（qp-m3 回源基准）逐文件差异行数。"""
import io, os, difflib

ROOT = r"C:/提示词/工作区/M2-第1章量产0911/成卷"
A = os.path.join(ROOT, "测评卷")
B = os.path.join(ROOT, "导学件/课时01")
C = os.path.join(ROOT, "滚动卷/滚A")
D = os.path.join(ROOT, "滚动卷/滚B")
files = ["qp-fonts.tex", "qp-layout.tex", "qp-parts.tex", "qp-headfoot.tex", "qp-titles.tex", "qp-blocks.tex"]

def lines(p):
    return io.open(p, encoding="utf-8").read().split("\n")

for f in files:
    a = lines(os.path.join(A, f))
    b = lines(os.path.join(B, f))
    diff = list(difflib.unified_diff(b, a, lineterm=""))
    changed = [x for x in diff if x.startswith(("+", "-")) and not x.startswith(("+++", "---"))]
    same_c = sum(1 for x in C if False)
    cd = len([x for x in difflib.unified_diff(lines(os.path.join(C, f)), a, lineterm="")
              if x.startswith(("+", "-")) and not x.startswith(("+++", "---"))])
    dd = len([x for x in difflib.unified_diff(lines(os.path.join(D, f)), a, lineterm="")
              if x.startswith(("+", "-")) and not x.startswith(("+++", "---"))])
    print("%-16s 导学基准→测评卷 diff行 %4d | 滚A→测评卷 diff行 %4d | 滚B→测评卷 diff行 %4d" % (f, len(changed), cd, dd))
