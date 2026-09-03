# -*- coding: utf-8 -*-
"""FX9 probe3: 对比 FX6/H_fixed.docx（FX6部署态）与当前部署H——空段定位（两种口径）＋段落计数＋diff定位。"""
import re, zipfile, io
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

def load_paras(path):
    with zipfile.ZipFile(path) as z:
        data = z.read("word/document.xml")
    root = etree.fromstring(data)
    body = root.find("w:body", NS)
    return body, body.findall("w:p", NS), list(root.iter("{%s}p" % W))

def para_text(p):
    parts = []
    for el in p.iter():
        tag = etree.QName(el).localname
        if tag == "t":
            parts.append(el.text or "")
        elif tag == "drawing":
            parts.append("⟦IMG⟧")
    return "".join(parts)

def has_content(p):
    for el in p.iter():
        if etree.QName(el).localname in ("drawing", "object", "oMath", "oMathPara"):
            return True
    return False

for name, path in [
    ("FX6_H_fixed", r"C:\提示词\工作区\同步-数学选必1-0903\FX6\H_fixed.docx"),
    ("H_deployed", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx"),
    ("FX3_E_fixed", r"C:\提示词\工作区\同步-数学选必1-0903\FX3_E\E_fixed.docx"),
    ("E_deployed", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx"),
]:
    body, direct, allp = load_paras(path)
    ed = [i for i, p in enumerate(direct) if re.sub(r"[\s\xa0\u3000]+", "", para_text(p)) == "" and not has_content(p)]
    ea = [i for i, p in enumerate(allp) if re.sub(r"[\s\xa0\u3000]+", "", para_text(p)) == "" and not has_content(p)]
    print(name, "| direct:", len(direct), "empty@direct:", ed, "| iter:", len(allp), "empty@iter:", ea)
