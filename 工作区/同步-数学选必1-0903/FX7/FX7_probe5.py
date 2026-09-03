# -*- coding: utf-8 -*-
"""FX7 probe5: B参照run XML + I2 p#601/347/357上下文 + 度符号约定"""
import os, re
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

def load(tag):
    return etree.parse(os.path.join(WK, "unpack", tag, "word", "document.xml"))

tb = load("B")
for p in tb.getroot().iter(W + "p"):
    t = "".join(el.text or "" for el in p.iter() if el.tag in (W + "t", M + "t"))
    if re.search(r"本节10题", t):
        runs = [r for r in p if r.tag == W + "r"]
        # 找分隔run与统计run
        for r in runs:
            txt = "".join(x.text or "" for x in r.iter(W + "t"))
            if txt == "　" or txt.startswith("本节"):
                print("B run XML:")
                print(etree.tostring(r, encoding="unicode", pretty_print=True)[:800])
        break

ti2 = load("I2")
ps = list(ti2.getroot().iter(W + "p"))

def ptext(p):
    return "".join(el.text or "" for el in p.iter() if el.tag in (W + "t", M + "t"))

print("=" * 20, "I2 p#601 上下文（前2段起）", "=" * 20)
for i in range(598, 604):
    print(f"p#{i}: {ptext(ps[i])[:130]}")
print("--- p#601 run结构 ---")
for r in ps[601].iter(W + "r"):
    txt = "".join(x.text or "" for x in r.iter(W + "t"))
    rpr = r.find(W + "rPr")
    shd = None
    if rpr is not None:
        s = rpr.find(W + "shd")
        shd = s.get(W + "fill") if s is not None else None
    if txt.strip() or shd:
        print(f"  R{('[' + shd + ']') if shd else ''} {repr(txt[:60])}")

print()
print("=" * 20, "I2 p#347/357 所在表格上下文", "=" * 20)
for i in (345, 346, 347, 355, 356, 357):
    print(f"p#{i}: {ptext(ps[i])[:100]}")

print()
print("=" * 20, "I2 度符号°在m:t中的既有形态（样本）", "=" * 20)
n = 0
for i, p in enumerate(ps):
    for t in p.iter(M + "t"):
        if t.text and "°" in t.text and n < 5:
            print(f"p#{i} m:t: {repr(t.text[:40])}")
            n += 1
    if n >= 5:
        break
print("(m:t含°样本数≥", n, ")")

# X1/X2 节标题段的直接子run是否含嵌套（检查X2 p#2结构）
tx2 = load("X2")
ps2 = list(tx2.getroot().iter(W + "p"))
print()
print("=" * 20, "X2 p#0/1/2 结构", "=" * 20)
for i in (0, 1, 2):
    p = ps2[i]
    print(f"p#{i}: {ptext(p)[:60]}")
    for child in p:
        if child.tag == W + "r":
            txt = "".join(x.text or "" for x in child.iter(W + "t"))
            zs = [z.get(W + "val") for z in child.iter(W + "sz")]
            print(f"    R sz={zs} [{txt[:40]}]")
