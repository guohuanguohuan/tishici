# -*- coding: utf-8 -*-
from lxml import etree as ET
from docx import Document
from docx.oxml.ns import qn

OUT = r"工作区/全品结构提取/数学选必一/样张v2/人教B版选必1-1.1.1-v2样张.docx"
doc = Document(OUT)
body = doc.element.body
kids = list(body.iterchildren())
print("body 子元素数:", len(kids))
for i, el in enumerate(kids[-6:]):
    idx = len(kids)-6+i
    tag = el.tag.split('}')[1]
    t = "".join(x.text or "" for x in el.iter(qn("w:t")))
    sty = ""
    ppr = el.find(qn("w:pPr")) if tag == "p" else None
    if ppr is not None:
        ps = ppr.find(qn("w:pStyle"))
        sty = ps.get(qn("w:val")) if ps is not None else ""
        sp = ppr.find(qn("w:spacing"))
        spv = ET.tostring(sp, encoding="unicode")[:120] if sp is not None else "无spacing"
        ind = ppr.find(qn("w:ind"))
        indv = ET.tostring(ind, encoding="unicode")[:140] if ind is not None else "无ind"
    print(f"[{idx}] {tag} sty={sty!r} text={t[:40]!r}")
    if tag == "p":
        print("      spacing:", spv)
        print("      ind:", indv)

import pymupdf
d = pymupdf.open(r"工作区/全品结构提取/数学选必一/样张v2/人教B版选必1-1.1.1-v2样张.pdf")
p7 = d[6]
print("\nPDF第7页 文本:", repr(p7.get_text()[:200]))
print("PDF第6页 尾部文本:", repr(d[5].get_text()[-200:]))
