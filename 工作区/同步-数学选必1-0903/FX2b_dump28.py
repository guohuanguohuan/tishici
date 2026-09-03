# -*- coding: utf-8 -*-
# FX2b dump28：28段全部run级+oMath结构+线性数学签名char区间（供逐段判定）
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

SIG = re.compile(r"√|[\u00b2\u00b3\u2070-\u209f]")

print(f"总段数: {len(paras)}")
for oi in ORIG:
    ci = oi - 1
    p = paras[ci]
    print("=" * 110)
    print(f"### 原p#{oi} 现p#{ci}")
    # run级
    for j, child in enumerate(p):
        tag = etree.QName(child).localname
        if tag == "r":
            ts = child.findall(f"{{{W}}}t")
            tabs = child.findall(f"{{{W}}}tab")
            dr = child.findall(f"{{{W}}}drawing")
            txt = "".join(t.text or "" for t in ts)
            extra = f" +tab×{len(tabs)}" if tabs else ""
            extra += f" +drawing×{len(dr)}" if dr else ""
            if txt or extra:
                print(f"   [{j}] w:r «{txt}»{extra}")
        elif tag == "oMath":
            mt = "".join(t.text or "" for t in child.iter(f"{{{M}}}t"))
            print(f"   [{j}] oMath ⟨{om_lin(child)}⟩ (m:t={mt!r})")
        elif tag == "pPr":
            ind = child.find(f"{{{W}}}ind")
            if ind is not None:
                print(f"   [{j}] pPr w:ind={etree.tostring(ind).decode()[:120]}")
    # 线性数学签名 char区间（w:t层，含m:t既有如何与正文交错）
    seq = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            seq.append(("t", node.text or ""))
        elif node.tag == f"{{{M}}}oMath":
            seq.append(("m", om_lin(node)))
    full = ""
    spans = []
    for kind, txt in seq:
        a = len(full)
        full += txt
        if kind == "t":
            b = len(full)
            for m in SIG.finditer(txt):
                # 映射到full绝对offset
                aa = a + m.start(); bb = a + m.end()
                lo = max(0, aa - 18); hi = min(len(full), bb + 18)
                spans.append((aa, bb, full[aa:bb], full[lo:hi]))
    print(f"   [FULL] {full}")
    if spans:
        for aa, bb, hit, ctx in spans:
            print(f"      SIG @{aa}-{bb} «{hit}»  ctx=…{ctx}…")
    else:
        print("      (w:t无√/²/上标签名)")
