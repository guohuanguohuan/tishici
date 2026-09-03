# -*- coding: utf-8 -*-
"""FX7 probe4: I2——空格命中段的表格归属 + 灰底越界扫描 + 21个编注段run级结构"""
import os, re
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

tree = etree.parse(os.path.join(WK, "unpack", "I2", "word", "document.xml"))
root = tree.getroot()
body = root.find(W + "body")
# 段落全局序（与probe一致：iter顺序）
ps = list(root.iter(W + "p"))
pidx = {id(p): i for i, p in enumerate(ps)}

def in_table(p):
    a = p.getparent()
    while a is not None:
        if a.tag == W + "tbl":
            return True
        a = a.getparent()
    return False

def ptext(p):
    return "".join(el.text or "" for el in p.iter() if el.tag in (W + "t", M + "t"))

print("=" * 25, "空格命中段表格归属", "=" * 25)
hits = [30, 95, 96, 97, 99, 100, 101, 111, 112, 119, 120, 169, 177, 182, 189, 205, 239, 254, 258,
        326, 327, 374, 376, 382, 384, 385, 387, 428, 429, 500, 502, 503, 505, 512, 520, 521, 523, 524,
        734, 802, 803, 804, 807, 809, 810, 811, 817, 818, 819, 822, 823, 824, 825, 827, 844, 845]
for i in hits:
    p = ps[i]
    print(f"p#{i}: in_tbl={in_table(p)} | {ptext(p)[:60]}")

print()
print("=" * 25, "灰底越界扫描（w:r挂C9C9C9，文本含标点/空格越界）", "=" * 25)
n_grey_runs = 0
n_over = 0
for i, p in enumerate(ps):
    for r in p.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            continue
        s = rpr.find(W + "shd")
        if s is None or s.get(W + "fill") != "C9C9C9":
            continue
        n_grey_runs += 1
        txt = "".join(t.text or "" for t in r.iter(W + "t"))
        # 越界判据：灰底文本首尾为标点/空格，或中间含句读级标点（，。；）
        if txt and (re.search(r"^[，。；、（）\[\]\s]+", txt) or re.search(r"[，。；、\s]+$", txt) or re.search(r"[，。；]", txt[1:-1]) if len(txt) > 1 else False):
            print(f"  I2 p#{i} 灰底run越界?: [{txt[:50]}] in_tbl={in_table(p)}")
            n_over += 1
print(f"C9C9C9 run总数={n_grey_runs}, 越界候选={n_over}")

# m:t 内挂灰且纯标点
n_mt_grey = 0
for i, p in enumerate(ps):
    for mr in p.iter(M + "r"):
        rpr = mr.find(W + "rPr")
        if rpr is None:
            continue
        s = rpr.find(W + "shd")
        if s is None or s.get(W + "fill") != "C9C9C9":
            continue
        n_mt_grey += 1
        txt = "".join(t.text or "" for t in mr.iter(M + "t"))
        if txt and re.fullmatch(r"[，。；、（）()\[\]|｜\s]+", txt):
            print(f"  I2 p#{i} m:r纯标点挂灰: [{txt}]")
print(f"m:r挂灰总数={n_mt_grey}")

print()
print("=" * 25, "21个编注段run级结构", "=" * 25)
targets = [12, 22, 28, 210, 230, 316, 336, 364, 394, 416, 487, 492, 569, 665, 673, 682, 730, 776, 799, 852, 867]
for i in targets:
    p = ps[i]
    print(f"--- p#{i} (in_tbl={in_table(p)})")
    seq = []
    for el in p:
        if el.tag == W + "r":
            t = "".join(x.text or "" for x in el.iter(W + "t"))
            rpr = el.find(W + "rPr")
            shd = None
            if rpr is not None:
                s = rpr.find(W + "shd")
                shd = s.get(W + "fill") if s is not None else None
            seq.append(("R", t, shd))
        elif el.tag == M + "oMath":
            t = "".join(x.text or "" for x in el.iter(M + "t"))
            seq.append(("M", t, None))
    for kind, t, shd in seq:
        print(f"    {kind}{'[' + shd + ']' if shd else ''} {repr(t)}")
