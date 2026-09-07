# -*- coding: utf-8 -*-
from lxml import etree as ET
from docx import Document
from docx.oxml.ns import qn

SRC = r"高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"
doc = Document(SRC)
body = doc.element.body
kids = list(body.iterchildren())
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

def tag(el): return el.tag.split('}')[1]

print("=== [0],[1],[3],[8] 段 pPr + run sz/color ===")
for idx in (0, 1, 3, 8):
    el = kids[idx]
    ppr = el.find(qn("w:pPr"))
    print(f"--- [{idx}] pPr ---")
    print(ET.tostring(ppr, encoding="unicode").replace('><','>\n<')[:600] if ppr is not None else "  (无pPr)")
    for r in el.iter(qn("w:r")):
        rpr = r.find(qn("w:rPr"))
        z = rpr.find(qn("w:sz")) if rpr is not None else None
        c = rpr.find(qn("w:color")) if rpr is not None else None
        t = "".join(x.text or "" for x in r.findall(qn("w:t")))
        print(f"    run sz={z.get(qn('w:val')) if z is not None else '—'} color={c.get(qn('w:val')) if c is not None else '—'} {t[:36]!r}")

print("\n=== [55]..[61],[70]..[72] 子元素轮廓 ===")
for rng in (range(55, 62), range(70, 73)):
    for i in rng:
        el = kids[i]
        parts = []
        for ch in el:
            tg = tag(ch)
            if tg == "r":
                t = "".join(x.text or "" for x in ch.findall(qn("w:t")))
                rpr = ch.find(qn("w:rPr"))
                shd = rpr.find(qn("w:shd")) if rpr is not None else None
                parts.append(f"r(shd={shd.get(qn('w:fill')) if shd is not None else '—'}){t[:14]!r}")
            elif tg == "oMath":
                parts.append("oMath[")
                for mm in ch.iter():
                    if tag(mm) == "r" and mm.tag.startswith(M):
                        t2 = "".join(x.text or "" for x in mm.findall(M+"t"))
                        wrpr = mm.find(qn("w:rPr"))
                        shd2 = wrpr.find(qn("w:shd")) if wrpr is not None else None
                        parts.append(f"m:r(shd={shd2.get(qn('w:fill')) if shd2 is not None else '—'}){t2[:12]!r}")
                parts.append("]")
            else:
                parts.append(tg)
        print(f"[{i}]", " ".join(parts)[:200])

print("\n=== [57] 全文 ===")
print(ET.tostring(kids[57], encoding="unicode").replace('><','>\n<')[:2500])

print("\n=== header1.xml / footer1.xml 内容 ===")
for part in doc.part.package.parts:
    pn = str(part.partname)
    if pn.endswith("header1.xml") or pn.endswith("footer1.xml"):
        print("---", pn, "---")
        print(part.blob.decode("utf-8")[:900])
