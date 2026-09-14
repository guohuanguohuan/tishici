# -*- coding: utf-8 -*-
"""组头一致性审计复扫（导学件全 21 片）：衔接节唯一 \\xjkeshi，常规课时全 \\jietitle。只读。"""
import io, os

BASE = r"C:\提示词\工作区\M3-第2章量产0913\成卷\导学件"
n = ok = 0
for d in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, d, "main.tex")
    if not os.path.isfile(p):
        continue
    s = io.open(p, encoding="utf-8").read()
    n += 1
    if d == "衔接节":
        good = ("\\xjkeshi{" in s) and ("\\jietitle{" not in s)
    else:
        good = ("\\xjkeshi{" not in s) and ("\\jietitle{" in s)
    ok += good
    if not good:
        print("异常:", d)
print("组头一致性审计：%d/%d（衔接节唯一 xjkeshi、常规课时全 jietitle）" % (ok, n))
