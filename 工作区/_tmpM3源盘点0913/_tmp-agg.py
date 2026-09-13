import pymupdf, json, collections, re

PDF = "高中数学/2019人教B版高中数学教材/人教B选择性必修1.pdf"
doc = pymupdf.open(PDF)
data = json.load(open("工作区/_tmpM3源盘点0913/_tmp-events.json", encoding="utf-8"))
events = [tuple(e) for e in data["events"]]

# 节 / 小节 页码区间（书页，来自目录 p6-7；PDF = 书页 + 7）
SEC = [
    ("2.1", "坐标法", 71, 74, []),
    ("2.2", "直线及其方程", 75, 102,
     [("2.2.1", "直线的倾斜角与斜率", 75, 82), ("2.2.2", "直线的方程", 83, 90),
      ("2.2.3", "两条直线的位置关系", 91, 96), ("2.2.4", "点到直线的距离", 97, 102)]),
    ("2.3", "圆及其方程", 103, 122,
     [("2.3.1", "圆的标准方程", 103, 106), ("2.3.2", "圆的一般方程", 107, 109),
      ("2.3.3", "直线与圆的位置关系", 110, 115), ("2.3.4", "圆与圆的位置关系", 116, 122)]),
    ("2.4", "曲线与方程", 123, 128, []),
    ("2.5", "椭圆及其方程", 129, 143,
     [("2.5.1", "椭圆的标准方程", 129, 134), ("2.5.2", "椭圆的几何性质", 135, 143)]),
    ("2.6", "双曲线及其方程", 144, 157,
     [("2.6.1", "双曲线的标准方程", 144, 148), ("2.6.2", "双曲线的几何性质", 149, 157)]),
    ("2.7", "抛物线及其方程", 158, 167,
     [("2.7.1", "抛物线的标准方程", 158, 161), ("2.7.2", "抛物线的几何性质", 162, 167)]),
    ("2.8", "直线与圆锥曲线的位置关系", 168, 174, []),
    ("小结", "本章小结＋复习题", 175, 180, []),
]

def which(sy):
    for a, b, c1, c2, subs in SEC:
        if c1 <= sy <= c2:
            sub = next((s for s in subs if s[2] <= sy <= s[3]), None)
            return (a, b, sub[0] if sub else "", sub[1] if sub else "")
    return None

# ---- 块-题号归属：按页/纵坐标顺序扫描 ----
blocks = []   # (label, sec, start_pdf, start_y, items, examples)
cur = None
for pno, sy, y, x, kind, detail in events:
    if kind == "blk":
        cur = {"blk": detail, "pdf": pno, "sy": sy, "items": 0}
        blocks.append(cur)
    elif kind == "item" and cur is not None:
        cur["items"] += 1
    elif kind == "item" and cur is None:
        blocks.append({"blk": "(未挂块)", "pdf": pno, "sy": sy, "items": 1})

# 例题归属：按小节
li_by_sec = collections.Counter()
jie_by_sec = collections.Counter()
tab_by_sec = collections.Counter()
sub_by_sec = collections.Counter()
for pno, sy, y, x, kind, detail in events:
    w = which(sy)
    if not w:
        continue
    key = w[2] or w[0]
    if kind == "li":
        li_by_sec[key] += 1
    elif kind == "jie":
        jie_by_sec[key] += 1
    elif kind == "tab":
        tab_by_sec[key] += 1
    elif kind == "sub":
        sub_by_sec[key] += 1

blk_by_sec = collections.defaultdict(list)
for b in blocks:
    w = which(b["sy"])
    key = (w[2] or w[0]) if w else "?"
    blk_by_sec[key].append(b)

print("== 块题量 ==")
tot_items = 0
for a, b, c1, c2, subs in SEC:
    keys = [s[0] for s in subs] or [a]
    for k in keys:
        for blk in blk_by_sec.get(k, []):
            print(f"{k:>7} {blk['blk']:<12} 书页{blk['sy']:<4} 题数{blk['items']}")
            tot_items += blk["items"]
print("练习+习题 circled 题量合计:", tot_items)
print("li:", sum(li_by_sec.values()), dict(li_by_sec))
print("tab:", dict(tab_by_sec), "sub:", dict(sub_by_sec))

# ---- 复习题（章末，页码 175-180 = PDF 182-187）题量：正文可读数字编号 ----
txt = "\n".join(doc[p].get_text() for p in range(181, 187))
FW = "０１２３４５６７８９"
groups = re.split(r"[犃犅犆]组", txt)
print("\n== 章末 组 标记出现次数 ==", re.findall(r"[犃犅犆]组", txt))
nums = re.findall(r"^([" + FW + r"]{1,2})．", txt, re.M)
print("章末题号（行首 N．）:", [n.translate(str.maketrans(FW, "0123456789")) for n in nums])

# ---- 黑体术语 ----
bold = data["bold"]
print("\n== 黑体术语（按页） ==")
for pno in sorted(bold, key=int):
    sy = int(pno) - 7
    w = which(sy)
    terms = [t for _, t in sorted(bold[pno], key=lambda z: z[0])]
    print(f"书页{sy:>4} {(w[2] or w[0]) if w else '?':<8}", " | ".join(terms))
