# -*- coding: utf-8 -*-
"""FX9 probe7: ①确认部署版E/H六段=仅图像段（无残留run）；②全件复核E/H是否还有其他真空段或纯空白run段；
③X1十五段（11+4）逐段run级解剖。"""
import re
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W}

def dissect(p, label, maxprint=40):
    print("=" * 12, label)
    for child in p:
        tag = etree.QName(child).localname
        if tag == "pPr":
            shd = child.find("w:shd", NS)
            print("  [pPr] shd=%s" % (shd.get("{%s}fill" % W) if shd is not None else None))
        elif tag == "r":
            parts = []
            for el in child.iter():
                t = etree.QName(el).localname
                if t == "t":
                    parts.append("TEXT%r" % (el.text or ""))
                elif t == "drawing":
                    parts.append("DRAWING")
                elif t == "br":
                    parts.append("BR")
                elif t == "tab":
                    parts.append("TAB")
            print("  [r] " + (" | ".join(parts) if parts else "(empty run)"))
        elif tag in ("oMath", "oMathPara"):
            print("  [%s] MATH" % tag)
        else:
            print("  [%s]" % tag)

def load_xml(path):
    return etree.parse(path).getroot()

# ① 部署版六段
rootE = load_xml("E_document.xml")
allpE = list(rootE.iter("{%s}p" % W))
dissect(allpE[261], "E deployed iter p#261")
dissect(allpE[268], "E deployed iter p#268")
rootH = load_xml("H_document.xml")
directH = rootH.find("w:body", NS).findall("w:p", NS)
for i in (362, 595, 864, 868):
    dissect(directH[i], "H deployed direct p#%d" % i)

# ② E/H全件：无文字无图的段（真空段）＋含drawing段的清单（对照图像守恒）
for tag, root in (("E", rootE), ("H", rootH)):
    paras = list(root.iter("{%s}p" % W))
    vac, img = [], []
    for i, p in enumerate(paras):
        txt = "".join(el.text or "" for el in p.iter() if etree.QName(el).localname == "t")
        has_img = any(etree.QName(el).localname == "drawing" for el in p.iter())
        has_math = any(etree.QName(el).localname in ("oMath", "oMathPara") for el in p.iter())
        if re.sub(r"[\s\xa0\u3000]+", "", txt) == "" and not has_img and not has_math:
            vac.append(i)
        if has_img:
            img.append(i)
    print("[%s] 真空段(无字无图无式): %s | 含图段数: %d" % (tag, vac, len(img)))

# ③ X1 十五段解剖
rootX = load_xml("X1_document.xml")
directX = rootX.find("w:body", NS).findall("w:p", NS)
targets = [8, 18, 39, 46, 78, 81, 83, 117, 119, 122, 128, 133, 138, 209, 216]
for i in targets:
    dissect(directX[i], "X1 p#%d" % i)
