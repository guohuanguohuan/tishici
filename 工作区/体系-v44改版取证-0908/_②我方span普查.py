# ②片专用：我方 v4.3 导学件 main.pdf span 级字体/字号/颜色普查（只读）
import pymupdf, collections, json

PDF = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件\main.pdf"
doc = pymupdf.open(PDF)
print("pages:", doc.page_count)

stat = collections.Counter()
samples = collections.defaultdict(list)
colors = collections.defaultdict(collections.Counter)
for pno in range(doc.page_count):
    d = doc[pno].get_text("dict")
    for blk in d["blocks"]:
        if blk["type"] != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                t = sp["text"].strip()
                if not t:
                    continue
                key = (sp["font"], round(sp["size"], 2))
                stat[key] += len(t)
                colors[key][sp["color"]] += 1
                if len(samples[key]) < 5:
                    samples[key].append(f"p{pno+1}:{t[:16]}")

for key, n in sorted(stat.items(), key=lambda kv: -kv[1]):
    cs = {f"{c:06X}": v for c, v in colors[key].most_common(2)}
    print(f"{key[0]:34s} {key[1]:6.2f}pt {n:6d}字 色{cs}  | " + " ‖ ".join(samples[key]))
doc.close()
