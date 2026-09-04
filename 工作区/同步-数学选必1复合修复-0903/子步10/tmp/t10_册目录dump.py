# -*- coding: utf-8 -*-
"""册目录页 python-docx 只读重 dump（禁抄子步8在案dump）：全段落 idx+text+缩进，
锚定六个件级行（段idx3/4/5/9/10/11），另自动检索「·本」行交叉定位。"""
import json
from docx import Document

PATH = r"C:\提示词\高中数学\高中数学同步\人教B版选必1·册目录页.docx"
OUT = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步10\tmp\t10_册目录dump.json"

doc = Document(PATH)
paras = []
for i, p in enumerate(doc.paragraphs):
    ind = p.paragraph_format.left_indent
    paras.append({"idx": i, "text": p.text,
                  "indent缇": round(ind.twips) if ind is not None else None})
anchors = {i: paras[i] for i in (3, 4, 5, 9, 10, 11) if i < len(paras)}
ben_rows = [{"idx": q["idx"], "text": q["text"]} for q in paras if "·本" in q["text"]]
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"段总数": len(paras), "锚定件级行": anchors,
               "含本字行": ben_rows, "全段落": paras}, f, ensure_ascii=False, indent=1)
print(f"段总数={len(paras)}")
print("— 锚定六行 —")
for i in (3, 4, 5, 9, 10, 11):
    print(f"idx{i}: {anchors.get(i,{}).get('text','<缺失>')}")
print("— 含「·本」行 —")
for r in ben_rows:
    print(f"idx{r['idx']}: {r['text']}")
