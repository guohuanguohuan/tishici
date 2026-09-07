# -*- coding: utf-8 -*-
import re
from docx import Document
from docx.oxml.ns import qn

SRC = r"高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"
doc = Document(SRC)
body = doc.element.body

def ptext(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))

def pstyle(p):
    ppr = p.find(qn("w:pPr"))
    if ppr is None: return ""
    ps = ppr.find(qn("w:pStyle"))
    return ps.get(qn("w:val")) if ps is not None else ""

kids = list(body.iterchildren())
print("body 子元素总数:", len(kids))
tags = {}
for el in kids:
    tag = el.tag.split('}')[1]
    tags[tag] = tags.get(tag, 0) + 1
print("标签分布:", tags)

# 找 1.1.2 标题3 段的索引
cut = None
for i, el in enumerate(kids):
    if el.tag == qn("w:p") and pstyle(el) in ("标题3", "Heading3", "3"):
        t = ptext(el).strip()
        if t.startswith("1.1.2"):
            cut = i
            print(f"\n截断点 body[{i}] = 标题3: {t}")
            break
print("截断索引 cut =", cut)

# 打印截断前的所有元素概览（标题类全打，其他抽样）
print("\n--- 截断前元素清单（前80 + 题号段全列）---")
n_shown = 0
for i, el in enumerate(kids[:cut]):
    tag = el.tag.split('}')[1]
    if tag == "tbl":
        # 表格行列数
        rows = el.findall(qn("w:tr"))
        print(f"[{i:4}] TBL rows={len(rows)}")
        n_shown += 1
        continue
    if tag != "p":
        print(f"[{i:4}] {tag}")
        continue
    sty = pstyle(el); t = ptext(el)
    imgs = len(el.findall(".//" + qn("wp:inline"))) + len(el.findall(".//" + qn("wp:anchor")))
    math = len(el.findall(".//" + qn("m:oMath")))
    shd = el.find(qn("w:pPr") + "/" + qn("w:shd")) if el.find(qn("w:pPr")) is not None else None
    shdv = shd.get(qn("w:fill")) if shd is not None else ""
    flag = ""
    if re.match(r"^\d[\d.]*-\d+．", t.strip()): flag = "◆题"
    if sty in ("标题1","标题2","标题3","Heading1","Heading2","Heading3","1","2","3") or flag or imgs or math or shdv or not t.strip():
        print(f"[{i:4}] P sty={sty:<8} img={imgs} math={math} shd={shdv:<7} | {t[:60]}")
        n_shown += 1
print("...(展示行数", n_shown, ")")

# 末尾 sectPr
print("\n--- body 尾部元素 ---")
for el in kids[-3:]:
    print(el.tag)
