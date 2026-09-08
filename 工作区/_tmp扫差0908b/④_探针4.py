# ④片探针4：p4探五例1区域字符高分布、判断题序号span、墨密像素测量
import pymupdf, re
io = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件\main.pdf"
d = pymupdf.open(io)
PT2MM=25.4/72

# ---- F. p4 y188-500 右栏 全字符按高度分组（找数学定界符实际高度） ----
print("===== F. p4 右栏(y150-560) 数学字符高分布 =====")
pg=d[3]; td=pg.get_text("rawdict")
tall={}
for b in td["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if "Times" in s["font"] or "CM" in s["font"] or s["font"].startswith("L"):
                for c in s["chars"]:
                    bb=c["bbox"]
                    if bb[1]<150 or bb[1]>560: continue
                    if bb[0]<300: continue
                    h=bb[3]-bb[1]
                    key=round(h,1)
                    tall.setdefault(key,[]).append((c["c"],round(bb[0]),round(bb[1]),s["font"][:20],round(s["size"],1)))
for h in sorted(tall, reverse=True)[:14]:
    vs=tall[h]
    from collections import Counter
    cc=Counter(v[0] for v in vs)
    print(f" h={h:5.1f}pt n={len(vs):3d} chars={dict(cc.most_common(6))} 例={vs[:3]}")

# ---- G. 判断题序号 span（p1 y537-549 行内全部 span） ----
print("\n===== G. p1 判断题行 y535-570 全 span =====")
for b in td["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        if 530<l["bbox"][1]<572 and l["bbox"][0]>300:
            for s in l["spans"]:
                print(f" fs={s['size']:.2f} font={s['font'][:26]:26s} fl={s['flags']:2d} | {s['text']!r}")
print("----- p7 检测题1 行 y68-90 左栏 spans -----")
pg7=d[6]; td7=pg7.get_text("rawdict")
for b in td7["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        if 66<l["bbox"][1]<92:
            for s in l["spans"]:
                print(f" fs={s['size']:.2f} font={s['font'][:26]:26s} fl={s['flags']:2d} | {s['text']!r}")
print("----- p7 【答案】行 y? 搜索 -----")
for b in td7["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        t="".join(s["text"] for s in l["spans"])
        if "【答案】" in t or "【解析】" in t:
            for s in l["spans"]:
                if s["text"].startswith("【"):
                    print(f" y={l['bbox'][1]:.0f} fs={s['size']:.2f} font={s['font'][:26]:26s} fl={s['flags']:2d} | {s['text'][:12]!r}")
                    break
            break

# ---- H. 墨密像素测量（300dpi 裁字符盒：墨占比<128、均值、横笔画中位） ----
print("\n===== H. 墨密测量（300dpi） =====")
DPI=300; SC=DPI/72.0
def ink_metrics(page, rect, tag):
    pg=d[page]
    pm=pg.get_pixmap(matrix=pymupdf.Matrix(SC,SC), clip=rect, colorspace=pymupdf.csGRAY)
    W,H,buf=pm.width,pm.height,pm.samples
    dark=0; tot=W*H; gsum=0
    runs=[]
    for y in range(H):
        r0=y*W; run=0
        for x in range(W):
            v=buf[r0+x]; gsum+=v
            if v<128: dark+=1; run+=1
            else:
                if run: runs.append(run); run=0
        if run: runs.append(run)
    runs.sort()
    med=runs[len(runs)//2] if runs else 0
    print(f" {tag:22s} bbox=({rect.x0:.0f},{rect.y0:.0f},{rect.x1:.0f},{rect.y1:.0f}) 墨占比={dark/tot:.3f} 均值灰={gsum/tot:.1f} 横run中位={med}px")

# 检测题号「1」 p7 y71-84 x42.5-50（数字1 span bbox精确取）
pg7=d[6]
for b in pg7.get_text("rawdict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            for c in s["chars"]:
                if c["c"]=="1" and 66<l["bbox"][1]<95 and l["bbox"][0]<60:
                    bb=c["bbox"]
                    ink_metrics(6, pymupdf.Rect(bb[0]-0.5,bb[1]-0.5,bb[2]+0.5,bb[3]+0.5), "检测题号'1'(11.4pt Times)")
# 【答案】标签 p7
for b in pg7.get_text("rawdict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if s["text"].startswith("【答案】"):
                bb=s["bbox"]
                ink_metrics(6, pymupdf.Rect(bb[0],bb[1],bb[2],bb[3]), "【答案】标签(10.5pt仿粗黑)")
                break
        else: continue
        break
# 【解析】标签 p7
done=False
for b in pg7.get_text("rawdict")["blocks"]:
    if done: break
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if s["text"].startswith("【解析】"):
                bb=s["bbox"]
                ink_metrics(6, pymupdf.Rect(bb[0],bb[1],bb[2],bb[3]), "【解析】标签(10.5pt仿粗黑)")
                done=True; break
        if done: break
# 例1 p3 例字＋数字
pg3=d[2]
for b in pg3.get_text("rawdict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if s["text"]=="例" and s["size"]>11.5 and l["bbox"][1]<300:
                bb=s["bbox"]
                ink_metrics(2, pymupdf.Rect(bb[0],bb[1],bb[2],bb[3]), "例1'例'字(12pt仿粗黑)")
# 例1 数字
for b in pg3.get_text("rawdict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if s["text"]=="1" and s["size"]>11.5 and l["bbox"][1]<300:
                bb=s["bbox"]; bb=pymupdf.Rect(bb[0]-0.5,bb[1]-0.5,bb[2]+0.5,bb[3]+0.5)
                ink_metrics(2, bb, "例1'1'字(12pt Times常规)")
# 变式1 p3
for b in pg3.get_text("rawdict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if s["text"]=="变式" and s["size"]>11.5 and 440<l["bbox"][1]<480:
                bb=s["bbox"]
                ink_metrics(2, pymupdf.Rect(bb[0],bb[1],bb[2],bb[3]), "变式1'变式'(12pt仿粗1.3)")
# 判断题（1） p1
pg1=d[0]
for b in pg1.get_text("rawdict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if "两个空间向量的模相等" in s["text"]:
                bb=s["bbox"]
                ink_metrics(0, pymupdf.Rect(bb[0],bb[1],bb[0]+30,bb[3]), "判断题干首字(10.5pt宋)")
                break
# 条目号「1.」 p1 知识点一
for b in pg1.get_text("rawdict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if s["text"].strip()=="1." and l["bbox"][1]>300 and l["bbox"][1]<330:
                bb=s["bbox"]; bb=pymupdf.Rect(bb[0]-0.5,bb[1]-0.5,bb[2]+0.5,bb[3]+0.5)
                ink_metrics(0, bb, "条目号'1.'(10.5pt Times?)")
d.close(); print("DONE")
