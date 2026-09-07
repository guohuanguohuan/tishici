# -*- coding: utf-8 -*-
import re
from collections import Counter
from lxml import etree as ET
from docx import Document
from docx.oxml.ns import qn

SRC = r"高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"
doc = Document(SRC)
body = doc.element.body
kids = list(body.iterchildren()); cut = 173

def ptext(p): return "".join(t.text or "" for t in p.iter(qn("w:t")))
def x(el, n=1600): return ET.tostring(el, encoding="unicode").replace("><", ">\n<")[:n]

print("=== A. styles.xml 关键定义 ===")
styles = doc.styles.element
dd = styles.find(qn("w:docDefaults"))
print("--- docDefaults ---"); print(x(dd, 1500))
for sid in ("Normal", "a", "Heading3", "标题3", "JieMingMao"):
    for st in styles.findall(qn("w:style")):
        if st.get(qn("w:styleId")) == sid:
            print(f"--- style {sid} ---"); print(x(st, 1100)); break

print("\n=== B. run 级 C7C7C7 的归属 ===")
for i, el in enumerate(kids[:cut]):
    if el.tag != qn("w:p"): continue
    hits = []
    for r in el.findall(qn("w:r")):
        rpr = r.find(qn("w:rPr"))
        if rpr is None: continue
        shd = rpr.find(qn("w:shd"))
        if shd is not None and shd.get(qn("w:fill")) == "C7C7C7":
            hits.append("".join(xx.text or "" for xx in r.findall(qn("w:t"))))
    if hits:
        print(f"[{i:3}] 段首={ptext(el)[:22]!r} n={len(hits)} {[h[:16] for h in hits]}")

print("\n=== C. 表格内 w:shd 父层级 ===")
for ti, el in enumerate([e for e in kids[:cut] if e.tag == qn("w:tbl")]):
    lv = Counter()
    for shd in el.iter(qn("w:shd")):
        lv[shd.getparent().tag.split('}')[1]] += 1
    print(f"表{ti}: {dict(lv)}")

print("\n=== D. 图[45] drawing XML ===")
print(x(kids[45].find(".//" + qn("w:drawing")), 2000))

print("\n=== D2. 6张真图 inline/anchor 与 extent vs a:ext ===")
EMU = 360000
for idx in (45, 75, 81, 120, 150, 169):
    for drw in kids[idx].iter(qn("w:drawing")):
        inline = drw.find(qn("wp:inline")); anch = drw.find(qn("wp:anchor"))
        kind = "inline" if inline is not None else ("anchor" if anch is not None else "?")
        host = inline if inline is not None else anch
        ext = host.find(qn("wp:extent")); aext = host.find(".//" + qn("a:ext"))
        w1, h1 = int(ext.get("cx"))/EMU, int(ext.get("cy"))/EMU
        w2 = int(aext.get("cx"))/EMU if aext is not None else -1
        h2 = int(aext.get("cy"))/EMU if aext is not None else -1
        print(f"[{idx}] {kind} wp:extent={w1:.1f}x{h1:.1f}mm a:ext={w2:.1f}x{h2:.1f}mm")

print("\n=== E. 挖空 _+ 分布 ===")
tot = 0
for i, el in enumerate(kids[:cut]):
    if el.tag == qn("w:tbl"):
        for p in el.iter(qn("w:p")):
            t = ptext(p)
            if "_" in t: print(f"  表内 [{i}] {t[:50]!r}")
        continue
    if el.tag != qn("w:p"): continue
    t = ptext(el)
    m = re.findall(r"_+", t)
    if m:
        tot += len(m)
        print(f"[{i:3}] {len(m)}处 {t[:56]!r}")
print("段内挖空总处数:", tot)

print("\n=== F. 包内 header/footer 部件 ===")
n = 0
for part in doc.part.package.parts:
    if "header" in str(part.partname) or "footer" in str(part.partname):
        print(" ", part.partname); n += 1
if not n: print("  （无 header/footer 部件）")

print("\n=== G. JieMingMao 段[4] XML ===")
print(x(kids[4], 900))

print("\n=== H. 题号段/条目段一览（run级shd数） ===")
pat_tk = re.compile(r"^\d[\d.]*-\d+．")
for i, el in enumerate(kids[:cut]):
    if el.tag != qn("w:p"): continue
    t = ptext(el).strip()
    if pat_tk.match(t):
        runshd = sum(1 for r in el.findall(qn("w:r"))
                     if r.find(qn("w:rPr")) is not None and r.find(qn("w:rPr")).find(qn("w:shd")) is not None)
        print(f"[{i:3}] runshd={runshd} {t[:38]!r}")

print("\n=== I. 全部 pBdr left sz=18 段（组标题） ===")
for i, el in enumerate(kids[:cut]):
    if el.tag != qn("w:p"): continue
    ppr = el.find(qn("w:pPr"))
    if ppr is None: continue
    b = ppr.find(qn("w:pBdr"))
    if b is not None:
        s = b.find(qn("w:left"))
        if s is not None and s.get(qn("w:sz")) == "18":
            print(f"[{i:3}] {ptext(el)[:44]!r}")

print("\n=== J. 段落显式 spacing/ind/jc 采样 ===")
cnt = Counter()
for el in kids[:cut]:
    if el.tag != qn("w:p"): continue
    ppr = el.find(qn("w:pPr"))
    if ppr is None: continue
    sp = ppr.find(qn("w:spacing"))
    key = (sp.get(qn("w:line")), sp.get(qn("w:lineRule")), sp.get(qn("w:before")), sp.get(qn("w:after"))) if sp is not None else None
    ind = ppr.find(qn("w:ind"))
    ikey = (ind.get(qn("w:left")), ind.get(qn("w:hanging")), ind.get(qn("w:firstLine"))) if ind is not None else None
    jc = ppr.find(qn("w:jc"))
    cnt[(key, ikey, jc.get(qn("w:val")) if jc is not None else None)] += 1
for k, v in cnt.most_common(12): print(f"  {v:4}  spacing={k[0]} ind={k[1]} jc={k[2]}")

print("\n=== K. run 显式 rFonts/sz 采样 ===")
cnt2 = Counter()
for el in kids[:cut]:
    if el.tag != qn("w:p"): continue
    for r in el.findall(qn("w:r")):
        rpr = r.find(qn("w:rPr"))
        if rpr is None: cnt2[None] += 1; continue
        f = rpr.find(qn("w:rFonts")); z = rpr.find(qn("w:sz"))
        cnt2[(f.get(qn("w:ascii")) if f is not None else None,
              f.get(qn("w:eastAsia")) if f is not None else None,
              z.get(qn("w:val")) if z is not None else None)] += 1
for k, v in cnt2.most_common(12): print(f"  {v:4}  fonts/sz={k}")

print("\n=== L. 题2 答案段[70] 与 知识点段[71] run 明细 ===")
for idx in (70, 71):
    print(f"--- [{idx}] ---")
    for r in kids[idx].findall(qn("w:r")):
        rpr = r.find(qn("w:rPr"))
        shd = rpr.find(qn("w:shd")) if rpr is not None else None
        z = rpr.find(qn("w:sz")) if rpr is not None else None
        txt = "".join(t.text or "" for t in r.findall(qn("w:t")))
        mt = "MATH" if r.find(qn("m:oMath")) is not None or r.tag == qn("m:r") else ""
        print(f"   shd={shd.get(qn('w:fill')) if shd is not None else '—'} sz={z.get(qn('w:val')) if z is not None else '—'} {mt} {txt[:30]!r}")
