# -*- coding: utf-8 -*-
import re
from docx import Document
from docx.oxml.ns import qn

SRC = r"高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"
doc = Document(SRC)
body = doc.element.body
kids = list(body.iterchildren())
cut = 173

def ptext(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))

print("=== [0..9] 逐段详情 ===")
for i in range(10):
    el = kids[i]
    tag = el.tag.split('}')[1]
    if tag == "tbl":
        print(f"[{i}] TBL 首行文本:", " | ".join(ptext(r)[:30] for r in el.findall(qn("w:tr"))[:2]))
        continue
    sty = ""
    ppr = el.find(qn("w:pPr"))
    if ppr is not None:
        ps = ppr.find(qn("w:pStyle")); sty = ps.get(qn("w:val")) if ps is not None else ""
    t = ptext(el)
    print(f"[{i}] P sty={sty!r} text={t!r}")
    # run 级 shd
    for r in el.findall(qn("w:r")):
        rpr = r.find(qn("w:rPr"))
        if rpr is not None:
            shd = rpr.find(qn("w:shd"))
            if shd is not None:
                print(f"    run shd={shd.get(qn('w:fill'))} text={(''.join(x.text or '' for x in r.findall(qn('w:t'))))[:30]!r}")

print("\n=== 全文 run 级 shd fill 统计（截断前）===")
from collections import Counter
cnt = Counter(); samples = {}
for el in kids[:cut]:
    if el.tag != qn("w:p"): continue
    for r in el.findall(qn("w:r")):
        rpr = r.find(qn("w:rPr"))
        if rpr is None: continue
        shd = rpr.find(qn("w:shd"))
        if shd is not None:
            f = shd.get(qn("w:fill"))
            cnt[f] += 1
            if f not in samples: samples[f] = []
            if len(samples[f]) < 3:
                samples[f].append(("".join(x.text or "" for x in r.findall(qn("w:t"))))[:40])
for f, c in cnt.items():
    print(f"fill={f}: {c} runs; 样例: {samples[f]}")

print("\n=== 段落级 shd fill 统计（截断前）===")
cnt2 = Counter()
for el in kids[:cut]:
    if el.tag != qn("w:p"): continue
    ppr = el.find(qn("w:pPr"))
    if ppr is None: continue
    shd = ppr.find(qn("w:shd"))
    if shd is not None: cnt2[shd.get(qn("w:fill"))] += 1
print(dict(cnt2))

print("\n=== 表格内段落级/行级 shd ===")
for ti, el in enumerate([e for e in kids[:cut] if e.tag == qn("w:tbl")]):
    fills = Counter()
    for shd in el.iter(qn("w:shd")):
        fills[shd.get(qn("w:fill"))] += 1
    print(f"表{ti}: {dict(fills)}")

print("\n=== pBdr 统计（截断前段落）===")
pb = Counter(); pbx = []
for i, el in enumerate(kids[:cut]):
    if el.tag != qn("w:p"): continue
    ppr = el.find(qn("w:pPr"))
    if ppr is None: continue
    b = ppr.find(qn("w:pBdr"))
    if b is not None:
        parts = []
        for side in ("left","bottom","top","right"):
            s = b.find(qn("w:"+side))
            if s is not None: parts.append(f"{side}:sz={s.get(qn('w:sz'))},color={s.get(qn('w:color'))}")
        key = ";".join(parts); pb[key] += 1
        if len(pbx) < 6: pbx.append((i, key, ptext(el)[:30]))
for k, v in pb.items(): print(f"  {k}: {v} 段")
for x in pbx: print("   例:", x)

print("\n=== 图片 extent（截断前）===")
EMU_MM = 360000
for i, el in enumerate(kids[:cut]):
    for ext in el.iter(qn("wp:extent")):
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        print(f"[{i}] extent {cx/EMU_MM:.1f}mm x {cy/EMU_MM:.1f}mm")

print("\n=== 【答案】【知识点】段与不可见字符 ===")
for i, el in enumerate(kids[:cut]):
    if el.tag != qn("w:p"): continue
    t = ptext(el)
    if t.startswith("【"):
        codes = " ".join(f"{ord(c):04X}" for c in t[:8])
        print(f"[{i}] {t[:46]!r} 前8字符码: {codes}")
