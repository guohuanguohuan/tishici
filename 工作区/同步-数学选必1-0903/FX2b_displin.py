# -*- coding: utf-8 -*-
# FX2b_displin：28段完整显示线性化（w:t + oMath序列）+ w:t纯文本层 逐段对照
# 用于精确判定：线性数学是不是真在w:t层（需转）还是已在oMath（无需转）
import re
from lxml import etree

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

doc = etree.parse(BASE + r"\unpacked\word\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

ORIG = [4,175,224,260,273,300,324,331,353,355,364,379,398,429,437,452,460,468,478,480,487,493,539,556,804,897,900,971]

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

def find_oms(p):
    """按文档序返回 (start_display_offset, oMath节点) — 需要w:t长度累计"""
    # 先收集w:t及其文本（含嵌套），与oMath按树序
    items = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            items.append(("t", node.text or ""))
        elif node.tag == f"{{{M}}}oMath":
            items.append(("m", om_lin(node)))
    # 但iter顺序是深度优先，oMath内无w:t，安全
    return items

for oi in ORIG:
    ci = oi - 1
    p = paras[ci]
    items = find_oms(p)
    full = "".join(t for k, t in items if k == "t")  # w:t层纯文本
    full_all = "".join(("«" + t + "»" if k == "m" else t) for k, t in items)  # oMath括起
    wt_math_hits = []
    for k, t in items:
        if k == "t":
            for m in re.finditer(r"√|\u00b2|\u00b3|\u00b9|[\u2070-\u209f]|[\u2080-\u209c]", t):
                wt_math_hits.append((m.group(), t[max(0,m.start()-12):m.end()+12]))
    print("=" * 100)
    print(f"原p#{oi} 现p#{ci}")
    print(f"  [w:t纯文本] {full!r}")
    print(f"  [显示(«»=om)] {full_all!r}")
    if wt_math_hits:
        print(f"  !! w:t层含√/²/³/上下标: {wt_math_hits}")
