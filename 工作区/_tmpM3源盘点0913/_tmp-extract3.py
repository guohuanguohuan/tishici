import pymupdf, json, collections

PDF = "高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf"
doc = pymupdf.open(PDF)
LIANXI = {0x22: "练习A", 0x23: "练习B"}
XITI_TAIL = {0x22: "A组", 0x23: "B组", 0x24: "C组"}
D = {0x11: '0', 0x12: '1', 0x13: '2', 0x14: '3', 0x15: '4', 0x16: '5', 0x17: '6', 0x18: '7', 0x19: '8', 0x1a: '9'}
CS = (0x114a, 0x41, 0x33b)      # 尝试与发现
TZ = (0x712, 0x2c1, 0x1ac8, 0x1ba5)  # 拓展阅读
FX = (0x72d, 0x2f8, 0x1ba5)     # 复习题
SUBS = [("2.1", 78, 0), ("2.2.1", 82, 201), ("2.2.2", 90, 80), ("2.2.3", 98, 80), ("2.2.4", 104, 480),
        ("2.3.1", 110, 201), ("2.3.2", 114, 80), ("2.3.3", 117, 341), ("2.3.4", 123, 531), ("2.4", 130, 0),
        ("2.5.1", 136, 201), ("2.5.2", 142, 548), ("2.6.1", 151, 201), ("2.6.2", 156, 285),
        ("2.7.1", 165, 201), ("2.7.2", 169, 424), ("2.8", 175, 0), ("小结", 182, 0)]

def locate(pno, y):
    cur = "?"
    for n, p, yy in SUBS:
        if (pno, y) >= (p, yy):
            cur = n
    return cur

codes = lambda s: tuple(ord(c) for c in s["text"])

def has(seq, sub):
    n = len(sub)
    return any(tuple(seq[i:i + n]) == sub for i in range(len(seq) - n + 1))
events = []
bars = []      # 箭头子标题条（待人工目读）
for pno in range(77, 188):
    spans = [s for b in doc[pno - 1].get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]
    hl = collections.defaultdict(list)
    for s in spans:
        if s["font"].startswith("FZLT") or s["font"].startswith("FZHTJW"):
            hl[round(s["bbox"][1] / 3)].append(s)
    for group in hl.values():
        group.sort(key=lambda s: s["bbox"][0])
        y = min(s["bbox"][1] for s in group); x = group[0]["bbox"][0]
        allc = tuple(c for s in group for c in codes(s))
        for s in group:
            c = codes(s)
            if s["font"].startswith("FZHTJW") and c:
                if c[0] == 0x393 and len(c) == 3 and c[2] in D:
                    events.append((pno, y, x, "li", "例" + D[c[2]]))
                elif c[0] == 0x174d:
                    events.append((pno, y, x, "jie", "解"))
                elif c[0] == 0x46c:
                    events.append((pno, y, x, "da", "答"))
        if has(allc, CS):
            events.append((pno, y, x, "tab", "尝试与发现"))
        elif has(allc, TZ):
            events.append((pno, y, x, "tab", "拓展阅读"))
        elif has(allc, FX):
            events.append((pno, y, x, "tab", "复习题"))
        elif len(allc) == 3 and allc[:2] == (0x1337, 0x2f8) and allc[2] in LIANXI:
            events.append((pno, y, x, "blk", LIANXI[allc[2]]))
        elif len(allc) >= 6 and allc[0] == 0x2f8 and allc[1] == 0x1ba5 and allc[2] == 0x13 and allc[3] == 0xe:
            events.append((pno, y, x, "blk", f"习题2-{D.get(allc[4], allc[4])}{XITI_TAIL.get(allc[5], '?')}"))
        elif len(allc) >= 3 and allc[1] == 0xf and allc[0] in D:
            events.append((pno, y, x, "sub", f"{D[allc[0]]}."))
            bars.append((pno, y, x, max(s["bbox"][1] for s in group), max(s["bbox"][2] for s in group)))
    for s in spans:
        if not (s["font"].startswith("F-BZ9") and s["size"] > 20 and s["bbox"][0] < 110):
            continue
        c = codes(s)
        # 题号＝①—⑨（未映射字形 0x3f）或 ⑩＋（U+FE63 连字符＋PUA 0xe7e8..，实测为两位数圈码）
        if c == (0x3f,) or (len(c) == 2 and c[0] == 0xfe63 and 0xe7e0 <= c[1] <= 0xe7ef):
            events.append((pno, s["bbox"][1], s["bbox"][0], "item", ""))
    # 你知道吗（仿宋栏目）
    yz = [s for s in spans if s["font"].startswith("FSJ") and s["text"].strip().startswith("你知道吗")]
    for s in yz:
        events.append((pno, s["bbox"][1], s["bbox"][0], "tab", "你知道吗"))
events.sort(key=lambda e: (e[0], e[1], e[2]))
json.dump([list(e) for e in events], open("工作区/_tmpM3源盘点0913/_tmp-events4.json", "w", encoding="utf-8"), ensure_ascii=False)

rows, cur = [], None
for pno, y, x, kind, detail in events:
    if kind == "blk":
        cur = {"sec": locate(pno, y), "blk": detail, "pdf": pno, "sy": pno - 7, "y": round(y), "items": 0}
        rows.append(cur)
    elif kind == "item" and cur is not None:
        cur["items"] += 1
stat = collections.defaultdict(lambda: collections.Counter())
for pno, y, x, kind, detail in events:
    s = locate(pno, y)
    if kind in ("li", "jie", "da"):
        stat[s][kind] += 1
    elif kind == "tab":
        stat[s][detail] += 1
    elif kind == "sub":
        stat[s]["sub"] += 1
json.dump({"rows": rows, "stat": {k: dict(v) for k, v in stat.items()}},
          open("工作区/_tmpM3源盘点0913/_tmp-tables4.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("blocks", len(rows), "items", sum(r["items"] for r in rows))
for k, v in stat.items():
    print(k, dict(v))
# 箭头条裁剪图
import os
os.makedirs("工作区/_tmpM3源盘点0913/_tmp页图", exist_ok=True)
for i, (pno, y, x, y2, x2) in enumerate(bars):
    r = pymupdf.Rect(max(0, x - 12), y - 10, min(560, max(x2 + 30, x + 200)), y2 + 10)
    pix = doc[pno - 1].get_pixmap(clip=r, matrix=pymupdf.Matrix(3, 3))
    pix.save(f"工作区/_tmpM3源盘点0913/_tmp页图/bar{i:02d}_p{pno}.png")
print("bars", len(bars))
