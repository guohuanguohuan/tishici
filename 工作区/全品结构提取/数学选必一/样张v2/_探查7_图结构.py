# -*- coding: utf-8 -*-
from lxml import etree as ET
from docx import Document
from docx.oxml.ns import qn

SRC = r"高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"
doc = Document(SRC)
kids = list(doc.element.body.iterchildren())

def brief(el, depth=0, maxdepth=6):
    tg = el.tag.split('}')[1]
    ns = el.tag.split('}')[0].split('/')[-1] if '}' in el.tag else '?'
    attrs = {k.split('}')[-1]: v for k, v in el.attrib.items()
             if k.split('}')[-1] in ('cx','cy','x','y','off','ext') or 'off' in k.lower() or 'ext' in k.lower()}
    line = "  "*depth + f"{ns}:{tg} {attrs if attrs else ''}"
    print(line[:160])
    if depth < maxdepth:
        for ch in el: brief(ch, depth+1, maxdepth)

for idx in (45, 81, 150):
    dr = kids[idx].find(".//" + qn("w:drawing"))
    print("="*20, f"源文件 段[{idx}] drawing", "="*20)
    brief(dr, maxdepth=4)
