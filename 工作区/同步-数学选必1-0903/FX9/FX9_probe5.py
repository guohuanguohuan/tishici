# -*- coding: utf-8 -*-
"""FX9 probe5: 检查FX前修复版中这些段落的完整XML结构（E前版p#261/268 iter口径；H前版p#363/596/865/869 direct口径）。"""
import re, zipfile
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

def load(path):
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read("word/document.xml"))
    return root, list(root.iter("{%s}p" % W)), root.find("w:body", NS).findall("w:p", NS)

# E 前修复版（FX3_E/E_backup.docx = git eca5560 态）
rootE, allpE, _ = load(r"C:\提示词\工作区\同步-数学选必1-0903\FX3_E\E_backup.docx")
print("### E pre-fix iter p#261 / p#268 full XML")
for i in (261, 268):
    xml = etree.tostring(allpE[i], encoding="unicode")
    print("--- p#%d (len %d):" % (i, len(xml)))
    print(re.sub(r"\s+", " ", xml)[:1500])
    print()

# H 前修复版（FX6/H_备份-0903.docx）
rootH, _, directH = load(r"C:\提示词\工作区\同步-数学选必1-0903\FX6\H_备份-0903.docx")
print("### H pre-fix direct p#363/596/865/869 full XML")
for i in (363, 596, 865, 869):
    xml = etree.tostring(directH[i], encoding="unicode")
    print("--- p#%d (len %d):" % (i, len(xml)))
    print(re.sub(r"\s+", " ", xml)[:1500])
    print()
