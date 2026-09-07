# -*- coding: utf-8 -*-
# v3诊断轮·我方结构块 y 坐标普查（只读）
import pymupdf

PDF = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v3\导学件\main.pdf"
M2 = 25.4/72.0
doc = pymupdf.open(PDF)
MARKS = ["【学习目标】","课前预习","◆ 知识点","【诊断分析】","课中探究","◆ 探究点","例1","例2","例3","变式","【素养小结】","【答案】","课堂检测","【分析】","【详解】"]
for pno in range(doc.page_count):
    page = doc[pno]
    print(f"\n=== p{pno+1} ===")
    rows=[]
    for b in page.get_text("dict")["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            txt="".join(s["text"] for s in l["spans"]).strip()
            if not txt: continue
            for m in MARKS:
                if txt.replace(" ","").startswith(m.replace(" ","")):
                    col = 0 if (l["bbox"][0]+l["bbox"][2])/2 < page.rect.width/2 else 1
                    rows.append((col, l["bbox"][1]*M2, l["bbox"][3]*M2, txt[:22]))
                    break
    for col,y0,y1,t in rows:
        print(f" col{col} y{y0:6.1f}~{y1:6.1f}mm |{t}|")
doc.close()
