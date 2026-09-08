# ④片探针4b：判断题序号span＋墨密像素测量（dict接口）
import pymupdf
io = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件\main.pdf"
d = pymupdf.open(io)
DPI=300; SC=DPI/72.0

print("===== G. 判断题/检测题/标签 span 细节 =====")
pg=d[0]
for b in pg.get_text("dict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        if 533<l["bbox"][1]<570 and l["bbox"][0]>300:
            for s in l["spans"]:
                print(f" p1 判断行 fs={s['size']:.2f} font={s['font'][:26]:26s} fl={s['flags']:2d} | {s['text'][:24]!r}")
pg7=d[6]
for b in pg7.get_text("dict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        if 66<l["bbox"][1]<92 and l["bbox"][0]<80:
            for s in l["spans"]:
                print(f" p7 检测1行 fs={s['size']:.2f} font={s['font'][:26]:26s} fl={s['flags']:2d} | {s['text'][:20]!r}")
n=0
for b in pg7.get_text("dict")["blocks"]:
    if n>=2: break
    if b["type"]!=0: continue
    for l in b["lines"]:
        t="".join(s["text"] for s in l["spans"])
        if "【答案】" in t or "【解析】" in t:
            for s in l["spans"]:
                if s["text"].startswith("【"):
                    print(f" p7 标签 fs={s['size']:.2f} font={s['font'][:26]:26s} fl={s['flags']:2d} | {s['text'][:8]!r}")
                    n+=1; break

print("\n===== H. 墨密测量（300dpi：墨占比v<128、均值灰、横笔画run中位） =====")
def ink_metrics(pno, rect, tag):
    pg=d[pno]
    pm=pg.get_pixmap(matrix=pymupdf.Matrix(SC,SC), clip=rect, colorspace=pymupdf.csGRAY)
    W,H,buf=pm.width,pm.height,pm.samples
    dark=0; tot=W*H; gsum=0; runs=[]
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
    print(f" {tag:30s} 墨占比={dark/tot:.3f} 均值灰={gsum/tot:6.1f} 横run中位={med}px")

targets=[]  # (page, finder(dict-mode span predicate), tag)
pg3=d[2]
# 检测题号 1
for b in pg7.get_text("dict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if s["text"].strip()=="1" and s["size"]>11 and l["bbox"][0]<60 and l["bbox"][1]<95:
                bb=s["bbox"]; targets.append((6,pymupdf.Rect(bb[0]-.5,bb[1]-.5,bb[2]+.5,bb[3]+.5),"检测题号'1' 11.4pt Times常规"))
# 标签
seen=set()
for b in pg7.get_text("dict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            key=s["text"][:4]
            if s["text"].startswith(("【答案】","【解析】")) and key not in seen and len(seen)<2:
                seen.add(key); bb=s["bbox"]
                targets.append((6,pymupdf.Rect(bb[0],bb[1],bb[2],bb[3]),f"{s['text'][:4]}标签 10.5pt 仿粗黑1.3"))
# 例1 p3 y202
for b in pg3.get_text("dict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        if 200<l["bbox"][1]<218 and l["bbox"][0]<80:
            for s in l["spans"]:
                bb=s["bbox"]
                if s["text"]=="例": targets.append((2,pymupdf.Rect(bb[0],bb[1],bb[2],bb[3]),"例1'例' 12pt 仿粗黑2.3"))
                if s["text"]=="1": targets.append((2,pymupdf.Rect(bb[0]-.5,bb[1]-.5,bb[2]+.5,bb[3]+.5),"例1'1' 12pt Times常规"))
        if 455<l["bbox"][1]<475 and l["bbox"][0]<80:
            for s in l["spans"]:
                bb=s["bbox"]
                if s["text"]=="变式": targets.append((2,pymupdf.Rect(bb[0],bb[1],bb[2],bb[3]),"变式1'变式' 12pt 仿粗黑1.3"))
                if s["text"]=="1": targets.append((2,pymupdf.Rect(bb[0]-.5,bb[1]-.5,bb[2]+.5,bb[3]+.5),"变式1'1' 12pt Times常规"))
# 条目号 1. p1
for b in d[0].get_text("dict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        if 300<l["bbox"][1]<335 and l["bbox"][0]<60:
            for s in l["spans"]:
                if s["text"].strip()=="1.":
                    bb=s["bbox"]; targets.append((0,pymupdf.Rect(bb[0]-.5,bb[1]-.5,bb[2]+.5,bb[3]+.5),"条目号'1.' 10.5pt Times常规"))
# 判断题干首二字 p1
for b in d[0].get_text("dict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        if 535<l["bbox"][1]<550 and l["bbox"][0]>300:
            for s in l["spans"]:
                if "两个空间" in s["text"]:
                    bb=s["bbox"]; targets.append((0,pymupdf.Rect(bb[0],bb[1],bb[0]+24,bb[3]),"判断题干首2字 10.5pt 宋常规"))
# 正文字样 p3（分析行）
for b in pg3.get_text("dict")["blocks"]:
    if b["type"]!=0: continue
    for l in b["lines"]:
        for s in l["spans"]:
            if s["text"].startswith("【分析】"):
                bb=s["bbox"]
                if bb[0]<80:
                    targets.append((2,pymupdf.Rect(bb[0],bb[1],bb[0]+36,bb[3]),"【分析】标签 10.5pt 仿粗黑1.3"))
                break
for pno,rect,tag in targets:
    ink_metrics(pno,rect,tag)
d.close(); print("DONE")
