# -*- coding: utf-8 -*-
# v3诊断轮·细化测量：块间距/行距直方/版心占用/底部空白/表格行高（只读）
import pymupdf, statistics
from collections import Counter

PDF = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v3\导学件\main.pdf"
PT2MM = 25.4/72.0
doc = pymupdf.open(PDF)

def is_cjk(ch):
    return '\u4e00' <= ch <= '\u9fff'

for pno in range(doc.page_count):
    page = doc[pno]
    H = page.rect.height
    d = page.get_text("dict")
    lines = []
    for b in d["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if not txt: continue
            szs=[s["size"] for s in l["spans"] if s["text"].strip()]
            lines.append((statistics.median(szs), l["bbox"], txt))
    body = [L for L in lines if 45 < L[1][1] < 800]  # 去页眉页脚
    mid = page.rect.width/2
    print(f"\n=== p{pno+1} 正文(去眉脚) ===")
    # 行距直方（同栏相邻、均为纯中文10.5pt行、x重叠>50%）
    pitches=Counter()
    for col in (0,1):
        cl=sorted([L for L in body if 9.5<=L[0]<=11.0 and ((L[1][0]+L[1][2])/2<mid)==(col==0)], key=lambda L:L[1][3])
        cjk=[L for L in cl if sum(is_cjk(c) for c in L[2])>=4]
        for a,b2 in zip(cjk,cjk[1:]):
            dp=b2[1][1]-a[1][1]
            if 4<dp<40:
                pitches[round(dp)]+=1
    common=sorted(pitches.items(), key=lambda kv:-kv[1])[:6]
    print(" 中文正文行距直方(pt:次数):", common, " 最频mm=", [f"{k*PT2MM:.1f}" for k,_ in common])
    for col in (0,1):
        cl=[L for L in body if ((L[1][0]+L[1][2])/2<mid)==(col==0)]
        if not cl: print(f" col{col}: 空"); continue
        y1=max(L[1][3] for L in cl)
        # 版心底 = 842-15mm边距(42.5pt) - 页脚区(fancy footskip 6mm+块高7.8mm→页脚顶约 y=780)
        ybot = 780.0
        print(f" col{col}: 行数={len(cl)} 正文末y={y1:.0f}pt={y1*PT2MM:.0f}mm 底部空白≈{(ybot-y1)*PT2MM:.0f}mm")
    # 大间距（块间距）：相邻行间隔>2×18pt
    for col in (0,1):
        cl=sorted([L for L in body if ((L[1][0]+L[1][2])/2<mid)==(col==0)], key=lambda L:(L[1][1]))
        gaps=[]
        for a,b2 in zip(cl,cl[1:]):
            g=b2[1][1]-a[1][3]
            if g>7: gaps.append((round(g*PT2MM), a[2][:14], b2[2][:14]))
        print(f" col{col} 块间大空隙(mm: 上行→下行):", gaps[:14])
doc.close()
