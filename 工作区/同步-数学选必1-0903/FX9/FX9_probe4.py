# -*- coding: utf-8 -*-
"""FX9 probe4: 直击E iter口径 p#258~272、H direct口径 p#360~366/593~599/862~870 的原始XML与文本。"""
import re, zipfile
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

def load(path):
    if path.endswith(".xml"):
        root = etree.parse(path).getroot()
    else:
        with zipfile.ZipFile(path) as z:
            root = etree.fromstring(z.read("word/document.xml"))
    return root, list(root.iter("{%s}p" % W)), root.find("w:body", NS).findall("w:p", NS)

def para_text(p):
    parts = []
    for el in p.iter():
        tag = etree.QName(el).localname
        if tag == "t":
            parts.append(el.text or "")
        elif tag == "drawing":
            parts.append("⟦IMG⟧")
    return "".join(parts)

root, allp, direct = load("E_document.xml")
print("### E iter p#258..272")
for i in range(258, 273):
    p = allp[i]
    xml = etree.tostring(p, encoding="unicode")
    print("p#%d len=%d text=%r" % (i, len(xml), para_text(p)[:80]))
    if len(xml) < 600:
        print("   XML:", re.sub(r"\s+", " ", xml)[:590])

rootH, allpH, directH = load("H_document.xml")
print("\n### H direct p#360..366")
for i in range(360, 367):
    print("p#%d text=%r" % (i, para_text(directH[i])[:80]))
print("### H direct p#593..599")
for i in range(593, 600):
    print("p#%d text=%r" % (i, para_text(directH[i])[:80]))
print("### H direct p#862..870")
for i in range(862, 871):
    print("p#%d text=%r" % (i, para_text(directH[i])[:80]))
