# -*- coding: utf-8 -*-
"""FX7 probe: 逐项定位修复点（只读分析，不改文件）"""
import os, re, sys
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

def load(tag):
    p = os.path.join(WK, "unpack", tag, "word", "document.xml")
    return etree.parse(p)

def paras(tree):
    return tree.getroot().iter(W + "p")

def ptext(p):
    """段落全文本（w:t + m:t，按文档序）"""
    out = []
    for el in p.iter():
        if el.tag == W + "t" or el.tag == M + "t":
            out.append(el.text or "")
    return "".join(out)

def ptext_wt(p):
    out = []
    for el in p.iter(W + "t"):
        out.append(el.text or "")
    return "".join(out)

print("=" * 30, "B: 节标题行统计段形态参照", "=" * 30)
tb = load("B")
for i, p in enumerate(paras(tb)):
    t = ptext(p)
    if re.search(r"本节\d+题", t):
        # 打印该段的run结构
        print(f"--- B p#{i}: {t[:80]}")
        for r in p.iter(W + "r"):
            txt = "".join(x.text or "" for x in r.iter(W + "t"))
            rpr = r.find(W + "rPr")
            props = []
            if rpr is not None:
                for c in rpr:
                    tag = etree.QName(c).localname
                    if tag == "rFonts":
                        props.append("rFonts")
                    elif tag == "sz":
                        props.append(f"sz={c.get(W+'val')}")
                    elif tag == "szCs":
                        props.append(f"szCs={c.get(W+'val')}")
                    elif tag == "b":
                        props.append(f"b={c.get(W+'val','on')}")
                    elif tag == "color":
                        props.append(f"color={c.get(W+'val')}")
                    else:
                        props.append(tag)
            if txt or props:
                print(f"    run [{txt[:50]}] {props}")
        break  # 只看第一处样例

print()
print("=" * 30, "X1: 节标题段结构", "=" * 30)
tx1 = load("X1")
for i, p in enumerate(paras(tx1)):
    t = ptext(p)
    if t.startswith("1.2.1 ") or t.startswith("1.2.5 "):
        print(f"--- X1 p#{i}: [{t}]")
        ppr = p.find(W + "pPr")
        if ppr is not None:
            print("    pPr:", etree.tostring(ppr, encoding="unicode")[:300])
        for r in p.iter(W + "r"):
            txt = "".join(x.text or "" for x in r.iter(W + "t"))
            rpr = r.find(W + "rPr")
            props = []
            if rpr is not None:
                for c in rpr:
                    tag = etree.QName(c).localname
                    if tag in ("sz", "szCs"):
                        props.append(f"{tag}={c.get(W+'val')}")
                    elif tag == "b":
                        props.append(f"b={c.get(W+'val','on')}")
                    elif tag == "rFonts":
                        props.append("rFonts")
            print(f"    run [{txt[:60]}] {props}")

print()
print("=" * 30, "X1: 题量复算（题号块）", "=" * 30)
cnt = {}
for p in paras(tx1):
    t = ptext(p)
    m = re.match(r"^(1\.2\.\d\.\d+-\d+．)", t)
    if m:
        sec = m.group(1).rsplit("-", 1)[0]
        cnt[sec] = cnt.get(sec, 0) + 1
print("X1 题号块按节:", cnt, "Σ=", sum(cnt.values()))

print()
print("=" * 30, "X1: p#84 选项段（w:tab所在段）", "=" * 30)
for i, p in enumerate(paras(tx1)):
    tabs = list(p.iter(W + "tab"))
    if tabs:
        print(f"--- X1 p#{i} tabs={len(tabs)}")
        print("    full text:", repr(ptext(p))[:400])
        # run级结构
        for j, r in enumerate(p.iter(W + "r")):
            parts = []
            for c in r:
                tag = etree.QName(c).localname
                if tag == "t":
                    parts.append(("t", c.text or ""))
                elif tag == "tab":
                    parts.append(("TAB", ""))
                elif tag == "drawing":
                    parts.append(("IMG", ""))
                elif tag == "oMath" or tag.endswith("}oMath"):
                    parts.append(("MATH", ""))
            print(f"    run{j}: {parts}")

print()
print("=" * 30, "X1: 段尾空格扫描", "=" * 30)
def trailing_scan(tree, tag):
    res = []
    for i, p in enumerate(paras(tree)):
        # 文档序最后一个 w:t 或 m:t
        last = None
        for el in p.iter():
            if el.tag in (W + "t", M + "t"):
                last = el
        if last is not None and last.text and re.search(r"[ \u00A0\u3000]+$", last.text):
            res.append((i, last.text[-25:], etree.QName(last).localname))
    return res
for r in trailing_scan(tx1, "X1"):
    print("X1 trailing:", r)

print()
print("=" * 30, "I1: 图例行000000 run + 段尾空格", "=" * 30)
ti1 = load("I1")
for i, p in enumerate(paras(ti1)):
    for r in p.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is not None:
            col = rpr.find(W + "color")
            if col is not None and col.get(W + "val") not in (None, "auto"):
                txt = "".join(x.text or "" for x in r.iter(W + "t"))
                print(f"I1 p#{i} color={col.get(W+'val')} run=[{txt[:60]}]")
for r in trailing_scan(ti1, "I1"):
    print("I1 trailing:", r)

print()
print("=" * 30, "X2: 节标题行统计段检查 + 题量复算", "=" * 30)
tx2 = load("X2")
for i, p in enumerate(paras(tx2)):
    t = ptext(p)
    if re.match(r"^2\.\d", t) and ("直线" in t or "圆锥" in t):
        print(f"X2 p#{i}: [{t}]  含统计段: {bool(re.search(r'本节\d+题', t))}")
cnt2 = 0
for p in paras(tx2):
    t = ptext(p)
    if re.match(r"^2\.8\.\d+-\d+．", t):
        cnt2 += 1
print("X2 题号块数:", cnt2)
# 顺便列出X2全部节标题样式段
print()
print("=" * 30, "X2: 空格卫生定位", "=" * 30)
for i, p in enumerate(paras(tx2)):
    t_w = ptext_wt(p)
    t_all = ptext(p)
    issues = []
    if re.search(r"  +", t_all):
        issues.append("双半空格")
    if re.search(r"[ ]+[，。；：、？！]", t_all):
        issues.append("全角标点前空格")
    if "\u00A0" in t_all:
        issues.append(f"nbsp×{t_all.count(chr(160))}")
    # 段尾
    last = None
    for el in p.iter():
        if el.tag in (W + "t", M + "t"):
            last = el
    if last is not None and last.text and re.search(r"[ \u00A0]+$", last.text):
        issues.append("段尾空格")
    if issues:
        print(f"X2 p#{i} {issues}: {repr(t_all[:90])}")
