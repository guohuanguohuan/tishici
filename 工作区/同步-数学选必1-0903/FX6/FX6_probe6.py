# -*- coding: utf-8 -*-
"""FX6 probe6: ④疑点段OMML结构判定 + p#617灰底 + p#314/p#973答案语境"""
import re, io
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
DOC = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H\word\document.xml"
OUT = r"C:\提示词\工作区\同步-数学选必1-0903\FX6\扫描-probe6.txt"
tree = etree.parse(DOC)
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
buf = io.StringIO()
def P(*a): print(*a, file=buf)

# 找含目标线性串的oMath，打印其结构摘要（元素tag序列）
TARGETS = {
    62: "Δ=16−4k", 301: "Δ=-2k2+8m", 469: "64c29−6c2", 940: "2b=2e=ca=32",
    1169: "ca=2232a=6", 1173: "x=3y=−3", 1252: "y=kx−1+1y=22x",
    59: "x=1y=2", 315: "x=-1y=14", 387: "y=tx+12y=x22",
}
def omml_struct(om):
    tags = []
    def walk(el, d=0):
        for ch in el:
            ln = etree.QName(ch).localname
            tags.append(ln)
            if ln in ("f", "d", "sSup", "sSub", "eqArr", "rad", "nary", "bar", "func"):
                walk(ch, d + 1)
    walk(om)
    return tags

for k, p in enumerate(paras):
    if k not in TARGETS:
        continue
    key = TARGETS[k]
    for om in p.iter(f"{{{M}}}oMath"):
        lin = "".join(om.itertext())
        if key in lin:
            P(f"\n=== p#{k} 命中 {key!r} 全式={lin[:100]!r}")
            P("  结构:", omml_struct(om))

# p#617 灰底run（剥ns重打印）
P("\n=== p#617 灰底值run（局部，无ns噪声） ===")
for r in paras[617].iter(f"{{{W}}}r"):
    rPr = r.find(f"{{{W}}}rPr")
    if rPr is not None and rPr.find(f"{{{W}}}shd") is not None:
        txt = "".join(t.text or "" for t in r.findall(f"{{{W}}}t"))
        children = [etree.QName(c).localname for c in r]
        rpr_ch = [etree.QName(c).localname + (f"={c.get(f'{{{W}}}val')}" if etree.QName(c).localname in ("sz","szCs","b") else "") for c in rPr]
        P(f"  run子={children} rPr={rpr_ch} 文本={txt!r}")

# p#314题干（验证 /3 错位修复的答案值）与 p#973
P("\n=== p#314 题干（题2.8.14-21） ===")
P(" ", "".join(paras[314].itertext())[:150])
for q in range(315, 320):
    P(f"  p#{q}:", "".join(paras[q].itertext())[:120])
P("\n=== p#973 题干（题2.8.39-71） ===")
P(" ", "".join(paras[973].itertext())[:150])
for q in range(974, 979):
    P(f"  p#{q}:", "".join(paras[q].itertext())[:120])

# 详解里查找 p#314题的最终答案式（含 /3 或 4x²）
P("\n=== p#320-345 中含 '3' 分数线结构的详解段（题2.8.14-21详解） ===")
for q in range(320, 346):
    t = "".join(paras[q].itertext())
    if "4x" in t or "y=(4" in t or "(4x" in t:
        P(f"  p#{q}: {t[:160]!r}")

open(OUT, "w", encoding="utf-8").write(buf.getvalue())
print("written", OUT)
