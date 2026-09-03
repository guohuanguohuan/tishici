# -*- coding: utf-8 -*-
"""FX7 probe2: X2空格段run级细节 + I2全部修复点定位（只读）"""
import os, re
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

def load(tag):
    return etree.parse(os.path.join(WK, "unpack", tag, "word", "document.xml"))

def paras(tree):
    return list(tree.getroot().iter(W + "p"))

def ptext(p):
    out = []
    for el in p.iter():
        if el.tag in (W + "t", M + "t"):
            out.append(el.text or "")
    return "".join(out)

print("=" * 25, "X2 p#12~14 上下文", "=" * 25)
tx2 = load("X2")
ps2 = paras(tx2)
for i in (11, 12, 13, 14):
    print(f"X2 p#{i}: {ptext(ps2[i])[:100]}")
print("--- p#14 run结构（w:t与m:t分记）---")
p = ps2[14]
for j, el in enumerate(p.iter()):
    if el.tag == W + "t":
        print(f"  w:t: {repr(el.text)}")
    elif el.tag == M + "t":
        print(f"  m:t: {repr(el.text)}")
print("--- p#35 nbsp所在元素 ---")
p = ps2[35]
for el in p.iter():
    if el.tag in (W + "t", M + "t") and el.text and ("\xa0" in el.text or "  " in el.text):
        print(f"  {etree.QName(el).localname}: {repr(el.text[:60])}")

print()
print("=" * 25, "X2 p#22/23 段尾元素", "=" * 25)
for i in (22, 23):
    p = ps2[i]
    last = None
    for el in p.iter():
        if el.tag in (W + "t", M + "t"):
            last = el
    print(f"p#{i} last {etree.QName(last).localname}: {repr((last.text or '')[-40:])}")

print()
print("=" * 25, "X1 p#84 pPr tabs 检查", "=" * 25)
tx1 = load("X1")
ps1 = paras(tx1)
p = ps1[84]
ppr = p.find(W + "pPr")
tabs = ppr.find(W + "tabs") if ppr is not None else None
print("pPr tabs def:", etree.tostring(tabs, encoding="unicode") if tabs is not None else None)
# 全X1 run级tab计数
run_tabs = sum(1 for p in ps1 for r in p.iter(W + "r") for _ in r.iter(W + "tab"))
ppr_tabs = sum(1 for p in ps1 for _ in p.iter(W + "pPr") for _ in _.iter(W + "tab"))
print(f"X1 run级tab={run_tabs}, pPr停靠定义tab={ppr_tabs}")

print()
print("=" * 25, "I2 修复点扫描", "=" * 25)
ti2 = load("I2")
ps = paras(ti2)
print("I2 段落总数:", len(ps))

# ① 1F4E79色run
print("\n--- ① 深蓝1F4E79 run ---")
for i, p in enumerate(ps):
    for r in p.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is not None:
            col = rpr.find(W + "color")
            if col is not None and col.get(W + "val") == "1F4E79":
                txt = "".join(x.text or "" for x in r.iter())
                print(f"I2 p#{i} 1F4E79 run text={repr(txt)}")

# 椭圆定义式条目2.5.1-1上下文：找含'|MF'或'2a'的条目段
print("\n--- 条目2.5.1-1 段落族（条目号run起段）---")
for i, p in enumerate(ps):
    t = ptext(p)
    if t.startswith("2.5.1-1．"):
        print(f"I2 p#{i}: {t[:150]}")
        # 打印该段与后续3段的run/m:r结构
        for k in range(i, min(i + 6, len(ps))):
            print(f"  [p#{k}] {ptext(ps[k])[:120]}")
        break

# ② 图例行000000
print("\n--- ② 图例行色 ---")
for i, p in enumerate(ps[:6]):
    t = ptext(p)
    if "〔基〕" in t or "〔进〕" in t:
        print(f"I2 p#{i}: {t[:50]}")
        for r in p.iter(W + "r"):
            rpr = r.find(W + "rPr")
            if rpr is not None:
                col = rpr.find(W + "color")
                if col is not None:
                    print(f"    color={col.get(W+'val')} run=[{''.join(x.text or '' for x in r.iter(W+'t'))[:40]}]")
