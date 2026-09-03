# -*- coding: utf-8 -*-
# FX2b探查2：(A)28段完整交错序列（oMath结构化线性化）；(B)选项段全量扫描找粘连/空格/杂散分号；(C)行首tab段w:ind二分
import re
from lxml import etree

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

doc = etree.parse(BASE + r"\unpacked\word\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

def lin_node(node):
    """结构化线性化：oMath→⟨m:原文⟩，rad→√(e)，f→num/den，其他递归"""
    if node.tag == f"{{{M}}}t":
        return node.text or ""
    q = etree.QName(node).localname
    if q == "rad":
        return "√(" + "".join(lin_node(c) for c in node.find(f"{{{M}}}e")) + ")"
    if q == "f":
        return ("«" + "".join(lin_node(c) for c in node.find(f"{{{M}}}num")) + "»/«" +
                "".join(lin_node(c) for c in node.find(f"{{{M}}}den")) + "»")
    if q == "sSup":
        e = node.find(f"{{{M}}}e"); sup = node.find(f"{{{M}}}sup")
        return "".join(lin_node(c) for c in e) + "^{" + "".join(lin_node(c) for c in sup) + "}"
    if q == "sSub":
        e = node.find(f"{{{M}}}e"); sub = node.find(f"{{{M}}}sub")
        return "".join(lin_node(c) for c in e) + "_{" + "".join(lin_node(c) for c in sub) + "}"
    if q == "d":  # 括号对
        return "(" + "".join(lin_node(c) for c in node.findall(f"{{{M}}}e")) + ")"
    return "".join(lin_node(c) for c in node)

def flat_node(node):
    """扁平线性化（round-trip用）：rad→√+e，f→num/den，其余原样拼接（与FX2口径一致+扩展）"""
    if node.tag == f"{{{M}}}t":
        return node.text or ""
    q = etree.QName(node).localname
    if q == "rad":
        return "√" + "".join(flat_node(c) for c in node.find(f"{{{M}}}e"))
    if q == "f":
        return ("".join(flat_node(c) for c in node.find(f"{{{M}}}num")) + "/" +
                "".join(flat_node(c) for c in node.find(f"{{{M}}}den")))
    return "".join(flat_node(c) for c in node)

def om_raw(om):
    """oMath原始m:t拼接（不含结构）"""
    return "".join(t.text or "" for t in om.iter(f"{{{M}}}t"))

def inline_dump(p):
    seq = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            seq.append(node.text or "")
        elif node.tag == f"{{{W}}}tab":
            seq.append("⇥")
        elif node.tag == f"{{{M}}}oMath":
            seq.append("⟨" + lin_node(node) + "⟩")
    return "".join(seq)

ORIG = [4,175,224,260,273,300,324,331,353,355,364,379,398,429,437,452,460,468,478,480,487,493,539,556,804,897,900,971]
print("###### A. 28段完整交错序列（⟨⟩=oMath结构化；«»/…=f分子分母） ######")
for oi in ORIG:
    ci = oi - 1
    p = paras[ci]
    print(f"--- 原p#{oi} 现p#{ci}: {inline_dump(p)}")

print()
print("###### B. 选项段全量扫描 ######")
# 选项段：w:t含≥2个「X．」标记（A-D）
opt_re = re.compile(r"[ABCD]．")
for i, p in enumerate(paras):
    wt = "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))
    letters = opt_re.findall(wt)
    if len(letters) >= 2:
        print(f"p#{i}: {inline_dump(p)}")

print()
print("###### C. 行首tab段二分（w:ind vs 纯w:tab字符） ######")
def inline_seq(p):
    seq = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t": seq.append(("text", node.text or "", node))
        elif node.tag == f"{{{W}}}tab": seq.append(("tab", "", node))
        elif node.tag == f"{{{M}}}oMath": seq.append(("math", "", node))
    return seq

tot_lead = 0
for i, p in enumerate(paras):
    seq = inline_seq(p)
    leads = []
    for k, (kind, txt, el) in enumerate(seq):
        if kind != "tab": continue
        before = False
        for j in range(k-1, -1, -1):
            if seq[j][0] == "math" or (seq[j][0] == "text" and seq[j][1].strip()):
                before = True; break
        if not before:
            leads.append(el)
    if not leads: continue
    tot_lead += len(leads)
    ind = p.find(f"{{{W}}}pPr/{{{W}}}ind")
    ind_s = etree.tostring(ind).decode() if ind is not None else "无w:ind"
    wt = "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))
    is_opt = bool(opt_re.search(wt))
    # 该段是否题号块段（以题号正则开头）
    is_num = bool(re.match(r"^1\.2\.5(\.\d+)*-\d+．", wt))
    print(f"p#{i}: LEADtab×{len(leads)} w:ind[{ind_s}] 选项行={is_opt} 题号段={is_num} 文本头={wt[:28]!r}")
print("LEAD总数:", tot_lead)
