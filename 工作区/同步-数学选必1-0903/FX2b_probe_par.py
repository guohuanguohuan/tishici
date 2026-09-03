# -*- coding: utf-8 -*-
# FX2b probe_par：确认oMath的父节点+完整w:t/w:tab/oMath交错（含嵌套层级）
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

for i in [3]:
    p = paras[i]
    print(f"===== p#{i} =====")
    # 查找所有oMath节点，打印其父链
    for om in p.iter(f"{{{M}}}oMath"):
        pc = om.getparent()
        print(f"oMath parent tag = {etree.QName(pc).localname}, parent is w:r? {pc.tag == f'{{{W}}}r'}")
        anc = om
        chain = []
        while anc is not None and anc is not p:
            anc = anc.getparent()
            if anc is not None and anc is not p:
                chain.append(etree.QName(anc).localname)
        print(f"  ancestor chain (excluding p): {chain}")
        print(f"  om_lin = {om_lin(om)}")
    # 打印p的完整嵌套结构：w:r的子元素
    print("--- p 的结构树 ---")
    def dump(node, depth=0):
        tag = etree.QName(node).localname
        if tag == "t":
            print("  " * depth + f"t «{node.text or ''}»")
        elif tag == "oMath":
            print("  " * depth + f"oMath ⟨{om_lin(node)}⟩")
        elif tag in ("r", "pPr", "rPr", "p", "oMath", "rPr"):
            extra = ""
            if tag == "r":
                extra = f" (has {'/'.join(etree.QName(c).localname for c in node)} )"
            print("  " * depth + f"<{tag}>{extra}")
        else:
            print("  " * depth + f"<{tag}>")
        for c in node:
            dump(c, depth + 1)
    dump(p)
    print()
