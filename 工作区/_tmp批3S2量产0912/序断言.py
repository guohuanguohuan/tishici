# -*- coding: utf-8 -*-
# 衔接节-1.2.1前 序断言（R7 防「白做29题」）｜批3 件2
# 判据（题面库-衔接节＋全章定稿汇总 §3.2/§3.3 冻结约束）：
#  ①衔接1..29 版面阅读序升序（multicols：页→列桶→y；x0 需列桶量化，浮点噪声 1e-5pt 级不可直接排序）；
#  ②衔接5 与衔接7 同页（组二侧等面积「公式—数值」讲一次）；
#  ③衔接20 与衔接22 同页（同约束四心侧，题面库-20清稿注）；
#  ④四心知识讲块先于第四组组行；
#  ⑤垂心族(17/23/25)与两心重合族(21/28)阅读序无邻接；
#  ⑥衔接18 先于 24/29（张角结论前置）；
#  ⑦衔接2/3 本栏近旁带图（图指代用题必配图抽检）。
# 用法：python 序断言.py [main.pdf]
import re, sys, io
import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
PDF = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:\提示词\工作区\M2-第1章量产0911\成卷\导学件\衔接节-1.2.1前\main.pdf"
COLMID = 180.0  # 双栏分界（pt）：x0<180 左栏，否则右栏

def col(x):
    return 0 if x < COLMID else 1

doc = pymupdf.open(PDF)
items = {}    # N -> [(page, col, y, x0raw)]
pageimg = {}  # page -> [(x0,y0,x1,y1)]
for pno, page in enumerate(doc, start=1):
    rects = []
    for x in page.get_images(full=True):
        r = page.get_image_bbox(x)
        if r is not None and r.width > 0:
            rects.append((r.x0, r.y0, r.x1, r.y1))
    pageimg[pno] = rects
    for b in page.get_text("blocks"):
        x0, y0, txt = b[0], b[1], b[4]
        for m in re.finditer(r"衔接\s*(\d{1,2})\.", txt):
            items.setdefault(int(m.group(1)), []).append((pno, col(x0), y0, x0))

def key(N):
    return sorted(items[N], key=lambda t: t[:3])

fails = []
# ① 升序
seq = sorted(items, key=lambda N: key(N)[0][:3])
ok = seq == list(range(1, 30))
print(f"①版面升序（29 题全号段）: {'PASS' if ok else f'FAIL {seq}'}")
if not ok:
    fails.append("①")
# ②③ 同页
for a, b, lab in ((5, 7, "②组二侧"), (20, 22, "③四心侧")):
    pa = {p for p, *_ in items[a]}; pb = {p for p, *_ in items[b]}
    o = bool(pa & pb)
    print(f"{lab}: 衔接{a}@页{sorted(pa)} 衔接{b}@页{sorted(pb)} -> {'PASS' if o else 'FAIL'}")
    if not o:
        fails.append(lab)
# ④ 讲块先于组四
fullpos = []
for pno, page in enumerate(doc, start=1):
    for b in page.get_text("blocks"):
        fullpos.append((pno, col(b[0]), b[1], b[4].replace("\n", " ")))
def firstpos(pat):
    rx = re.compile(pat)
    hits = sorted((t for t in fullpos if rx.search(t[3])), key=lambda t: t[:3])
    return hits[0] if hits else None
zhub, zu4, zu1 = firstpos(r"知识讲块"), firstpos(r"四、三角形"), firstpos(r"一、平行线分线段")
o = bool(zhub and zu1 and zu4 and zu1[:3] < zhub[:3] < zu4[:3])
print(f"④讲块@{zhub[:3] if zhub else None} 在组一@{zu1[:3] if zu1 else None} 后、组四@{zu4[:3] if zu4 else None} 前 -> {'PASS' if o else 'FAIL'}")
if not o:
    fails.append("④")
# ⑤ 邻接
stream = sorted(((key(N)[0][:3], N) for N in items))
rank = {N: i for i, (pos, N) in enumerate(stream)}
bad = [(a, b) for a in (17, 23, 25) for b in (21, 28) if abs(rank[a] - rank[b]) <= 1]
print(f"⑤垂心族17/23/25 vs 两心重合族21/28 相邻对: {bad if bad else '无'} -> {'PASS' if not bad else 'FAIL'}")
if bad:
    fails.append("⑤")
# ⑥ 18 先于 24/29
o = key(18)[0][:3] < key(24)[0][:3] and key(18)[0][:3] < key(29)[0][:3]
print(f"⑥衔接18@{key(18)[0][:3]} 先于 24@{key(24)[0][:3]} / 29@{key(29)[0][:3]} -> {'PASS' if o else 'FAIL'}")
if not o:
    fails.append("⑥")
# ⑦ 图位抽检
for N in (2, 3):
    p, c, y, x = key(N)[0]
    o = any(-6 <= ry0 - y <= 130 and (col(rx0) == c or col(rx1) == c)
            for (rx0, ry0, rx1, ry1) in pageimg[p])
    print(f"⑦衔接{N} 本栏近旁带图 -> {'PASS' if o else 'FAIL'}")
    if not o:
        fails.append(f"⑦衔接{N}")
print("=" * 40)
print("RESULT:", "ALL PASS" if not fails else f"FAILS={fails}")
sys.exit(1 if fails else 0)
