# -*- coding: utf-8 -*-
"""FX9 probe8: X1全件空格盘点——逐段枚举 nbsp(\xa0)/全角空格(\u3000)/半角空格 的run级位置，
线性化全文（含m:t）输出p#8/81/138/209/216上下文与p#209整题。"""
import re
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W}

root = etree.parse("X1_document.xml").getroot()
body = root.find("w:body", NS)
paras = body.findall("w:p", NS)

def lin(p):
    """full linearization: w:t text + oMath as ⟦…⟧ (m:t inside)."""
    out = []
    def walk(el):
        for ch in el:
            q = etree.QName(ch)
            if q.namespace == W and q.localname == "t":
                out.append(ch.text or "")
            elif q.namespace == M and q.localname in ("oMath", "oMathPara"):
                mm = "".join(t.text or "" for t in ch.iter("{%s}t" % M))
                out.append("⟦" + mm + "⟧")
            elif q.namespace == W and q.localname == "drawing":
                out.append("⟦IMG⟧")
            elif q.namespace == W and q.localname == "r":
                walk(ch)
            elif q.namespace == W and q.localname in ("hyperlink", "smartTag"):
                walk(ch)
    walk(p)
    return "".join(out)

print("### X1 全件 nbsp / U+3000 盘点（段号｜计数｜线性化片段）")
for i, p in enumerate(paras):
    t = lin(p)
    n_a, n_u, n_s = t.count("\xa0"), t.count("\u3000"), None
    if n_a or n_u:
        frag = t
        # 截取含空格的窗口
        print("p#%d nbsp=%d U3000=%d :: %s" % (i, n_a, n_u, frag[:160]))

print()
print("### 目标段完整线性化")
for i in (8, 78, 81, 83, 117, 138, 209, 216):
    print("--- p#%d:" % i)
    print(lin(paras[i]))
    print()

print("### p#209 所属整题（向前找题号块、向后找【知识点】/下一题号块）")
start = None
for j in range(209, -1, -1):
    t = lin(paras[j])
    if re.match(r"^\d+(\.\d+)*-\d+．", t) or re.match(r"^\d+\.\d+\.\d+\.\d+-\d+．", t):
        start = j
        break
print("题号块起点 p#%d" % start)
for j in range(start, min(start + 40, len(paras))):
    t = lin(paras[j])
    if j > start and (re.match(r"^\d+\.\d+\.\d+\.\d+-\d+．", t) or t.startswith("1.2.5 ") or "本节" in t[:30]):
        print("  [p#%d] <<下一题>> %s" % (j, t[:60]))
        break
    print("  [p#%d] %s" % (j, t))
