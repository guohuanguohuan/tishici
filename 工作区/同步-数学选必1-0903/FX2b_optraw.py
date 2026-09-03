# -*- coding: utf-8 -*-
# FX2b_optraw：6个异常选项段 顶层含"．；"/空格 的 w:r 精确结构
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

for i in [281, 804, 266]:
    p = paras[i]
    print("=" * 110)
    print(f"#### 现p#{i} 顶层run序列 ####")
    for j, child in enumerate(p):
        tag = etree.QName(child).localname
        if tag == "r":
            sub = []
            for c in child:
                ct = etree.QName(c).localname
                if ct == "t":
                    sub.append(f"t«{c.text or ''}»")
                elif ct == "tab":
                    sub.append("TAB")
                elif ct == "rPr":
                    continue
                else:
                    sub.append(f"<{ct}>")
            print(f"  [{j}] r: {' | '.join(sub)}")
        elif tag == "oMath":
            print(f"  [{j}] oMath ⟨{om_lin(child)}⟩")
        elif tag == "pPr":
            print(f"  [{j}] pPr")
        else:
            print(f"  [{j}] <{tag}>")
    print()
