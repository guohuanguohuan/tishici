# -*- coding: utf-8 -*-
"""FX6 probe9: 正确的结构dump——全部④命中段: d的dPr(begChr/sepChr)+eqArr有无+叶子"""
import re, io
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H"
tree = etree.parse(BASE + r"\word\document.xml")
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
buf = io.StringIO()
def P(*a): print(*a, file=buf)

def describe(om):
    """完整结构描述：递归所有，含eqArr行、d的chr属性、f/rad"""
    def d_el(el, depth):
        parts = []
        for ch in el:
            ln = etree.QName(ch).localname
            if ln == "r":
                parts.append("".join(ch.itertext()))
            elif ln == "rPr" or ln == "ctrlPr":
                continue
            elif ln == "d":
                dPr = ch.find(f"{{{M}}}dPr")
                beg = sep = end = None
                if dPr is not None:
                    b = dPr.find(f"{{{M}}}begChr"); s = dPr.find(f"{{{M}}}sepChr"); e = dPr.find(f"{{{M}}}endChr")
                    beg = b.get(f"{{{M}}}val") if b is not None else "("
                    sep = s.get(f"{{{M}}}val") if s is not None else "|"
                    end = e.get(f"{{{M}}}val") if e is not None else ")"
                inner = d_el(ch.find(f"{{{M}}}e"), depth+1) if ch.find(f"{{{M}}}e") is not None else ""
                parts.append(f"d[{beg}…{sep}…{end}]({inner})")
            elif ln == "eqArr":
                rows = ch.findall(f"{{{M}}}e")
                parts.append("eqArr[" + " ⏎ ".join(d_el(r, depth+1) for r in rows) + "]")
            elif ln == "f":
                n = ch.find(f"{{{M}}}num"); d2 = ch.find(f"{{{M}}}den")
                parts.append(f"f({d_el(n, depth+1) if n is not None else ''}/{d_el(d2, depth+1) if d2 is not None else ''})")
            elif ln == "rad":
                e2 = ch.find(f"{{{M}}}e")
                parts.append(f"√({d_el(e2, depth+1) if e2 is not None else ''})")
            elif ln == "sSup":
                e2 = ch.find(f"{{{M}}}e"); sup = ch.find(f"{{{M}}}sup")
                parts.append(f"{d_el(e2, depth+1) if e2 is not None else ''}^({d_el(sup, depth+1) if sup is not None else ''})")
            elif ln == "sSub":
                e2 = ch.find(f"{{{M}}}e"); sb = ch.find(f"{{{M}}}sub")
                parts.append(f"{d_el(e2, depth+1) if e2 is not None else ''}_({d_el(sb, depth+1) if sb is not None else ''})")
            elif ln in ("num","den","deg","e","sup","sub"):
                parts.append(d_el(ch, depth+1))
            else:
                parts.append(f"<{ln}>")
        return "".join(parts)
    return d_el(om, 0)

KEYS = ["x=1y=±2", "x=1y=2", "x=-1y=14", "y=tx+12y=x22", "x23+y22=1y=kx+1",
        "y22+x2=1y=kx+1", "2b=2e=ca=32", "x24−y212=1y=kx+4", "ca=2232a=6",
        "x=3y=−3", "y=kx−1+1y=22x"]
for k, p in enumerate(paras):
    for om in p.iter(f"{{{M}}}oMath"):
        lin = "".join(om.itertext())
        for key in KEYS:
            if key in lin:
                P(f"p#{k} [{key[:12]}]:")
                P("   ", describe(om))
                P("")
                break

open(BASE.replace("tmp\\FX6_H", "FX6") + r"\扫描-probe9.txt", "w", encoding="utf-8").write(buf.getvalue())
print("written")
