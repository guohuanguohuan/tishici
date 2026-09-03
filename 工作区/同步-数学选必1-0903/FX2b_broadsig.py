# -*- coding: utf-8 -*-
# FX2b_broadsig：28段w:t层宽数学签名扫描（√ ² ³ 上标 下标 /分数 ÷×以及连缀表达式）
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
    return "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))

# 关键数学签名：方根/上下标字符/连缀数字字母混合的表达式
KB = re.compile(r"√|\u00b2|\u00b3|\u00b9|[\u2070-\u209f]")
# 分数/除式：数字或变量后跟/再跟数字或变量，且位于非"文字斜杠"语境（简判：/前后各是数字或字母或)或deg）
FRAC = re.compile(r"(?<![^\s\dA-Za-z)])([\dA-Za-z)]+?)/([\dA-Za-z.^]+)")

for oi in ORIG:
    ci = oi - 1
    p = paras[ci]
    wt = wt_layer(p)
    kb = [m.group() for m in KB.finditer(wt)]
    frac = [m.group(0) for m in FRAC.finditer(wt)]
    print("=" * 100)
    print(f"原p#{oi} 现p#{ci}: KB={kb or 'None'} FRAC={frac or 'None'}")
