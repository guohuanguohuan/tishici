# ④片精化探针2：表规则长线精确、判断题全行序、行内间隙、定界符高度、字体三数
import pymupdf, re
io = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件\main.pdf"
d = pymupdf.open(io)
PT2MM = 25.4/72

def lines_of(pg):
    td = pg.get_text("dict"); rows=[]
    for b in td["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            t="".join(s["text"] for s in l["spans"])
            if t.strip():
                rows.append({"bbox":l["bbox"],"text":t})
    rows.sort(key=lambda r:(round(r["bbox"][1]),r["bbox"][0]))
    return rows

def table_rules(pg, minw=200):
    segs=[]
    for dr in pg.get_drawings():
        for it in dr["items"]:
            if it[0]=="l":
                p1,p2=it[1],it[2]
                if abs(p1.y-p2.y)<0.3 and abs(p1.x-p2.x)>=minw:
                    segs.append((min(p1.x,p2.x),max(p1.x,p2.x),p1.y,dr.get("width",0)))
            elif it[0]=="re":
                r=it[1]
                if r.height<1.2 and r.width>=minw:
                    segs.append((r.x0,r.x1,(r.y0+r.y1)/2,r.width))
    segs.sort(key=lambda s:(s[2],s[0]))
    return segs

print("===== A. 长横规则(≥200pt) 全清单＋上下邻文字 gap =====")
for p in range(d.page_count):
    pg=d[p]; segs=table_rules(pg); rows=lines_of(pg)
    if not segs: continue
    print(f"\n-- p{p+1}: {len(segs)} 条长横线")
    for x0,x1,y,w in segs:
        ups=[r for r in rows if r["bbox"][2]>x0-5 and r["bbox"][0]<x1+5 and r["bbox"][3]<=y+1]
        dns=[r for r in rows if r["bbox"][2]>x0-5 and r["bbox"][0]<x1+5 and r["bbox"][1]>=y-1]
        ups.sort(key=lambda r:-r["bbox"][3]); dns.sort(key=lambda r:r["bbox"][1])
        gu = y-ups[0]["bbox"][3] if ups and y-ups[0]["bbox"][3]>=0 else (y-ups[0]["bbox"][3] if ups else 99)
        gd = dns[0]["bbox"][1]-y if dns and dns[0]["bbox"][1]-y>=0 else 99
        su = f"up gap={gu:5.1f}pt({gu*PT2MM:4.1f}mm) «{ups[0]['text'][:26]}»" if ups and gu<40 else (f"up OVERLAP {-gu:5.1f}pt «{ups[0]['text'][:26]}»" if ups else "up -")
        sd = f"dn gap={gd:5.1f}pt({gd*PT2MM:4.1f}mm) «{dns[0]['text'][:26]}»" if dns and gd<40 else (f"dn OVERLAP {-gd:5.1f}pt «{dns[0]['text'][:26]}»" if dns else "dn -")
        print(f"  y={y:6.1f} x={x0:5.1f}-{x1:5.1f} w={w:.2f} | {su} | {sd}")

print("\n===== B. 判断题 6 条全行序（题干每行 x0-x1/宽） =====")
pat = re.compile(r"判断正误|模相等，则|一定是共线|传递性失效|不唯一|共面向量定理|锐角，故|存在唯一实数|数量积大于|则这两个向量相等|则a∥c|共线向量（平行向量）|缺前提|故×|故√|^\s*（×）|^\s*（√）|^\s*（1）|^\s*（2）")
for p in range(d.page_count):
    pg=d[p]; rows=lines_of(pg)
    for i,r in enumerate(rows):
        t=r["text"]
        if re.search(r"判断正误", t):
            print(f"\n-- p{p+1} 诊断块 @y={r['bbox'][1]:.1f}")
            for r2 in rows[i:i+8]:
                b=r2["bbox"]
                print(f"   y={b[1]:6.1f}-{b[3]:6.1f} x={b[0]:6.1f}-{b[2]:6.1f} w={(b[2]-b[0])*PT2MM:5.1f}mm | {r2['text'][:52]}")

print("\n===== C. 行内字符间隙 >1.6em 实例（含上下文） =====")
for p in range(d.page_count):
    pg=d[p]; td=pg.get_text("rawdict")
    for b in td["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            chars=[]
            for s in l["spans"]:
                for c in s["chars"]:
                    chars.append((c["bbox"],c["c"]))
            chars.sort(key=lambda cc:(cc[0][0]))
            fsize = max(s["size"] for s in l["spans"])
            for i in range(len(chars)-1):
                (b1,c1),(b2,c2)=chars[i],chars[i+1]
                gap = b2[0]-b1[2]
                if gap > fsize*1.6 and gap>8:
                    txt="".join(cc[1] for cc in chars)
                    ctx = txt[max(0,i-6):i+1]+"▣"+txt[i+1:min(len(txt),i+7)]
                    print(f"[p{p+1}] y={l['bbox'][1]:.0f} fs={fsize:.1f} gap={gap:.1f}pt({gap*PT2MM:.1f}mm) …{ctx}…")

print("\n===== D. 大号数学定界符（高>13pt 的括号/竖线字符） =====")
targets=set("()[]|⟨⟩〈〉")
for p in range(d.page_count):
    pg=d[p]; td=pg.get_text("rawdict")
    for b in td["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                for c in s["chars"]:
                    ch=c["c"]; bb=c["bbox"]; h=bb[3]-bb[1]
                    if ch in targets and h>13:
                        print(f"[p{p+1}] y={bb[1]:.1f}-{bb[3]:.1f} h={h:.1f}pt({h*PT2MM:.2f}mm) ch={ch!r} font={s['font'][:28]} fs={s['size']:.1f} ctx={''.join(cc['c'] for cc in s['chars'])[:30]}")

print("\n===== E. 题号/标签字体三数（span 级采样） =====")
pats = {"题号_检测":r"^\s*\d．","题号_判断":r"^（\d）","例N":r"^例1","变式N":r"^变式1","答案标签":r"【答案】","解析标签":r"【解析】","条目号":r"^[1234]\."}
for p in range(d.page_count):
    pg=d[p]; td=pg.get_text("dict")
    for b in td["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                t=s["text"]
                for k,pat2 in pats.items():
                    if re.search(pat2,t) and len(t)<40:
                        col=s["color"]
                        print(f"[p{p+1}] {k:6s} fs={s['size']:5.2f} font={s['font'][:32]:32s} col=#{col:06x} fl={s['flags']} | {t[:30]}")
                        break
d.close(); print("\nDONE")
