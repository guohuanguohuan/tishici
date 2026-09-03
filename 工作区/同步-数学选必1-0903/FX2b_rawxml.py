# -*- coding: utf-8 -*-
# FX2b rawxml：打印目标段原始XML（看oMath是否w:p直接子级）
import re
from lxml import etree

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

doc = etree.parse(BASE + r"\unpacked\word\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

def show(i):
    p = paras[i]
    s = etree.tostring(p).decode()
    s = re.sub(r'\s+', ' ', s)
    print(f"===== p#{i} =====")
    print(s[:3000])
    print()

for i in [3, 259, 299]:
    show(i)
