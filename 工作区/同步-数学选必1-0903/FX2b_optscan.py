# -*- coding: utf-8 -*-
# FX2b_opt：Task2 相关选项段结构（嵌套oMath+文本+tab+分号）；Task3 LEADtab确认
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

def token_seq(p):
    """按文档顺序产出 token：(kind, payload, node)。oMath用om_lin"""
    seq = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            # 只在非oMath内的w:t出现？ iter会进入oMath内部吗？ oMath内用m:t，无w:t。安全
            seq.append(("t", node.text or "", node))
        elif node.tag == f"{{{W}}}tab":
            seq.append(("tab", "\t", node))
        elif node.tag == f"{{{M}}}oMath":
            seq.append(("m", om_lin(node), node))
    return seq

def show(i):
    p = paras[i]
    wt = "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))
    print("=" * 108)
    print(f"### 现p#{i}")
    print(f"   [w:t层] {wt!r}")
    seq = token_seq(p)
    print("   [token序]")
    for k, (kind, txt, node) in enumerate(seq):
        print(f"      [{k}] ({kind}) «{txt}»")

# Task2 候选段（探针找到A．；的6段 + 题号段带选项）
for i in [266, 273, 281, 297, 804, 1037]:
    show(i)
