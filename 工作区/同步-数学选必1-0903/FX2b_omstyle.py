# -*- coding: utf-8 -*-
# FX2b_omstyle：验看既有oMath内部XML房型（m:rad/m:f/sup/normal run）供建房
from lxml import etree

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

doc = etree.parse(BASE + r"\unpacked\word\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

import re
def clean(s):
    s = re.sub(r'xmlns(:\w+)?="[^"]*"', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s

# p#259 的 a² / a³ oMath XML；p#364 的 =1+√2 / r² oMath XML；p#5 的 √(3) oMath（选项既有房型对照）
print("===== p#259 (原260) oMath XML =====")
for om in paras[259].iter(f"{{{M}}}oMath"):
    print("  om_lin:", "".join(t.text or "" for t in om.iter(f"{{{M}}}t")))
    print("  ", clean(etree.tostring(om).decode()))
    print()

print("===== p#363 (原364) oMath XML =====")
for om in paras[363].iter(f"{{{M}}}oMath"):
    print("  om_lin:", "".join(t.text or "" for t in om.iter(f"{{{M}}}t")))
    print("  ", clean(etree.tostring(om).decode()))
    print()

print("===== p#5 选项 √(3) oMath XML (既有房型对照) =====")
for om in paras[5].iter(f"{{{M}}}oMath"):
    print("  om_lin:", "".join(t.text or "" for t in om.iter(f"{{{M}}}t")))
    print("  ", clean(etree.tostring(om).decode()))
    print()

print("===== p#803 (原804) R²=r²+( oMath XML =====")
for om in paras[803].iter(f"{{{M}}}oMath"):
    print("  om_lin:", "".join(t.text or "" for t in om.iter(f"{{{M}}}t")))
    print("  ", clean(etree.tostring(om).decode()))
    print()
