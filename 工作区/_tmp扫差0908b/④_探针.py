# ④片只读取证探针：v4.3 main.pdf 行层/字符层/绘图层实测（不改任何成品）
import pymupdf, re, sys
io = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件\main.pdf"
d = pymupdf.open(io)
PT2MM = 25.4/72

def dump_lines(page, pat=None, tag=""):
    """print lines (y0,x0,text) optionally filtered"""
    td = page.get_text("dict")
    out=[]
    for b in td["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            t="".join(s["text"] for s in l["spans"])
            if pat and not re.search(pat,t): continue
            x0,y0,x1,y1=l["bbox"]
            out.append((round(y0,1),round(x0,1),round(x1,1),round(y1,1),t))
    out.sort()
    for y0,x0,x1,y1,t in out:
        print(f"{tag} y={y0:7.1f}-{y1:7.1f} x={x0:6.1f}-{x1:6.1f} ({round((x1-x0)*PT2MM,1)}mm) | {t[:60]}")
    return out

def sec(p, title):
    print(f"\n===== p{p} {title} =====")

# ---------- b: 判断题全部 6 条 ----------
for p in range(d.page_count):
    pg=d[p]
    hits = dump_lines(pg, r"模相等，则|一定是共线|平行\\传递|唯一实数|共面．|锐角|^（×）$|^（√）$|^（\s*×\s*）$|^（\s*√\s*）$|判断正误", f"[p{p+1}]")

# ---------- f: 探究点标题行及其下一行 ----------
print("\n===== 探究点标题行（含折行检查） =====")
for p in range(d.page_count):
    pg=d[p]; td=pg.get_text("dict"); rows=[]
    for b in td["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            t="".join(s["text"] for s in l["spans"])
            x0,y0,x1,y1=l["bbox"]
            rows.append((y0,x0,x1,y1,t))
    rows.sort()
    for i,(y0,x0,x1,y1,t) in enumerate(rows):
        if re.search(r"探究点[一二三四五六七八九]",t):
            print(f"[p{p+1}] TITLE y={y0:.1f}-{y1:.1f} x={x0:.1f}-{x1:.1f} w={(x1-x0)*PT2MM:.1f}mm | {t}")
            for j in range(i+1,min(i+3,len(rows))):
                y0b,x0b,x1b,y1b,tb=rows[j]
                print(f"      next y={y0b:.1f} x={x0b:.1f} | {tb[:50]}")

# ---------- a: 表格线 vs 正文 ink 交叠 ----------
print("\n===== 表格线带与文字带交叠检测 =====")
for p in range(d.page_count):
    pg=d[p]
    # horizontal segments from drawings
    hseg=[]
    for dr in pg.get_drawings():
        for it in dr["items"]:
            if it[0]=="l":
                p1,p2=it[1],it[2]
                if abs(p1.y-p2.y)<0.3 and abs(p1.x-p2.x)>5:
                    hseg.append((min(p1.x,p2.x),max(p1.x,p2.x),p1.y,dr.get("width",0)))
            elif it[0]=="re":
                r=it[1]
                if r.height<1.2 and r.width>5:
                    hseg.append((r.x0,r.x1,(r.y0+r.y1)/2,r.width))
    if not hseg: continue
    # cluster into table bands by y
    hseg.sort(key=lambda s:s[2])
    bands=[]
    for x0,x1,y,w in hseg:
        if bands and y-bands[-1][1]<14:
            b=bands[-1]; b[1]=max(b[1],y); b[2]=min(b[2],x0); b[3]=max(b[3],x1); b[4]+=1
        else:
            bands.append([y,y,x0,x1,1])
    td=pg.get_text("dict"); lines=[]
    for b in td["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            t="".join(s["text"] for s in l["spans"]).strip()
            if not t: continue
            lines.append((l["bbox"],t))
    for b in bands:
        if b[4]<3: continue  # 需≥3条横线才算表
        print(f"[p{p+1}] TABLE band y={b[0]:.1f}-{b[1]:.1f} x={b[2]:.1f}-{b[3]:.1f} nh={b[4]}")
        # text lines overlapping band vertically
        for (bbx,t) in lines:
            ix0=max(bbx[0],b[2]); ix1=min(bbx[2],b[3])
            if ix1-ix0<2: continue
            ov_top = max(0, min(bbx[3],b[1]+1.2)-max(bbx[1],b[0]-1.2))
            if ov_top>0:
                print(f"    OVERLAP {ov_top:.1f}pt y_text={bbx[1]:.1f}-{bbx[3]:.1f} x={bbx[0]:.1f} | {t[:40]}")
            # near miss above/below
            gap_up = b[0]-bbx[3]; gap_dn = bbx[1]-b[1]
            if 0<gap_up<4 or 0<gap_dn<4:
                side = "ABOVE" if gap_up>0 else "BELOW"
                print(f"    near-{side} gap={min(abs(gap_up),abs(gap_dn)):.1f}pt | {t[:40]}")

d.close()
print("\nDONE")
