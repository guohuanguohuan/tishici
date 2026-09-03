# -*- coding: utf-8 -*-
# FX2b_wt_layer：正确分离w:t层（全部w:t子孙，不含oMath内m:t）vs m:t层（m:t）
# p#3验算：w:t层应含「d=√(|a|²−(a·b/|b|)²)」等线性数学
import re
from lxml import etree

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

doc = etree.parse(BASE + r"\unpacked\word\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

ORIG = [4,175,224,260,273,300,324,331,353,355,364,379,398,429,437,452,460,468,478,480,487,493,539,556,804,897,900,971]

def wt_layer(p):
    """全部w:t文本（p.iter(w:t)，oMath内m:t不属w:t故自然排除）"""
    return "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))

def mt_layer(p):
    return "".join(t.text or "" for t in p.iter(f"{{{M}}}t"))

SIG = re.compile(r"√|\u00b2|\u00b3|[\u2070-\u209f]")

print(f"总段数({len(paras)})")
for oi in ORIG:
    ci = oi - 1
    p = paras[ci]
    wt = wt_layer(p)
    mt = mt_layer(p)
    sig_wt = [m.group() for m in SIG.finditer(wt)]
    print("=" * 105)
    print(f"原p#{oi} 现p#{ci}: w:t签名={sig_wt or 'None'}")
    print(f"  [w:t层全部] {wt!r}")
    if mt:
        print(f"  [m:t层]     {mt!r}")
