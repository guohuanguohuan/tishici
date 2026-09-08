# ②片专用取证脚本：物理线全品电子版 PDF 嵌入字体普查（只读）
# 用法：python _②字体普查_物理PDF.py  （在 C:\提示词 下）
import pymupdf, json, collections, sys

BASE = r"C:\提示词\高中物理\参考\全品学练考官方样书\选必一"
FILES = {
    "练习册": "【5562】2025-2026（上）全品学练考 高中物理 选择性必修第一册 RJ 练习册.pdf",
    "导学案": "【5563】2025-2026（上）全品学练考 高中物理 选择性必修第一册 RJ 导学案.pdf",
    "测评卷": "【5564】2025-2026（上）全品学练考 高中物理 选择性必修第一册 RJ 测评卷.pdf",
}

out = {}
for label, fn in FILES.items():
    doc = pymupdf.open(BASE + "\\" + fn)
    # 1) 全文档嵌入字体清单
    fonts = {}
    for pno in range(doc.page_count):
        for f in doc.get_page_fonts(pno, full=True):
            xref, ext, ftype, basefont, name, enc = f[0], f[1], f[2], f[3], f[4], f[5]
            fonts.setdefault((basefont, ftype), set()).add(ext)
    # 2) span 级字号分布：字体名 × 字号 × 用量
    span_stat = collections.Counter()
    sample_text = collections.defaultdict(list)
    color_stat = collections.defaultdict(collections.Counter)
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
                    span_stat[key] += len(t)
                    if len(sample_text[key]) < 4 and len(t) >= 2:
                        sample_text[key].append((pno + 1, t[:24]))
                    color_stat[key][sp["color"]] += 1
    out[label] = {
        "pages": doc.page_count,
        "fonts": [{"basefont": k[0], "type": k[1], "ext": sorted(v)} for k, v in fonts.items()],
        "spans": [
            {"font": k[0], "size_pt": k[1], "chars": n,
             "sample": sample_text[k],
             "colors": dict(color_stat[k].most_common(3))}
            for k, n in sorted(span_stat.items(), key=lambda kv: -kv[1])
        ],
    }
    doc.close()

with open(r"C:\提示词\工作区\体系-v44改版取证-0908\_②物理字体普查_raw.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# 控制台摘要：仅列字体名全谱＋每字体的字号档
for label, o in out.items():
    print(f"== {label} ({o['pages']}页) ==")
    names = sorted(set(x["basefont"] for x in o["fonts"]))
    for n in names:
        sizes = sorted(set(s["size_pt"] for s in o["spans"] if s["font"] == n), reverse=True)
        total = sum(s["chars"] for s in o["spans"] if s["font"] == n)
        print(f"  {n}  [{total}字] 字号档: {sizes}")
print("done")
