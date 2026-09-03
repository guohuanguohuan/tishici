# -*- coding: utf-8 -*-
"""FX9 probe6: 完整解剖前修复版6段（E 261/268；H 363/596/865/869）与现部署版对应段——
逐run枚举（text/drawing/尺寸），判定FX前手到底清了什么、现态是什么。"""
import zipfile
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W}

def load_all(path):
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read("word/document.xml"))
    return root, list(root.iter("{%s}p" % W)), root.find("w:body", NS).findall("w:p", NS)

def dissect(p, label):
    print("=" * 15, label)
    # runs in direct children order
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
                    ext = el.find(".//{%s}extent" % WP)
                    if ext is None:
                        ext = el.find(".//{%s}wp14:extent" % WP)
                    dim = (ext.get("cx"), ext.get("cy")) if ext is not None else ("?", "?")
                    blip = el.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip")
                    rid = blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed") if blip is not None else "?"
                    anchor = el.find(".//{%s}anchor" % WP) is not None
                    inline = el.find(".//{%s}inline" % WP) is not None
                    parts.append("DRAWING rid=%s extent=%s inline=%s anchor=%s" % (rid, dim, inline, anchor))
                elif t == "br":
                    parts.append("BR")
            print("  [r] " + (" | ".join(parts) if parts else "(empty run)"))
        else:
            print("  [%s]" % tag)

# 前修复版
rootE, allpE, _ = load_all(r"C:\提示词\工作区\同步-数学选必1-0903\FX3_E\E_backup.docx")
dissect(allpE[261], "E pre-fix p#261")
dissect(allpE[268], "E pre-fix p#268")
rootH, _, directH = load_all(r"C:\提示词\工作区\同步-数学选必1-0903\FX6\H_备份-0903.docx")
for i in (363, 596, 865, 869):
    dissect(directH[i], "H pre-fix p#%d" % i)

# 现部署版对应段
rootE2, allpE2, _ = load_all("E_document.xml")
dissect(allpE2[261], "E deployed p#261 (iter)")
dissect(allpE2[268], "E deployed p#268 (iter)")
rootH2, _, directH2 = load_all("H_document.xml")
for i in (362, 595, 864, 868):
    dissect(directH2[i], "H deployed p#%d (direct)" % i)
