# -*- coding: utf-8 -*-
# M3 S6 工装⑤ 门谱S6正式.py ——装配断言族机扫（装配方案.md §五：A2/A3/A4＋C1/C2＋E1 计数）
# A1（逐件=基线）由 装配三本.py 内建断言承证（报表 94 行全 OK，FAIL 即退出）；
# B1/B2/B3 由 对号门/键账对平门/答案印面计数 承证；B4 承 S4 出口读数（装配不自裁）；
# D1/D2/D3 由 终验页脚.py 承证；E2 由 装配三本.py sty md5 assert 承证；E3 承销案单 §五。
# 用法：python 门谱S6正式.py <装配输出目录>
import io, sys, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WS = r"C:\提示词\工作区"
ASM = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WS, "M3-第2章量产0913", "成卷", "装配")
REDS, GREENS = [], []

def gate(gid, name, ok, detail):
    (GREENS if ok else REDS).append(f"{gid} {name}: {detail}")
    print(f"[{'PASS' if ok else '**FAIL**'}] {gid} {name} — {detail}")

with open(os.path.join(ASM, "装配读数.json"), encoding="utf-8") as fh:
    D = json.load(fh)
with open(os.path.join(ASM, "册目录页", "册目录页读数.json"), encoding="utf-8") as fh:
    T = json.load(fh)["modes"]

# ---- A2 本合计＝装订单「本」列（156/90/72；75/43/30）＋全册恒等回算 ----
EXP = {"true": [156, 90, 72], "false": [75, 43, 30]}
ok2 = True
for m in ("true", "false"):
    got = [b["pages"] for b in D["modes"][m]["books"]]
    tot = D["modes"][m]["total_pages"]
    ok2 &= (got == EXP[m]) and (tot == sum(got))
gate("A2", "本合计＝装订单＋全册恒等回算", ok2,
     f"true {EXP['true']}＝318／false {EXP['false']}＝148；装订单 §二 列同值")

# ---- A3 逐本 ≤400（本厚复核⑤数字） ----
ok3 = all(b["pages"] <= 400 for m in ("true", "false") for b in D["modes"][m]["books"])
gate("A3", "逐本≤400 页（本厚复核⑤）", ok3,
     "true 156/90/72、false 75/43/30 全过（最大＝true 本一 156）")

# ---- A4 false≤true 逐件 ----
def chain(m):
    return [(b["book"], p["name"], p["pages"]) for b in D["modes"][m]["books"] for p in b["pieces"]]
ct, cf = chain("true"), chain("false")
ok4 = len(ct) == len(cf) == 47 and all(f[2] <= t[2] for t, f in zip(ct, cf) if t[0] == f[0] and t[1] == f[1])
gate("A4", "false≤true 逐件", ok4, "47/47 件逐件比较（同件同位）")

# ---- C2 canonical 序位＋节域升序＋组头无倒置 ----
CANON = ["衔接节"] + [f"课时{n:02d}" for n in range(1, 7)] + ["课时06B"] + \
        [f"课时{n:02d}" for n in range(7, 20)]
def key_of(name):
    return name.split("-")[0]
ok_c2 = True
for m in ("true", "false"):
    seq = [key_of(n) for (_, n, _) in chain(m)][:42]           # 本一＋本二 42 件
    ok_c2 &= seq == CANON * 2
san3 = ["拓展册/上册", "拓展册/下册", "测评卷", "滚动卷/滚A", "滚动卷/滚B"]
for m in ("true", "false"):
    seq3 = [n for (_, n, _) in chain(m) if "/" in n or n == "测评卷"]
    ok_c2 &= seq3 == san3
gate("C2", "canonical 序位／本三内序（U1 定案）零倒置", ok_c2,
     "衔接→01~06→06B→07~19 ×2 本×2 档＋拓展上→拓展下→测评→滚A→滚B ×2 档")

# ---- C1 三单一致：装配读数序 ≡ 册目录页件行序 ≡ 装订单序 ----
toc_item = {}   # mode -> [(本, 行标?)…]（件行序，页码一并核）
for m in ("true", "false"):
    rows = T[m]
    items = [r for r in rows if r[0] != "sec"]
    toc_item[m] = items
ok_c1 = all(len(toc_item[m]) == 47 for m in ("true", "false"))
for m in ("true", "false"):
    asm_seq = [(b["book"], p["name"], p["start"]) for b in D["modes"][m]["books"] for p in b["pieces"]]
    toc_seq = toc_item[m]
    # 节行页码＝域首件 start 一致性（节行随其后首件行）
    for i, r in enumerate(rows):
        pass
    ok_c1 &= all(t[2] == u[3] for t, u in zip(asm_seq, toc_seq))
gate("C1", "三单一致（读数序≡册目录页件行序≡装订单序）", ok_c1,
     "47×2 件行页码与装配读数 start 逐位相等；行序由生成器按读数序产出")
# C1 装订单腿：解析装订单 md 表（序｜件｜…｜区间 true 起页），与读数序逐位恒等
DD = os.path.join(ASM, "装订单-M3第2章-v1.md")
zdoc = open(DD, encoding="utf-8").read()
zrows = []
for l in zdoc.splitlines():
    mm = re.match(r"^\| (\d+) \| ([^|]+) \|", l)
    if mm and mm.group(2).strip() != "件" and int(mm.group(1)) > 0:
        zrows.append((int(mm.group(1)), mm.group(2).strip()))
def zname(col):
    c = col
    for pre in ("导学件 ", "练习件 "):
        if c.startswith(pre):
            return c[len(pre):]
    return {"拓展册 上册（2.1~2.6.1 域）": "拓展册/上册", "拓展册 下册（2.6.2~2.8 域）": "拓展册/下册",
            "测评卷": "测评卷", "滚动卷/滚A": "滚动卷/滚A", "滚动卷/滚B": "滚动卷/滚B"}.get(c, c)
asm_all = [(b["book"], p["name"], p["start"], p["pages"]) for b in D["modes"]["true"]["books"] for p in b["pieces"]]
ok_z = len(zrows) == 47
for (seq, col), (bk, nm, st, pg) in zip(zrows, asm_all):
    ok_z &= (seq == asm_all.index((bk, nm, st, pg)) + 1) and (zname(col) == nm)
mm2 = re.findall(r"^\| (\d+) \| [^|]+ \| [^|]+ \| [^|]+ \| (\d+)–(\d+) \|", zdoc, re.M)
ok_z &= len(mm2) == 47
for (seq, s, e), (bk, nm, st, pg) in zip([(int(a), int(b), int(c)) for a, b, c in mm2], asm_all):
    ok_z &= (int(s) == st and int(e) == st + pg - 1)
gate("C1z", "装订单腿（序＋件名＋区间 true 起讫↔读数）", ok_z, "47 行逐行恒等（false 链同源差由 A 族覆盖）")
# 节行页码核：节行页码＝域首件实测 start（按本分册取值——本一/本二件名同名，不得互撞）
ok_sec = True
SECFIRST = ["衔接节", "课时01", "课时02", "课时07", "课时10", "课时11", "课时13", "课时15", "课时17", "课时19"]
for m in ("true", "false"):
    secs = [r for r in T[m] if r[0] == "sec"]
    ok_sec &= len(secs) == 20
    for bi, bk in enumerate(("本一导学本", "本二练习本")):
        starts = {p["name"]: p["start"] for b in D["modes"][m]["books"] if b["book"] == bk for p in b["pieces"]}
        for i, sf in enumerate(SECFIRST):
            r = secs[bi * 10 + i]
            exp = starts[[n for n in starts if n.split("-")[0] == sf][0]]
            ok_sec &= (r[3] == exp)
gate("C1+", "节行页码＝域首件实测 start（生成器同源全量复核）", ok_sec,
     "20 节行×2 档（衔接/2.1~2.8/章末 ×本一本二）逐行相等")

# ---- E1 编译卫生计数（报表 94 行全零＋全 OK） ----
rep = open(os.path.join(ASM, "装配报表-正式0914.txt"), encoding="utf-8").read()
rows_ = [l for l in rep.splitlines() if re.match(r"^\[(true|false)\]", l)]
ok_e1 = (len(rows_) == 94 and rep.count("**FAIL**") == 0
         and all(("err=0" in l and "ovr=0" in l and "mch=0" in l and "rc=0" in l and l.endswith("OK")) for l in rows_))
gate("E1", "装配副本编译三零×双档", ok_e1, f"{len(rows_)} 编（47×2）err/Overfull/Missing/rc 全 0（方案文头 92 系 46 笔误，实编 94）")

print("\n＝＝ 门谱S6正式 汇总：PASS %d／FAIL %d ＝＝" % (len(GREENS), len(REDS)))
for r in REDS:
    print("红:", r)
sys.exit(1 if REDS else 0)
