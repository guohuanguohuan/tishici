# -*- coding: utf-8 -*-
# FX2b wt_only：28段仅w:t文本（exclude oMath）+线性数学签名判定（真/假阳性）
import re
from lxml import etree

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

doc = etree.parse(BASE + r"\unpacked\word\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

ORIG = [4,175,224,260,273,300,324,331,353,355,364,379,398,429,437,452,460,468,478,480,487,493,539,556,804,897,900,971]

def wt_only(p):
    """p直接子r中的w:t（不含oMath内的m:t）"""
    out = []
    for r in p.findall(f"{{{W}}}r"):
        out.append("".join(t.text or "" for t in r.findall(f"{{{W}}}t")))
    return "".join(out)

def mt_join(p):
    return "".join(t.text or "" for t in p.iter(f"{{{M}}}t"))

# 签名：含数学运算符/方根/上下标/除号/±加减
SIG = re.compile(r"√|\u00b2|\u00b3|[\u2070-\u209f]")

print("### 判定标准：w:t层含数学签名（√/²/³/上下标/行内分数）→真阳性；仅出现在m:t→假阳性 ###")
for oi in ORIG:
    ci = oi - 1
    p = paras[ci]
    wt = wt_only(p)
    mt = mt_join(p)
    sig_in_wt = [m.group() for m in SIG.finditer(wt)]
    sig_in_mt = [m.group() for m in SIG.finditer(mt)]
    verdict = "真阳性" if sig_in_wt else ("假阳性(m:t)" if sig_in_mt else "无签名")
    print("=" * 105)
    print(f"原p#{oi} 现p#{ci}: 判定={verdict}")
    print(f"  w:t文 {'(no w:t sig)' if not sig_in_wt else ''}: {wt!r}")
    if sig_in_wt:
        print(f"    w:t签名: {sig_in_wt}")
    if mt:
        print(f"  m:t集 : {mt!r}")
