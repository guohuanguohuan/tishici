# -*- coding: utf-8 -*-
"""FX9 probe1: E/H 真空段定位——枚举全部「无文字、无图、无公式、无表格」的空段，
并打印疑似段的前后邻居文本，核对衔接。"""
import re
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

def para_text(p):
    """text stream: w:t + m:t in doc order, oMath as [M] atoms."""
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
        if tag == "drawing" or tag == "object":
            return True
        if tag == "oMath" or tag == "oMathPara":
            return True
    return False

def norm(s):
    return re.sub(r"[\s\xa0\u3000]+", "", s)

for tag in ["E", "H"]:
    tree = etree.parse(tag + "_document.xml")
    body = tree.getroot().find("w:body", NS)
    paras = body.findall("w:p", NS)
    empties = []
    for i, p in enumerate(paras):
        txt = para_text(p)
        if norm(txt) == "" and not para_has_content(p) and p.find("w:pPr/w:sectPr", NS) is None:
            empties.append(i)
    print("=" * 20, tag, "total paras:", len(paras), "empty paras:", len(empties), empties)
    for i in empties:
        print("-" * 10, tag, "p#%d context:" % i)
        for j in range(max(0, i - 2), min(len(paras), i + 3)):
            mark = ">>" if j == i else "  "
            t = para_text(paras[j])
            t_show = t if len(t) <= 100 else t[:100] + "…"
            # show raw repr to reveal nbsp etc
            print("%s p#%d: %r" % (mark, j, t_show))
