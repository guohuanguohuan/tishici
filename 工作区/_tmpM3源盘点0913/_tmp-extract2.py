import pymupdf, json, collections, re

PDF = "高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf"
doc = pymupdf.open(PDF)

LIANXI = {0x22: "练习A", 0x23: "练习B"}
XITI_TAIL = {0x22: "A组", 0x23: "B组", 0x24: "C组"}
D = {0x11: '0', 0x12: '1', 0x13: '2', 0x14: '3', 0x15: '4',
     0x16: '5', 0x17: '6', 0x18: '7', 0x19: '8', 0x1a: '9'}
TAB_CHANGSHI = (0x114a, 0x41, 0x33b)
TAB_TUOZHAN = (0x712, 0x2c1, 0x1ac8, 0x1ba5)
TAB_FUXITI = (0x72d, 0x2f8, 0x1ba5)
LBL_LI, LBL_JIE, LBL_DA = 0x393, 0x174d, 0x46c

# 小节起点（PDF页, y）——由正文中可读的“2.2.1”等编号条定位
SUBS = [("2.1", 78, 0), ("2.2.1", 82, 201), ("2.2.2", 90, 80), ("2.2.3", 98, 80),
        ("2.2.4", 104, 480), ("2.3.1", 110, 201), ("2.3.2", 114, 80), ("2.3.3", 117, 341),
        ("2.3.4", 123, 531), ("2.4", 130, 0), ("2.5.1", 136, 201), ("2.5.2", 142, 548),
        ("2.6.1", 151, 201), ("2.6.2", 156, 285), ("2.7.1", 165, 201), ("2.7.2", 169, 424),
        ("2.8", 175, 0), ("小结", 182, 0)]

def locate(pno, y):
    cur = "?"
    for name, p, yy in SUBS:
        if (pno, y) >= (p, yy):
            cur = name
    return cur

def codes(s):
    return tuple(ord(c) for c in s["text"])

events = []
bold = collections.defaultdict(list)
for pno in range(77, 188):
    page = doc[pno - 1]
    spans = [s for b in page.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]
    hl = collections.defaultdict(list)
    for s in spans:
        if s["font"].startswith("FZLT") or s["font"].startswith("FZHTJW"):
            hl[round(s["bbox"][1] / 3)].append(s)
    for group in hl.values():
        group.sort(key=lambda s: s["bbox"][0])
        y = min(s["bbox"][1] for s in group)
        x = group[0]["bbox"][0]
        allc = tuple(c for s in group for c in codes(s))
        for s in group:
            c = codes(s)
            if s["font"].startswith("FZHTJW") and c:
                if c[0] == LBL_LI and len(c) == 3 and c[2] in D:
                    events.append((pno, y, x, "li", "例" + D[c[2]]))
                elif c[0] == LBL_JIE:
                    events.append((pno, y, x, "jie", "解"))
                elif c[0] == LBL_DA:
                    events.append((pno, y, x, "da", "答"))
        if allc[:3] == TAB_CHANGSHI:
            events.append((pno, y, x, "tab", "尝试与发现"))
        elif allc[:4] == TAB_TUOZHAN:
            events.append((pno, y, x, "tab", "拓展阅读"))
        elif TAB_FUXITI[0] in allc:
            dig = "".join(D.get(c, "") for c in allc if c in D)
            events.append((pno, y, x, "tab", "复习题" + dig))
        elif len(allc) == 3 and allc[:2] == (0x1337, 0x2f8) and allc[2] in LIANXI:
            events.append((pno, y, x, "blk", LIANXI[allc[2]]))
        elif len(allc) >= 6 and allc[0] == 0x2f8 and allc[1] == 0x1ba5 and allc[2] == 0x13 and allc[3] == 0xe:
            ev, grp = allc[4], XITI_TAIL.get(allc[5], "?")
            events.append((pno, y, x, "blk", f"习题2-{D.get(ev, ev)}{grp}"))
        elif len(allc) >= 3 and allc[1] == 0xf and allc[0] in D:
            events.append((pno, y, x, "sub", f"{D[allc[0]]}."))
    for s in spans:
        if s["font"].startswith("F-BZ9") and codes(s) == (0x3f,) and s["bbox"][0] < 110 and s["size"] > 20:
            events.append((pno, s["bbox"][1], s["bbox"][0], "item", ""))
    for s in spans:
        if s["font"].startswith("HTJ") and s["size"] >= 23:
            t = s["text"].strip()
            if t and any('\u4e00' <= c <= '\u9fff' for c in t):
                bold[pno].append((round(s["bbox"][1], 1), t))

events.sort(key=lambda e: (e[0], e[1], e[2]))
json.dump([list(e) for e in events], open("工作区/_tmpM3源盘点0913/_tmp-events2.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump({str(k): v for k, v in bold.items()}, open("工作区/_tmpM3源盘点0913/_tmp-bold.json", "w", encoding="utf-8"), ensure_ascii=False)

# ---- 块归属与题量 ----
rows = []
cur = None
for pno, y, x, kind, detail in events:
    if kind == "blk":
        cur = {"sec": locate(pno, y), "blk": detail, "pdf": pno, "sy": pno - 7, "items": 0}
        rows.append(cur)
    elif kind == "item" and cur is not None:
        cur["items"] += 1
print("== 练习/习题块 ==")
tot = 0
for r in rows:
    print(f"{r['sec']:<7} {r['blk']:<12} 书页{r['sy']:<4} 题数 {r['items']}")
    tot += r["items"]
print("块数", len(rows), "题量合计", tot)

li = collections.Counter(); tab = collections.Counter(); sub = collections.Counter()
for pno, y, x, kind, detail in events:
    s = locate(pno, y)
    if kind == "li": li[s] += 1
    elif kind == "tab": tab[(s, detail)] += 1
    elif kind == "sub": sub[s] += 1
print("\n例题：", dict(li), "合计", sum(li.values()))
print("栏目：", dict(tab))
print("子标题条：", dict(sub))

# ---- 章末复习题 ----
txt = "\n".join(doc[p].get_text() for p in range(181, 187))
marks = [(m.start(), m.group()) for m in re.finditer(r"[犃犅犆]组", txt)]
print("\n== 复习题组标记 ==", marks)
FW = "０１２３４５６７８９"
for idx, (pos, g) in enumerate(marks):
    seg = txt[pos:marks[idx + 1][0] if idx + 1 < len(marks) else len(txt)]
    nums = [int(n.translate(str.maketrans(FW, "0123456789"))) for n in re.findall(r"^\s*([" + FW + r"]{1,2})", seg, re.M)]
    print(g, "题号", nums, "共", len(nums))
