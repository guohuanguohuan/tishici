# -*- coding: utf-8 -*-
"""探查章首、节名锚格式、1.1.1 范围内的表/图分布"""
from docx import Document
from docx.oxml.ns import qn

SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"
doc = Document(SRC)

def desc_run(r):
    rPr = r._element.find(qn('w:rPr'))
    vanish = sz = fonts = color = None
    if rPr is not None:
        v = rPr.find(qn('w:vanish'))
        vanish = v is not None and v.get(qn('w:val')) != '0'
        s = rPr.find(qn('w:sz'))
        sz = s.get(qn('w:val')) if s is not None else None
        f = rPr.find(qn('w:rFonts'))
        fonts = (f.get(qn('w:ascii')), f.get(qn('w:eastAsia'))) if f is not None else None
        c = rPr.find(qn('w:color'))
        color = c.get(qn('w:val')) if c is not None else None
    return f"vanish={vanish} sz={sz} fonts={fonts} color={color}"

print("--- 前 8 段 ---")
for i, p in enumerate(doc.paragraphs[:8]):
    print(f"#{i} [{p.style.style_id}] {p.text[:50]!r}")
    for r in p.runs[:2]:
        print("   run:", desc_run(r))

print("\n--- 节名锚 para#165 ---")
p = doc.paragraphs[165]
print(repr(p.text), "[style", p.style.style_id, "]")
for r in p.runs[:2]:
    print("   run:", desc_run(r))

# 1.1.1 范围：从 para#4 到 para#166 之间统计表与图（按 body 元素顺序）
body = doc.element.body
W = qn('w:p'), qn('w:tbl')
pels = [p._element for p in doc.paragraphs]
cut_el = pels[167]
idx_map = {id(el): i for i, el in enumerate(pels)}
from collections import Counter
tbl_in = 0
drawing_in = 0
for el in body.iter():
    pass
# 简化：遍历 body 直接子元素，在 cut 之前的
seen = 0
for el in body:
    if el is cut_el:
        break
    if el.tag == qn('w:tbl'):
        tbl_in += 1
    if el.tag == qn('w:p'):
        for d in el.iter(qn('w:drawing')):
            drawing_in += 1
        seen += 1
print(f"\n截断点之前: 段落 {seen} 个, 表格 {tbl_in} 个, drawing {drawing_in} 个")

# 图片 blip 统计（截断前）
blips = 0
for el in body:
    if el is cut_el:
        break
    for b in el.iter(qn('a:blip')):
        blips += 1
print("blip 数:", blips)

# 段落总数中截断点位置
print("总段数:", len(doc.paragraphs))
