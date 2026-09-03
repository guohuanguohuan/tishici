# -*- coding: utf-8 -*-
"""FX6 probe7: ④23处全量结构判定导出 + rels验证 + p#417选项语境"""
import re, io
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H"
tree = etree.parse(BASE + r"\word\document.xml")
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
buf = io.StringIO()
def P(*a): print(*a, file=buf)

# ④目标串（工具23处的内容键）
KEYS = ["x=1y=±2", "x=1y=2", "Δ=16−4k", "Δ=-2k2+8m", "x=-1y=14",
        "y=tx+12y=x22", "64c29−6c2", "AFBF=2=a+12ca−12c", "x23+y22=1y=kx+1",
        "p+2pk2", "S△MF1F2=12|F1F2|", "yA−1m+−yA−1m", "yA+1m+−yA+1m",
        "y22+x2=1y=kx+1", "2b=2e=ca=32", "S△ODE=12a×2b", "x24−y212=1y=kx+4",
        "kx1+4+kx2+4", "ca=2232a=6", "MN=1+k2x1−x2", "12×m2×221−2m",
        "x=3y=−3", "y=kx−1+1y=22x"]

def om_info(om):
    """OMML结构摘要: 元素序列含关键结构 + m:r文本切分"""
    rs = []
    def walk(el):
        for ch in el:
            ln = etree.QName(ch).localname
            if ln == "r":
                t = "".join(ch.itertext())
                rs.append(t)
            else:
                rs.append(f"⟨{ln}⟩")
                if ln in ("f", "d", "sSup", "sSub", "eqArr", "rad", "nary", "bar"):
                    walk(ch)
    walk(om)
    return rs

seen = set()
for k, p in enumerate(paras):
    for om in p.iter(f"{{{M}}}oMath"):
        lin = "".join(om.itertext())
        for key in KEYS:
            if key in lin and (k, key[:14]) not in seen:
                seen.add((k, key[:14]))
                P(f"\n=== p#{k} | {lin[:90]!r}")
                P("  切分:", om_info(om))

# rels 验证
P("\n=== document.xml.rels: header/footer 引用 ===")
rt = etree.parse(BASE + r"\word\_rels\document.xml.rels")
for rel in rt.getroot():
    if "header" in rel.get("Target", "") or "footer" in rel.get("Target", ""):
        P(" ", rel.get("Id"), rel.get("Type", "").split("/")[-1], rel.get("Target"))

# p#417 选项行run级（验证A/B/C空值）
P("\n=== p#417 选项行结构 ===")
for r in paras[417].iter(f"{{{W}}}r"):
    rPr = r.find(f"{{{W}}}rPr")
    kinds = [etree.QName(c).localname for c in r]
    txt = "".join(t.text or "" for t in r.findall(f"{{{W}}}t"))
    P(f"  子={kinds} 文本={txt!r}")
P("段内drawing数:", len(paras[417].findall(f".//{{{W}}}drawing")))

# p#416-418 全文
for q in (415, 416, 417, 418):
    P(f"p#{q}:", "".join(paras[q].itertext())[:160])

open(BASE.replace("tmp\\FX6_H", "FX6") + r"\扫描-probe7.txt", "w", encoding="utf-8").write(buf.getvalue())
print("written")
