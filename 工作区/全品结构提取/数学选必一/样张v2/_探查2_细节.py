# -*- coding: utf-8 -*-
import re
from docx import Document
from docx.oxml.ns import qn

SRC = r"高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"
doc = Document(SRC)
body = doc.element.body
kids = list(body.iterchildren())
cut = 173

print("=== sectPr（body 末尾）===")
sectPr = body.find(qn("w:sectPr"))
import xml.dom.minidom
print(xml.dom.minidom.parseString(sectPr.xml if hasattr(sectPr,'xml') else __import__('lxml.etree',fromlist=['etree']).tostring(sectPr).decode()).toprettyxml()[:3000])
