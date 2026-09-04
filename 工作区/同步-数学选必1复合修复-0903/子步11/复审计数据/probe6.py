# -*- coding: utf-8 -*-
import re, zipfile
from lxml import etree
W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M="{http://schemas.openxmlformats.org/officeDocument/2006/math}"
p=r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"
z=zipfile.ZipFile(p)
root=etree.fromstring(z.read("word/document.xml"))
body=root.find(W+"body")
paras=[]
for para in body.iter(W+"p"):
    t_all="".join(n.text or "" for n in para.iter() if n.tag in (W+"t",M+"t"))
    t_math="".join(n.text or "" for n in para.iter() if n.tag==M+"t")
    paras.append((para,t_all,t_math))
def nows(s): return re.sub(r"\s+","",s)
for i in range(468,482):
    _,ta,tm=paras[i]
    print("--- para",i)
    print("ALL:",ta[:300])
    print("MATH:",tm[:300])
