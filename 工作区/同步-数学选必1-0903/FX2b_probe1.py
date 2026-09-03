# -*- coding: utf-8 -*-
# FX2b探查1：28段创作句线性数学候选（FX2原索引−1）逐段验真：w:t层 vs m:t层
import re
from lxml import etree

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

doc = etree.parse(BASE + r"\unpacked\word\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
print("总段数:", len(paras))

ORIG = [4,175,224,260,273,300,324,331,353,355,364,379,398,429,437,452,460,468,478,480,487,493,539,556,804,897,900,971]

def wt_text(p):
    return "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))

def mt_text(p):
    return "".join(t.text or "" for t in p.iter(f"{{{M}}}t"))

SIG = re.compile(r"√|[/]|\u00b2|\u00b3|[\u2070-\u209f]|[\uff0d]|[\u2212]")

for oi in ORIG:
    ci = oi - 1
    p = paras[ci]
    wt = wt_text(p)
    mt = mt_text(p)
    style = p.find(f"{{{W}}}pPr/{{{W}}}pStyle")
    sv = style.get(f"{{{W}}}val") if style is not None else "-"
    n_om = len(list(p.iter(f"{{{M}}}oMath")))
    print("=" * 100)
    print(f"原p#{oi} 现p#{ci} 样式={sv} oMath块数={n_om}")
    print(f"  [w:t全文] {wt}")
    if mt:
        print(f"  [m:t既有] {mt}")
    # w:t中的线性数学签名片段
    hits = []
    for mm in SIG.finditer(wt):
        a = max(0, mm.start() - 25); b = min(len(wt), mm.end() + 25)
        hits.append(wt[a:b])
    if hits:
        print(f"  [w:t签名片段] {' | '.join(repr(h) for h in hits[:8])}")
