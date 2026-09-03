# -*- coding: utf-8 -*-
"""FX9 probe9: p#209与p#8的run级精细解剖（含shd灰底、rPr、嵌套检查）＋p#0-15上下文＋全件（　）答题位形态盘点。"""
import re
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W}

root = etree.parse("X1_document.xml").getroot()
paras = root.find("w:body", NS).findall("w:p", NS)

def runs_detail(p, label):
    print("=" * 12, label)
    for child in p:
        q = etree.QName(child)
        if q.localname == "pPr":
            shd = child.find("w:shd", NS)
            print("  [pPr] shd=%s" % (shd.get("{%s}fill" % W) if shd is not None else None))
            continue
        if q.localname in ("oMath", "oMathPara"):
            mm = "".join(t.text or "" for t in child.iter("{%s}t" % M))
            # check for w:r INSIDE oMath (illegal nesting)
            nested = [e for e in child.iter() if etree.QName(e).localname == "r" and etree.QName(e).namespace == W]
            print("  [oMath] ⟦%s⟧ nested_w_r=%d" % (mm, len(nested)))
            continue
        if q.localname == "r":
            rpr = child.find("w:rPr", NS)
            shd = rpr.find("w:shd", NS) if rpr is not None else None
            shd_v = shd.get("{%s}fill" % W) if shd is not None else "-"
            texts = [(el.text or "") for el in child.findall("w:t", NS)]
            has_math = child.find(".//{%s}oMath" % M) is not None
            n_draw = len(child.findall(".//w:drawing", NS))
            desc = "TEXT%r" % texts if texts else ""
            if has_math:
                inner = "".join(t.text or "" for t in child.iter("{%s}t" % M))
                desc += " +嵌套oMath⟦%s⟧" % inner
            if n_draw:
                desc += " +DRAWING×%d" % n_draw
            print("  [r shd=%s] %s" % (shd_v, desc or "(empty)"))
        else:
            print("  [%s]" % q.localname)

runs_detail(paras[209], "X1 p#209 run解剖")
runs_detail(paras[8], "X1 p#8 run解剖")

print()
print("### p#0..p#15 上下文")
def lin(p):
    out = []
    def walk(el):
        for ch in el:
            qn = etree.QName(ch)
            if qn.namespace == W and qn.localname == "t":
                out.append(ch.text or "")
            elif qn.namespace == M and qn.localname in ("oMath", "oMathPara"):
                out.append("⟦" + "".join(t.text or "" for t in ch.iter("{%s}t" % M)) + "⟧")
            elif qn.namespace == W and qn.localname == "drawing":
                out.append("⟦IMG⟧")
            elif qn.namespace == W and qn.localname in ("r", "hyperlink"):
                walk(ch)
    walk(p)
    return "".join(out)

for i in range(0, 16):
    print("p#%d: %s" % (i, lin(paras[i])[:120]))

print()
print("### 全件（　）答题位形态盘点")
for i, p in enumerate(paras):
    t = lin(p)
    for m in re.finditer(r"（[\s\xa0\u3000]*）|\([\s\xa0\u3000]*\)|（[\s\xa0\u3000]{1,6}）", t):
        seg = m.group(0)
        print("p#%d: 答题位=%r 上下文=…%s…" % (i, seg, t[max(0, m.start()-25):m.end()+10]))
