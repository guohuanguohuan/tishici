# -*- coding: utf-8 -*-
"""FX9 probe2: 口径勘定——iter全量段（含表内） vs body直接子段；空段按iter口径重扫。"""
import re
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

def para_text(p):
    parts = []
    for el in p.iter():
        tag = etree.QName(el).localname
        if tag == "t":
            parts.append(el.text or "")
        elif tag == "drawing":
            parts.append("⟦IMG⟧")
    return "".join(parts)

def para_has_content(p):
    for el in p.iter():
        tag = etree.QName(el).localname
        if tag in ("drawing", "object", "oMath", "oMathPara"):
            return True
    return False

for tag in ["E", "H", "X1"]:
    tree = etree.parse(tag + "_document.xml")
    root = tree.getroot()
    body = root.find("w:body", NS)
    direct = body.findall("w:p", NS)
    allp = root.iter("{%s}p" % W)
    allp = list(allp)
    ntbl = len(body.findall("w:tbl", NS))
    # empty by iter-口径 (norm text empty & no content)
    empties = []
    for i, p in enumerate(allp):
        txt = para_text(p)
        if re.sub(r"[\s\xa0\u3000]+", "", txt) == "" and not para_has_content(p):
            empties.append(i)
    print(tag, "direct paras:", len(direct), "| iter-all paras:", len(allp),
          "| top tables:", ntbl, "| sectPr-in-pPr count:",
          len(root.findall(".//w:pPr/w:sectPr", NS)), "| empty(iter idx):", empties)
    for i in empties:
        for j in range(max(0, i - 2), min(len(allp), i + 3)):
            mark = ">>" if j == i else "  "
            t = para_text(allp[j])
            t_show = t if len(t) <= 110 else t[:110] + "…"
            print("%s p#%d: %r" % (mark, j, t_show))
        print("-" * 8)
