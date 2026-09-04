# -*- coding: utf-8 -*-
"""T1 python-docx 只读采集：十件 pgNumType@start＋分节数＋各节start清单（一律读原件路径，不走COM）。
start实测值＝首个含 pgNumType 的 sectPr 之 @start；断言首节之外零 start 残留。"""
import json, os
from docx import Document

BASE = r"C:\提示词\高中数学\高中数学同步"
OUT = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步10\tmp\t10_start采集.json"
NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

FILES = [  # 短名, 实名, 基线分节数, 基线start
    ("X1", "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx", 2, 1),
    ("I1", "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx", 2, 1),
    ("B", "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx", 2, 1),
    ("C", "人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx", 2, 62),
    ("X2", "人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx", 2, 1),
    ("I2", "人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx", 2, 1),
    ("E", "人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx", 2, 1),
    ("F", "人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx", 1, 56),
    ("G", "人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx", 1, 112),
    ("H", "人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx", 2, 156),
]

rows = []
red = False
for key, name, exp_sec, exp_start in FILES:
    doc = Document(os.path.join(BASE, name))
    sects = []
    for sp in doc.element.body.iter(NS + "sectPr"):
        pg = sp.find(NS + "pgNumType")
        st = pg.get(NS + "start") if pg is not None else None
        sects.append(int(st) if st is not None else None)
    first_pg_idx = next((i for i, sp in enumerate(doc.element.body.iter(NS + "sectPr"))
                         if sp.find(NS + "pgNumType") is not None), None)
    start_val = sects[first_pg_idx] if first_pg_idx is not None else None
    residual = sum(1 for i, s in enumerate(sects)
                   if s is not None and i != first_pg_idx)
    ok = (len(sects) == exp_sec and start_val == exp_start
          and first_pg_idx == 0 and residual == 0)
    red = red or not ok
    rows.append({"短名": key, "件": name, "分节数": len(sects),
                 "各节start清单": sects, "首节start": start_val,
                 "首个pgNumType节序": first_pg_idx, "首节外start残留数": residual,
                 "基线分节数": exp_sec, "基线start": exp_start, "符合基线": ok})

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)
for r in rows:
    print(f"{r['短名']:>3} 节={r['分节数']} 各节start={r['各节start清单']} 首节start={r['首节start']} 残留={r['首节外start残留数']} 基线符合={r['符合基线']}")
print("RED" if red else "ALL-OK")
