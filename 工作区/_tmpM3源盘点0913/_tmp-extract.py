import pymupdf, json, collections

PDF = "高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf"
doc = pymupdf.open(PDF)

# ---- label signatures observed in the embedded (broken-ToUnicode) heading fonts ----
# FZLTZHJW: 练习A/B = [0x1337,0x2f8,0x22/0x23] ; FZLTDHJW: 习题2-N + [0x13,0xe,digit,letter]
LIANXI = {0x22: "练习A", 0x23: "练习B"}
XITI_TAIL = {0x22: "A组", 0x23: "B组", 0x24: "C组"}
DIG10 = {0x11: '0', 0x12: '1', 0x13: '2', 0x14: '3', 0x15: '4',
         0x16: '5', 0x17: '6', 0x18: '7', 0x19: '8', 0x1a: '9'}
TAB_CHANGSHI = (0x114a, 0x41, 0x33b)      # 尝试与发现 (first span)
TAB_TUOZHAN = (0x712, 0x2c1, 0x1ac8, 0x1ba5)  # 拓展阅读
TAB_FUXITI = (0x72d, 0x2f8, 0x1ba5)       # 复习题
LBL_LI = 0x393      # 例
LBL_JIE = 0x174d    # 解
LBL_DA = 0x46c      # 答

def codes(s):
    return tuple(ord(c) for c in s["text"])

events = []          # (pdf_page, shuye, y, x, kind, detail)
bold_terms = collections.defaultdict(list)   # pdf_page -> [(y, term)]

for pno in range(77, 188):
    page = doc[pno - 1]
    spans = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                spans.append(s)
    # group heading-font spans into lines
    hl = collections.defaultdict(list)
    for s in spans:
        f = s["font"]
        if f.startswith("FZLT") or f.startswith("FZHTJW"):
            hl[round(s["bbox"][1] / 3)].append(s)
    for key, group in hl.items():
        group.sort(key=lambda s: s["bbox"][0])
        y = min(s["bbox"][1] for s in group)
        allc = [c for s in group for c in codes(s)]
        x = group[0]["bbox"][0]
        # 例题 / 解 / 答
        for s in group:
            c = codes(s)
            if s["font"].startswith("FZHTJW") and c:
                if c[0] == LBL_LI and len(c) == 3 and c[2] in DIG10:
                    events.append((pno, pno - 7, y, x, "li", "例" + DIG10[c[2]]))
                elif c[0] == LBL_JIE:
                    events.append((pno, pno - 7, y, x, "jie", "解"))
                elif c[0] == LBL_DA:
                    events.append((pno, pno - 7, y, x, "da", "答"))
        if allc[:3] == TAB_CHANGSHI:
            events.append((pno, pno - 7, y, x, "tab", "尝试与发现"))
        elif allc[:4] == TAB_TUOZHAN:
            events.append((pno, pno - 7, y, x, "tab", "拓展阅读"))
        elif allc[:3] == TAB_FUXITI:
            tail = [c for c in allc if c not in TAB_FUXITI]
            events.append((pno, pno - 7, y, x, "tab", "复习题" + "".join(DIG10.get(t, "?") for t in tail)))
        elif len(allc) == 3 and allc[0] == 0x1337 and allc[1] == 0x2f8 and allc[2] in LIANXI:
            events.append((pno, pno - 7, y, x, "blk", LIANXI[allc[2]]))
        elif len(allc) == 6 and allc[0] == 0x2f8 and allc[1] == 0x1ba5 and allc[2] == 0x13 and allc[3] == 0xe:
            ev = allc[4]
            grp = XITI_TAIL.get(allc[5], "?")
            events.append((pno, pno - 7, y, x, "blk", f"习题2-{DIG10.get(ev, ev)}{grp}"))
        elif len(allc) >= 3 and allc[1] == 0xf and allc[2] == 0x1 and allc[0] in DIG10:
            # arrow-bar sub heading: "N. 标题"（标题为乱码字体，只留编号与位置）
            events.append((pno, pno - 7, y, x, "sub", f"{DIG10[allc[0]]}."))
    # circled item markers in the left margin (练习/习题 题号)
    for s in spans:
        if s["font"].startswith("F-BZ9") and codes(s) == (0x3f,) and s["bbox"][0] < 95 and s["size"] > 20:
            events.append((pno, pno - 7, s["bbox"][1], s["bbox"][0], "item", ""))
    # 黑体（HTJ）正文术语 = 定义/知识点标题
    for s in spans:
        if s["font"].startswith("HTJ") and s["size"] >= 23:
            t = s["text"].strip()
            if t and any('\u4e00' <= c <= '\u9fff' for c in t):
                bold_terms[pno].append((round(s["bbox"][1], 1), t))

events.sort(key=lambda e: (e[0], e[2], e[3]))
json.dump({"events": events, "bold": {str(k): v for k, v in bold_terms.items()}},
          open("工作区/_tmpM3源盘点0913/_tmp-events.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

cnt = collections.Counter(e[4] for e in events)
print(cnt)
print("li total", sum(1 for e in events if e[4] == "li"))
for e in events:
    if e[4] in ("blk", "tab", "sub"):
        print(e[0], e[1], round(e[2]), e[4], e[5])
