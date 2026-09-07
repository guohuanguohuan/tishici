# -*- coding: utf-8 -*-
# v3诊断轮·我方导学件 main.pdf 实测脚本（只读，输出stdout）
import pymupdf, statistics, json

PDF = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v3\导学件\main.pdf"
doc = pymupdf.open(PDF)
print("pages:", doc.page_count, " mediabox:", doc[0].rect)
PT2MM = 25.4/72.0

def col_of(x, mid):
    return 0 if x < mid else 1

for pno in range(doc.page_count):
    page = doc[pno]
    W, H = page.rect.width, page.rect.height
    d = page.get_text("dict")
    mid = W/2
    sizes = {}
    spans_all = []
    for b in d["blocks"]:
        if b["type"] != 0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                if not s["text"].strip(): continue
                sz = round(s["size"],1)
                sizes[sz] = sizes.get(sz,0)+len(s["text"])
                spans_all.append((sz, s["bbox"], s["text"]))
    # 字号直方图（按字符数）
    print(f"\n=== page {pno+1} (W={W:.0f}pt H={H:.0f}pt) ===")
    top = sorted(sizes.items(), key=lambda kv:-kv[1])[:10]
    print(" 字号直方图(pt:chars):", top)
    # 正文行距：相邻同栏 span 基线差（取 size 9.5~12 的行）
    lines = []
    for b in d["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if not txt: continue
            szs = [s["size"] for s in l["spans"] if s["text"].strip()]
            if not szs: continue
            m = statistics.median(szs)
            lines.append((m, l["bbox"], txt))
    body = [L for L in lines if 9.0<=L[0]<=13.5]
    pitches = []
    for col in (0,1):
        cl = sorted([L for L in body if col_of((L[1][0]+L[1][2])/2, mid)==col], key=lambda L:L[1][1])
        for a,b2 in zip(cl, cl[1:]):
            dp = b2[1][1]-a[1][1]
            if 5 < dp < 30: pitches.append(dp)
    if pitches:
        pitches.sort()
        print(f" 正文行距 pitch: n={len(pitches)} 中位={statistics.median(pitches):.1f}pt ({statistics.median(pitches)*PT2MM:.2f}mm) p10-p90={pitches[int(len(pitches)*.1)]:.1f}~{pitches[int(len(pitches)*.9)]:.1f}")
    # 每栏内容纵向范围与底部空白
    for col in (0,1):
        cl = [L for L in lines if col_of((L[1][0]+L[1][2])/2, mid)==col]
        if not cl: 
            print(f" col{col}: 无文本"); continue
        y0 = min(L[1][1] for L in cl); y1 = max(L[1][3] for L in cl)
        n = len(cl)
        print(f" col{col}: 行数={n} y[{y0:.0f}~{y1:.0f}]pt 底部空白={(H-56-y1)*PT2MM:.0f}mm(页脚上缘≈H-56)")
    print(f" 全页文本行数={len(lines)}")

# 标题梯子 y 坐标（第1页）与花形行 drawings
print("\n=== 第1页 标题梯子（黑体大字行 bbox）===")
page = doc[0]
for b in page.get_text("dict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        txt = "".join(s["text"] for s in l["spans"]).strip()
        sz = max([s["size"] for s in l["spans"] if s["text"].strip()], default=0)
        if sz >= 13.5 and txt:
            print(f"  {sz:.1f}pt y={l['bbox'][1]:.1f}~{l['bbox'][3]:.1f} |{txt[:30]}|")
print("\n=== drawings 统计（花形框/底线/灰块/表格线）===")
for pno in range(doc.page_count):
    page = doc[pno]
    dr = page.get_drawings()
    rects = [x["rect"] for x in dr]
    fills = {}
    for x in dr:
        c = x.get("fill")
        if c:
            key = tuple(round(v,2) for v in c)
            fills[key] = fills.get(key,0)+1
    hlist = sorted([(r.width, r.height) for r in rects], key=lambda t:-t[1])[:3]
    print(f" p{pno+1}: drawings={len(dr)} fills={fills} 最高3块(w×h pt)={[(round(w),round(h)) for w,h in hlist]}")
doc.close()
