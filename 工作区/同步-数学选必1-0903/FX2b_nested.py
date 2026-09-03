# -*- coding: utf-8 -*-
# FX2b_nested：真阳性段完整嵌套结构（run内嵌oMath）逐节点
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
    if q == "sSup":
        e = node.find(f"{{{M}}}e"); sup = node.find(f"{{{M}}}sup")
        return "".join(om_lin(c) for c in e) + "^{" + "".join(om_lin(c) for c in sup) + "}"
    if q == "sSub":
        e = node.find(f"{{{M}}}e"); sub = node.find(f"{{{M}}}sub")
        return "".join(om_lin(c) for c in e) + "_{" + "".join(om_lin(c) for c in sub) + "}"
    if q == "d":
        return "(" + "".join(om_lin(c) for c in node.findall(f"{{{M}}}e")) + ")"
    return "".join(om_lin(c) for c in node)

def dump(p, depth=0):
    for node in p:
        tag = etree.QName(node).localname
        if tag == "t":
            print("  " * depth + f"t «{node.text or ''}»")
        elif tag == "oMath":
            print("  " * depth + f"oMath ⟨{om_lin(node)}⟩")
        elif tag == "r":
            print("  " * depth + f"<r>")
            dump(node, depth + 1)
        elif tag == "pPr":
            ind = node.find(f"{{{W}}}ind")
            print("  " * depth + f"<pPr>" + (f" ind={etree.tostring(ind).decode()[:80]}" if ind is not None else ""))
        elif tag in ("rPr", "pPr"):
            print("  " * depth + f"<{tag}>")
        elif tag == "tab":
            print("  " * depth + "⇥tab")
        elif tag == "br":
            print("  " * depth + "<w:br>")
        else:
            # 其他（rPr的子元素、m的子元素等）不深打，仅名
            if tag in ("rFonts","sz","szCs","shd","spacing","jc","ctrlPr"):
                print("  " * depth + f"<{tag}>")
            # else skip

# 真阳性段 + 内容瑕疵段
for i in [3, 259, 272, 363, 479, 492, 555, 803]:
    print("=" * 110)
    print(f"### 现p#{i} (原p#{i+1})")
    dump(paras[i])
