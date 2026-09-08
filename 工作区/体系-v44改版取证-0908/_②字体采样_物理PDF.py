# ②片专用：物理PDF 逐字体×字号 用途元素采样（只读）
import pymupdf, collections, json

BASE = r"C:\提示词\高中物理\参考\全品学练考官方样书\选必一"
FILES = {
    "练习册": "【5562】2025-2026（上）全品学练考 高中物理 选择性必修第一册 RJ 练习册.pdf",
    "导学案": "【5563】2025-2026（上）全品学练考 高中物理 选择性必修第一册 RJ 导学案.pdf",
    "测评卷": "【5564】2025-2026（上）全品学练考 高中物理 选择性必修第一册 RJ 测评卷.pdf",
}
FOCUS = ["FZSSK", "E-BZ", "E-BX", "FZLTHK", "FZLTZHK", "FZLTCHK", "FZLTXHK", "FZLTXIHJW",
         "FZHTK", "FZKTK", "FZFSK", "FZZYK", "FZY3K", "FZJINHJW", "FZPSZHJW", "FZLTHJW",
         "E-B6", "E-F2", "E-F3", "E-F4", "E-F5", "E-F6", "E-FZ", "E-XFZ", "E-YT1", "E-H4"]

res = {}
for label, fn in FILES.items():
    doc = pymupdf.open(BASE + "\\" + fn)
    samples = collections.defaultdict(list)
    for pno in range(doc.page_count):
        d = doc[pno].get_text("dict")
        for blk in d["blocks"]:
            if blk["type"] != 0:
                continue
            for line in blk["lines"]:
                # 行级聚合同字体的 span
                buf = collections.defaultdict(str)
                for sp in line["spans"]:
                    base = sp["font"].split("+")[-1].split("--")[0].split("-0")[0]
                    base = base.replace("FZLT", "FZLT")  # keep
                    key = (base, round(sp["size"], 1))
                    buf[key] += sp["text"]
                for (base, size), t in buf.items():
                    t = t.strip()
                    if t and len(samples[(base, size)]) < 6:
                        samples[(base, size)].append(f"p{pno+1}:{t[:20]}")
    res[label] = {f"{k[0]}@{k[1]}": v for k, v in samples.items()}
    doc.close()

with open(r"C:\提示词\工作区\体系-v44改版取证-0908\_②物理字体采样.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)

# 控制台：导学案全量＋练习册差异项
for label in ["导学案", "练习册", "测评卷"]:
    print(f"===== {label} =====")
    for key in sorted(res[label]):
        print(f"  {key:22s} | " + " ‖ ".join(res[label][key][:3]))
