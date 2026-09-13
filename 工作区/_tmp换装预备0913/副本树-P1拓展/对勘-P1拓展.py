# -*- coding: utf-8 -*-
"""对勘-P1拓展：原印面页级零漂移＋逐卡灰底/括线量测＋像素比对＋PNG 出图。"""
import hashlib, json, os, re
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(HERE, "拓展册")
ORIG = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/拓展册/main.pdf"
man = json.load(open(os.path.join(HERE, "试迁键账-拓展.json"), encoding="utf-8"))

MM = 72 / 25.4
PAGE_W, PAGE_H = 595.276, 841.89
BANDS = {
    2: [(17.2 * MM, 101.2 * MM), (108.8 * MM, 192.8 * MM)],
    3: [(17.2 * MM, 70.667 * MM), (78.267 * MM, 131.733 * MM), (139.333 * MM, 192.8 * MM)],
}
COLH = 257.4 * MM   # 版心高 297−19.6−20

def norm(s):
    return re.sub(r"\s+", "", s)

def pages_of(pdf):
    doc = pymupdf.open(pdf)
    return [p.get_text() for p in doc], len(doc)

def render(pdf, outdir, dpi=150):
    os.makedirs(outdir, exist_ok=True)
    doc = pymupdf.open(pdf)
    for i, p in enumerate(doc, 1):
        p.get_pixmap(dpi=dpi).save(os.path.join(outdir, "page%d.png" % i))
    return len(doc)

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

t_orig, n_orig = pages_of(ORIG)
t_base, n_base = pages_of(os.path.join(PIECE, "main.pdf"))
t_true, n_true = pages_of(os.path.join(PIECE, "main-换装-true.pdf"))
t_false, n_false = pages_of(os.path.join(PIECE, "main-换装-false.pdf"))

print("== ① 页数与工具链基线 ==")
print("页数: 原印面=%d 基线复编译=%d true=%d false=%d" % (n_orig, n_base, n_true, n_false))
print("断言: false≤true %s；false=原页数 %s" % (n_false <= n_true, n_false == n_orig))
eq = all(norm(a) == norm(b) for a, b in zip(t_orig, t_base)) and n_orig == n_base
print("基线复编译 vs 原印面 逐页文本全等: %s" % ("PASS" if eq else "FAIL"))

print("== ② 像素级（150dpi MD5，原印面 vs 基线/纯题档） ==")
render(ORIG, os.path.join(HERE, "png-原印面"))
render(os.path.join(PIECE, "main.pdf"), os.path.join(HERE, "png-基线"))
render(os.path.join(PIECE, "main-换装-true.pdf"), os.path.join(HERE, "png-true"))
render(os.path.join(PIECE, "main-换装-false.pdf"), os.path.join(HERE, "png-false"))
for tag, d in [("基线", "png-基线"), ("false", "png-false")]:
    same = [i + 1 for i in range(n_orig)
            if md5(os.path.join(HERE, "png-原印面", "page%d.png" % (i + 1)))
            == md5(os.path.join(HERE, d, "page%d.png" % (i + 1)))]
    print("  %-4s 与原印面逐像素同页: %s" % (tag, same))

print("== ③ 题序锚（46 题干/选项 distinctive 片段，沿件面单调） ==")
anchors = [
    "此处不再重复呈现题面", "现将A、B接触后再分开", "光滑水平面上有三个带电小球",
    "悬挂于天花板上，平衡时细线竖直", "的小球A固定在倾角", "的完全相同的金属球壳",
    "电荷量分别为", "V型对接的绝缘斜面", "在挡板上连接一根劲度系数", "带电金属小球A套在倾角",
    "圆环被竖直固定", "光滑绝缘杆MN、NP上", "两根绝缘细线的上端都系在", "光滑绝缘杆弯成直角",
    "水平天花板下方固定一光滑小定滑轮", "的绝缘丝线相互连接", "两根绝缘轻绳将两个", "沿一直线有三个带电小球",
    "绝缘光滑细杆与水平方向夹角为", "电场线分布如图所示，下列说法正确的是", "内壁光滑的绝缘细管",
    "虚线为某带电粒子只在静电力作用下", "水平面上有一均匀带电圆环", "点电荷与均匀带电薄板相距",
    "均匀带正电的绝缘细圆环", "固定于光滑绝缘水平面上的", "的圆盘上均匀分布着电荷量",
    "半球面AB上均匀分布着正电荷", "分别为M点和N点", "的正方体的两个顶点上",
    "就可以判断结论是否正确", "均匀分布在半球面ACB上", "常见的四种电场分布如图所示",
    "两正四面体边长均为", "A、B、O三点在同一直线上", "平面是无穷大导体的表面",
    "一簇未标明方向的由点电荷产生", "竖直面内一绝缘细圆环", "一无限大接地导体板",
    "中央轴线上距离O点为", "某科学博物馆有一个令人印象深刻", "在优质话筒线外包金属网线",
    "用金属网把验电器罩起来", "避雷针上方有雷雨云时", "用起电机使金属鸟笼带电",
    "不带电的金属球壳导体置于匀强电场中",
]
assert len(anchors) == 46
def order_idx(txt):
    idx, pos = [], 0
    for a in anchors:
        i = txt.find(norm(a), pos)
        assert i >= 0, "缺锚: %s" % a
        idx.append(i); pos = i
    return idx
o, u, f = norm("\n".join(t_orig)), norm("\n".join(t_true)), norm("\n".join(t_false))
io, iu, if_ = order_idx(o), order_idx(u), order_idx(f)
print("锚: 原=%d true=%d false=%d 全中；三档单调一致（题序/题面零漂移）" % (len(io), len(iu), len(if_)))

print("== ④ 元素计数（true 应有/false 应零/尾块两档在） ==")
for s, et, ef in [("[答案]", 46, 0), ("[详解]", 2, 0), ("笔记与错题整理", 1, 1)]:
    a, b, c = o.count(norm(s)), u.count(norm(s)), f.count(norm(s))
    ok = (b == et and c == ef and a == 0)
    print("  %-10s 原=%d true=%d(期%d) false=%d(期%d) %s" % (s, a, b, et, c, ef, "PASS" if ok else "FAIL"))
print("  [答案] 等 true 独有即 false 档印面＝原印面语义的换装面证据")

print("== ⑤ 答案值抽检（true 独有；原/false 零命中） ==")
for s in ["合场强为", "注记位（A-2式）", "正解取49题9详解正确结论", "半截子理解"]:
    ss = norm(s)
    a, b, c = o.count(ss), u.count(ss), f.count(ss)
    print("  %-16s 原=%d true=%d false=%d %s" % (s, a, b, c, "PASS" if (b >= 1 and c == 0 and a == 0) else "FAIL"))

print("== ⑥ tex 层值零漂移（键账 vs 生成的 main-换装.tex 逐字） ==")
mig = open(os.path.join(PIECE, "main-换装.tex"), encoding="utf-8").read()
def parse_item_line(line):
    m = re.match(r"\\ansitem\{(\d+)\}\{", line)
    assert m, "ansitem 行解析失败: %r" % line[:50]
    i = m.end(); depth = 1; j = i
    while depth:
        if line[j] == "{":
            depth += 1
        elif line[j] == "}":
            depth -= 1
        j += 1
    val, rest = line[i:j - 1], line[j:]
    note = None
    mn = re.match(r"\\ansnote\{详解\}\{", rest)
    if mn:
        assert rest.endswith("}"), "详解括号失衡: %r" % rest[:60]
        note = rest[mn.end():-1]
    return int(m.group(1)), val, note

bad = []
for k, v in man["键值"].items():
    seg_m = re.search(re.escape(k) + r"\]\n% ans:" + re.escape(k) + r"\n(.+)$", mig, re.M)
    if not seg_m:
        bad.append(k); continue
    n_, val, note = parse_item_line(seg_m.group(1))
    if n_ != int(k.split("-")[1]) or val != v or note != man["详解随键"].get(k):
        bad.append(k)
print("  46 键逐字断言（含详解随键 2 处逐字）: %s" % ("PASS" if not bad else "FAIL %s" % bad))
fp10 = norm(t_false[-1])
p10frags = ["不带电的金属球壳导体置于匀强电场中", "球壳外表面附近的电场线不必与壳面垂直"]
print("  false 末页 p10 题面片段 %d/%d 在: %s；尾块文本在 %s" % (
    len(p10frags), len(p10frags), all(norm(x) in fp10 for x in p10frags), "PASS" if "笔记与错题整理" in fp10 else "FAIL"))

print("== ⑦ 逐卡量测（灰底 F0F0F0 卡块／括线 7A7A7A 线） ==")
GRAY, RULE = (0.941176, 0.941176, 0.941176), (122 / 255, 122 / 255, 122 / 255)
def near(c, ref):
    return c is not None and all(abs(x - y) < 0.004 for x, y in zip(c, ref))

def measure(pdf, ncol):
    doc = pymupdf.open(pdf)
    cards, strokes = [], []
    for pno, page in enumerate(doc, 1):
        for d in page.get_drawings():
            if d.get("fill") and near(d["fill"], GRAY):
                r = d["rect"]
                cards.append((pno, r.x0, r.y0, r.width, r.height))
            for it in d.get("items", []):
                if it[0] == "l" and near(d.get("color"), RULE):
                    p1, p2 = it[1], it[2]
                    strokes.append((pno, min(p1.x, p2.x), min(p1.y, p2.y),
                                    abs(p2.x - p1.x), abs(p2.y - p1.y)))
                elif it[0] == "re" and near(d.get("color"), RULE):
                    r = it[1]
                    strokes.append((pno, r.x0, r.y0, r.width, r.height))
    return cards, strokes

def band_of(x0, x1, ncol):
    for bi, (a, b) in enumerate(BANDS[ncol], 1):
        if x0 >= a - 2.5 and x1 <= b + 2.5:
            return bi
    return None

for name, ncol, exp_gray, exp_stroke in [
        ("main-换装-true.pdf", 2, 45, 4), ("main-换装-false.pdf", 2, 0, 2),
        ("压测A-三栏灰底-true.pdf", 3, 46, 2), ("压测B-两栏括线-true.pdf", 2, 0, 94),
        ("压测C-三栏括线-true.pdf", 3, 0, 94)]:
    cards, strokes = measure(os.path.join(PIECE, name), ncol)
    oob = [c for c in cards if band_of(c[1], c[1] + c[3], ncol) is None]
    tall = [c for c in cards if c[4] > COLH]
    overlap = 0
    bycol = {}
    for c in cards:
        b = band_of(c[1], c[1] + c[3], ncol)
        if b:
            bycol.setdefault((c[0], b), []).append(c)
    for lst in bycol.values():
        lst.sort(key=lambda c: c[2])
        for a, b in zip(lst, lst[1:]):
            if b[2] < a[2] + a[4] - 2.5:
                overlap += 1
    hs = sorted(c[4] / MM for c in cards)
    sths = [s for s in strokes if s[4] > 2]   # 非竖直细线的横线
    ok = (len(cards) == exp_gray and not oob and not tall and overlap == 0
          and len(strokes) == exp_stroke)
    print("  %-24s 灰卡=%d(期%d) 括线/尾线=%d(期%d) 出栏=%d 超栏高=%d 同栏叠印=%d" % (
        name, len(cards), exp_gray, len(strokes), exp_stroke, len(oob), len(tall), overlap),
        "最高卡=%.1fmm" % max(hs) if hs else "", "PASS" if ok else "FAIL")
    if name.startswith("main-换装-true"):
        for i, (pno, x, y, w, h) in enumerate(sorted(cards, key=lambda c: -c[4])[:5], 1):
            print("    true 最高卡 Top%d: p%d 列%d x=%.1fmm h=%.1fmm" % (i, pno, band_of(x, x + w, ncol), x / MM, h / MM))
        print("    true 括线/尾线 stroke: %s" % [
            "p%d 列%d y=%.1fmm w=%.1fmm" % (s[0], band_of(s[1], s[1] + s[3], ncol), s[2] / MM, s[3] / MM)
            for s in sorted(strokes, key=lambda s: (s[0], s[2]))])
    if name.startswith("压测A"):
        for i, (pno, x, y, w, h) in enumerate(sorted(cards, key=lambda c: -c[4])[:3], 1):
            print("    压测A 最高卡 Top%d: p%d 列%d h=%.1fmm（栏高限 %.0fmm）" % (i, pno, band_of(x, x + w, ncol), h / MM, COLH / MM))

print("== ⑧ 压测 PNG 出图 ==")
for name, d in [("压测A-三栏灰底-true", "png-压测A"), ("压测B-两栏括线-true", "png-压测B"), ("压测C-三栏括线-true", "png-压测C")]:
    n = render(os.path.join(PIECE, name + ".pdf"), os.path.join(HERE, d))
    print("  %-20s → %s（%d 页）" % (name, d, n))
print("DONE")
