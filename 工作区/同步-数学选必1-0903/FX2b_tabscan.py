# -*- coding: utf-8 -*-
# FX2b_tabscan：Task3 全文所有段首tab清点（不管是否选项行）+全文w:ind清点
import re
from lxml import etree

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

doc = etree.parse(BASE + r"\unpacked\word\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

opt_re = re.compile(r"[ABCD]．")

def inline_seq(p):
    seq = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            seq.append(("t", node.text or "", node))
        elif node.tag == f"{{{W}}}tab":
            seq.append(("tab", "", node))
        elif node.tag == f"{{{M}}}oMath":
            seq.append(("m", "", node))
    return seq

# 1) 全文w:ind清点
inds = body.findall(f".//{{{W}}}ind")
print("=== 全文w:ind总数 ===", len(inds))
for ind in inds[:20]:
    p = ind.getparent().getparent() if ind.getparent() is not None else None
    # w:ind的父是pPr，pPr的父是p
    pp = ind.getparent()
    p = pp.getparent() if pp is not None else None
    tag = etree.QName(p).localname if p is not None else "?"
    # 该段文本头
    wt = "".join(t.text or "" for t in p.iter(f"{{{W}}}t")) if p is not None else ""
    ind_s = etree.tostring(ind).decode()
    print(f"  ind:{ind_s[:90]} | 段标签={tag} | 文头={wt[:40]!r}")

# 2) 所有段首tab（leading tabs）清点，标注是否选项行/题号段
lead_total = 0
option_leads = 0
nonopt_leads = 0
print("=== 段首tab清点 ===")
for i, p in enumerate(paras):
    seq = inline_seq(p)
    leads = []
    for k, (kind, txt, el) in enumerate(seq):
        if kind != "tab": continue
        before_content = False
        for j in range(k-1, -1, -1):
            if seq[j][0] == "m" or (seq[j][0] == "t" and seq[j][1].strip()):
                before_content = True; break
        if not before_content:
            leads.append(el)
    if not leads: continue
    wt = "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))
    is_opt = bool(opt_re.search(wt))
    is_num = bool(re.match(r"^1\.2\.5(\.\d+)*-\d+(\.\d+)*．", wt))
    lead_total += len(leads)
    if is_opt:
        option_leads += len(leads)
    else:
        nonopt_leads += len(leads)
    print(f"  p#{i}: lead×{len(leads)} 选项行={is_opt} 题号段={is_num} 文头={wt[:24]!r}")
print(f"LEAD总数={lead_total} 选项行内={option_leads} 非选项行={nonopt_leads}")
