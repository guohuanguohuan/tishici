# -*- coding: utf-8 -*-
"""FX7 edit I1: ①图例行2个run color=000000→auto ②段尾空格1处"""
import os, re
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
DOC = os.path.join(WK, "unpack", "I1", "word", "document.xml")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

tree = etree.parse(DOC)
ps = list(tree.getroot().iter(W + "p"))

def ptext(p):
    return "".join(el.text or "" for el in p.iter() if el.tag in (W + "t", M + "t"))

# ① 图例行 000000 → auto
fixed = []
for i, p in enumerate(ps[:5]):
    t = ptext(p)
    if not (t.startswith("〔基〕") or t.startswith("〔进〕")):
        continue
    for r in p.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            continue
        col = rpr.find(W + "color")
        if col is not None and col.get(W + "val") == "000000":
            col.set(W + "val", "auto")
            fixed.append((i, t[:14]))
print("I1 ① 图例行色→auto:", fixed)
assert len(fixed) == 2

# ② 段尾空格
stripped = []
for i, p in enumerate(ps):
    last = None
    for el in p.iter():
        if el.tag in (W + "t", M + "t"):
            last = el
    if last is not None and last.text and re.search(r"[ \u00A0\u3000]+$", last.text):
        stripped.append((i, repr(last.text[-12:])))
        last.text = re.sub(r"[ \u00A0\u3000]+$", "", last.text)
print("I1 ② 段尾空格:", stripped)
assert len(stripped) == 1

# 复核：全件非auto非FFFFFF色run应仅剩锚白字（FFFFFF）
rem = []
for i, p in enumerate(ps):
    for r in p.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            continue
        col = rpr.find(W + "color")
        if col is not None and col.get(W + "val") not in (None, "auto"):
            rem.append((i, col.get(W + "val")))
print("I1 复核·残留非auto色run:", set(v for _, v in rem), "数=", len(rem))

tree.write(DOC, xml_declaration=True, encoding="UTF-8", standalone=True)
print("I1 document.xml 已写回")
