# -*- coding: utf-8 -*-
# FX2b探查3：(1)关键段run级+oMath原始XML；(2)p#485/515缺值疑云（图？）；(3)全文w:ind；(4)清单外【编注】线性数学扫描
import re
from lxml import etree

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

doc = etree.parse(BASE + r"\unpacked\word\document.xml")
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

def om_xml(om, maxlen=220):
    s = etree.tostring(om).decode()
    s = re.sub(r'xmlns(:\w+)?="[^"]*"', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s[:maxlen]

def run_dump(i):
    p = paras[i]
    print(f"=== p#{i} run级 ===")
    for j, child in enumerate(p):
        tag = etree.QName(child).localname
        if tag == "r":
            ts = child.findall(f"{{{W}}}t")
            tabs = child.findall(f"{{{W}}}tab")
            dr = child.findall(f"{{{W}}}drawing")
            txt = "".join(t.text or "" for t in ts)
            extra = f" +tab×{len(tabs)}" if tabs else ""
            extra += f" +drawing×{len(dr)}" if dr else ""
            print(f"  [{j}] w:r «{txt}»{extra}")
        elif tag == "oMath":
            mt = "".join(t.text or "" for t in child.iter(f"{{{M}}}t"))
            print(f"  [{j}] oMath m:t=«{mt}»")
            print(f"       XML: {om_xml(child)}")
        elif tag == "pPr":
            print(f"  [{j}] pPr")
        else:
            print(f"  [{j}] {tag}")

# (1) 关键oMath内部结构验看
for i in [3, 259, 272, 436, 477, 492, 555, 803, 970, 378, 363]:
    run_dump(i)

# (2) p#485/p#515 全节点（含图）
print("\n###### p#485 / p#515 全节点扫描（找drawing） ######")
for i in [485, 515]:
    p = paras[i]
    ndr = len(list(p.iter(f"{{{W}}}drawing")))
    print(f"p#{i}: drawing数={ndr}")
    run_dump(i)

# (3) 全文w:ind清点
print("\n###### 全文w:ind清点 ######")
inds = body.findall(f".//{{{W}}}ind")
print("w:ind总数:", len(inds))
for ind in inds[:10]:
    print("  ", etree.tostring(ind).decode()[:150])

# (4) 清单外【编注】句w:t线性数学扫描（28段之外）
print("\n###### 清单外【编注】/题型通式段 w:t签名扫描 ######")
ORIG = {4,175,224,260,273,300,324,331,353,355,364,379,398,429,437,452,460,468,478,480,487,493,539,556,804,897,900,971}
KNOWN_CUR = {oi-1 for oi in ORIG} | {64, 483}  # FX2已修的p#65/484(现64/483)
SIG = re.compile(r"√|[/]|\u00b2|\u00b3|[\u2070-\u209f]|\u00bd|\u2153|\u00b0")
cnt = 0
for i, p in enumerate(paras):
    wt = "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))
    if ("【编注】" not in wt) and ("题型通式" not in wt):
        continue
    if i in KNOWN_CUR:
        continue
    if SIG.search(wt):
        cnt += 1
        print(f"  清单外命中 p#{i}: {wt[:90]}")
print("清单外命中数:", cnt)
