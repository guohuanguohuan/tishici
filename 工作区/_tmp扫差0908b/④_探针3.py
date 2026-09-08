# ④片探针3：像素级表线-文字交叠、超栏行、行内间隙带、定界符全dump、题号span补采
import pymupdf, re
io = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件\main.pdf"
d = pymupdf.open(io)
PT2MM = 25.4/72
DPI = 300; SC = DPI/72.0

# ---- A2. 像素级：每条长表线横带内是否有近黑文字墨 ----
print("===== A2. 表线像素检验（300dpi；规则灰122≈val120-180，文字黑<80） =====")
for p in range(d.page_count):
    pg=d[p]
    segs=[]
    for dr in pg.get_drawings():
        for it in dr["items"]:
            if it[0]=="l":
                p1,p2=it[1],it[2]
                if abs(p1.y-p2.y)<0.3 and abs(p1.x-p2.x)>=200: segs.append((min(p1.x,p2.x),max(p1.x,p2.x),p1.y))
            elif it[0]=="re":
                r=it[1]
                if r.height<1.2 and r.width>=200: segs.append((r.x0,r.x1,(r.y0+r.y1)/2))
    if not segs: continue
    pm = pg.get_pixmap(matrix=pymupdf.Matrix(SC,SC), colorspace=pymupdf.csGRAY)
    W,H,buf = pm.width,pm.height,pm.samples
    print(f"\n-- p{p+1}")
    for x0,x1,y in segs:
        ytp=int(round((y-0.8)*SC)); ybt=int(round((y+0.8)*SC))+1
        xtp=int(round(x0*SC)); xbt=int(round(x1*SC))
        dark=0; xs=[]
        for yy in range(max(0,ytp),min(H,ybt)):
            row0=yy*W
            for xx in range(xtp,xbt):
                v=buf[row0+xx]
                if v<80: dark+=1; xs.append(xx)
        if dark>0:
            xx0=min(xs)/SC; xx1=max(xs)/SC
            print(f"  rule y={y:.1f} x={x0:.0f}-{x1:.0f}: 带内近黑墨 {dark}px (x {xx0:.1f}-{xx1:.1f}) !!")

# ---- B2. 超栏行（墨迹 x1 超栏缘 >2pt）----
print("\n===== B2. 超栏行清单（行 bbox x1 超本栏右缘≥2pt） =====")
COLS = {1:[(42.5,287.0),(308.3,552.8)], 2:[(42.5,287.0),(308.3,552.8)]}
for p in range(d.page_count):
    pg=d[p]; td=pg.get_text("dict")
    for b in td["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            t="".join(s["text"] for s in l["spans"])
            if not t.strip(): continue
            x0,y0,x1,y1=l["bbox"]
            for cx0,cx1 in [(42.5,287.0),(308.3,552.8)]:
                if x0>=cx0-6 and x0<cx0+40:
                    if x1>cx1+2:
                        print(f"[p{p+1}] 栏缘{cx1:.0f} x1={x1:.1f} 超{x1-cx1:.1f}pt({(x1-cx1)*PT2MM:.1f}mm) y={y0:.0f} | {t[:44]}")
                    break

# ---- C2. 行内间隙带（累计空隙≥1.0em 的连续带，>2.5em 才报）----
print("\n===== C2. 行内大间隙（连续空隙带 ≥2.5em） =====")
for p in range(d.page_count):
    pg=d[p]; td=pg.get_text("rawdict")
    for b in td["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            chars=[]
            for s in l["spans"]:
                for c in s["chars"]:
                    if c["c"].strip(): chars.append((c["bbox"],c["c"]))
            chars.sort(key=lambda cc:cc[0][0])
            if len(chars)<2: continue
            fsize=max(s["size"] for s in l["spans"])
            # 间隙带：连续小间隙累积
            run=0; start=None; prev=None; txt="".join(cc[1] for cc in chars)
            for i in range(len(chars)-1):
                (b1,_),(b2,_)=chars[i],chars[i+1]
                gap=b2[0]-b1[2]
                if gap>1.5:
                    if start is None: start=i; run=0
                    run+=gap
                    prev=i
                else:
                    if start is not None and run>=fsize*2.5:
                        ctx=txt[max(0,start-5):start+1]+"▣"+txt[start+1:prev+2]+"▣"+txt[prev+2:prev+8]
                        print(f"[p{p+1}] y={l['bbox'][1]:.0f} fs={fsize:.1f} 带隙={run:.1f}pt({run/fsize:.1f}em) …{ctx}…")
                    start=None; run=0
            if start is not None and run>=fsize*2.5:
                ctx=txt[max(0,start-5):start+1]+"▣"+txt[start+1:prev+2]+"▣"+txt[prev+2:prev+8]
                print(f"[p{p+1}] y={l['bbox'][1]:.0f} fs={fsize:.1f} 带隙={run:.1f}pt({run/fsize:.1f}em) …{ctx}…")

# ---- D2. 全件字符高 >11.8pt dump（定界符/大字符）----
print("\n===== D2. 字符高>11.8pt 全清单（定界符候补） =====")
for p in range(d.page_count):
    pg=d[p]; td=pg.get_text("rawdict")
    for b in td["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                for c in s["chars"]:
                    bb=c["bbox"]; h=bb[3]-bb[1]
                    if h>11.8 and c["c"].strip():
                        print(f"[p{p+1}] y={bb[1]:5.1f}-{bb[3]:5.1f} h={h:5.2f}pt({h*PT2MM:4.2f}mm) ch={c['c']!r:6s} fs={s['size']:.1f} | ctx {''.join(cc['c'] for cc in s['chars'])[:24]}")

# ---- E2. 题号/例变标签 span 补采 ----
print("\n===== E2. 题号与例变标签 span（含 12pt 层与检测题号） =====")
for p in range(d.page_count):
    pg=d[p]; td=pg.get_text("dict")
    for b in td["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                t=s["text"].strip()
                if not t: continue
                if s["size"]>10.8 and len(t)<=8:
                    print(f"[p{p+1}] fs={s['size']:5.2f} font={s['font'][:30]:30s} fl={s['flags']} y={l['bbox'][1]:.0f} | {t!r}")
                elif re.match(r"^（\d）$",t):
                    print(f"[p{p+1}] 判断序号 fs={s['size']:5.2f} font={s['font'][:30]:30s} fl={s['flags']} y={l['bbox'][1]:.0f} | {t!r}")
                elif re.match(r"^\d．",t) or t in("例1","变式1"):
                    print(f"[p{p+1}] fs={s['size']:5.2f} font={s['font'][:30]:30s} fl={s['flags']} y={l['bbox'][1]:.0f} | {t!r}")
d.close(); print("\nDONE")
