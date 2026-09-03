# -*- coding: utf-8 -*-
# FX2b probe_om：定位指定段内oMath的父节点与前置/后置内容
import re
from lxml import etree

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

doc = etree.parse(BASE + r"\unpacked\word\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

def om_lin(node):
    if node.tag == f"{{{M}}}t":
        return node.text or ""
    q = etree.QName(node).localname
    if q == "rad":
        return "√(" + "".join(om_lin(c) for c in node.find(f"{{{M}}}e")) + ")"
    if q == "f":
        return ("«" + "".join(om_lin(c) for c in node.find(f"{{{M}}}num")) + "»/«" +
                "".join(om_lin(c) for c in node.find(f"{{{M}}}den")) + "»")
    if q == "d":
        return "(" + "".join(om_lin(c) for c in node.findall(f"{{{M}}}e")) + ")"
    return "".join(om_lin(c) for c in node)

for i in [3, 259, 299]:
    p = paras[i]
    print(f"===== p#{i} 直接子级标签序列 =====")
    for j, child in enumerate(p):
        print(f"  [{j}] {etree.QName(child).localname}")
    print(f"  oMath总数: {len(list(p.iter(f'{{{M}}}oMath')))}")
    # oMath前置文本
    print("  --- 按标签顺序（含oMath）---")
    for j, child in enumerate(p):
        tag = etree.QName(child).localname
        if tag == "r":
            print(f"  [{j}] r «{''.join(t.text or '' for t in child.findall(f'{{{W}}}t'))}»")
        elif tag == "oMath":
            print(f"  [{j}] oMath ⟨{om_lin(child)}⟩")
        elif tag == "pPr":
            print(f"  [{j}] pPr")
    print()
