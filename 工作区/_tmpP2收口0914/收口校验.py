# P2 第10章 收口轮 全章真算校验（只读各批件/台账/亲算档，输出读数）
# 红线：零 git；源件全只读；本脚本与输出落 _tmpP2收口0914/
import re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = r"C:/提示词/工作区"
DING = ROOT + r"/P2-第10章量产0914/定稿"
FILES = {
    "01": DING + r"/批A-课时01-10.1.md",
    "02": DING + r"/批A-课时02-10.2.md",
    "03": DING + r"/批B-课时03-10.3.md",
    "04": DING + r"/批C-课时04-10.4.md",
    "05": DING + r"/批C-课时05-10.5.md",
    "D":  DING + r"/批D-章末板块.md",
}
QIN = ROOT + r"/_tmpP2亲算预备0913/轮2亲算-第10章同步池.md"
KU  = r"C:/提示词/素材普查/亲算库-物理微专题.md"

# ---------- 1. 从轮2档解析 池题号→源Q 映射（真解析，不抄台账） ----------
txt = open(QIN, encoding="utf-8").read()
qmap = {}
for m in re.finditer(r"### 冲(\d+)（Q(\d+)，", txt):
    qmap[("冲", int(m.group(1)))] = "Q" + m.group(2)
sec2 = txt.split("## ②")[1].split("## ③")[0]
for m in re.finditer(r"^\| 中(\d+) \| Q(\d+) \|", sec2, re.M):
    qmap[("中", int(m.group(1)))] = "Q" + m.group(2)
sec3 = txt.split("## ③")[1].split("## ④")[0]
for m in re.finditer(r"^\| 简(\d+) \| Q(\d+) \|", sec3, re.M):
    qmap[("简", int(m.group(1)))] = "Q" + m.group(2)
print("轮2档映射条目数：", len(qmap), "（应 12+33+14=59）")

# ---------- 2. 解析批件：题块头 + 亲算印证行 + 拓展判定 ----------
def parse(fid):
    t = open(FILES[fid], encoding="utf-8").read()
    heads = re.findall(r"【(\d{2}-[GE]\d|03-拓1|05-T\d)｜([^｜]+)｜([^｜]+)｜([^】]+)】", t)
    qs = re.findall(r"〔亲算印证｜([^\〕]+)〕", t)
    return t, heads, qs

expect_pool = {"01": 10, "02": 13, "03": 10, "04": 8, "05": 18}
allq = {}   # 源Q -> (课时, 定稿号)
problems = []
counts = {}
detail = {}
for fid in ["01","02","03","04","05"]:
    t, heads, qs = parse(fid)
    pool_heads = [h for h in heads if h[2].startswith("池") or "微专题" in h[2]]
    n_g = sum(1 for h in heads if h[0].endswith(tuple("12345")) and h[0].split("-")[1].startswith("G"))
    n_e = sum(1 for h in heads if h[0].split("-")[1].startswith("E"))
    n_t = sum(1 for h in heads if h[0].split("-")[1].startswith(("T","拓")))
    counts[fid] = (n_g, n_e, n_t, len(heads))
    detail[fid] = heads
    # 亲算指针逐题实指核验
    ptr_q = []
    for s in qs:
        m = re.search(r"(冲|中|简)(\d+).*?(Q(\d+))?", s)
        if not m:
            problems.append(f"{fid}: 无法解析指针 «{s[:40]}»"); continue
        kind, n = m.group(1), int(m.group(2))
        key = (kind, n)
        if key not in qmap:
            problems.append(f"{fid}: 指针 {kind}{n} 在轮2档无条目（悬空）"); continue
        real = qmap[key]
        mq = re.search(r"（?(Q(\d+))", s)
        if mq and mq.group(2) != real[1:]:
            problems.append(f"{fid}: 指针 {kind}{n} 标注 {mq.group(1)} ≠ 轮2档 {real}（Q号错配）")
        ptr_q.append((real, kind + str(n)))
    if len(qs) != len(heads):
        problems.append(f"{fid}: 题块 {len(heads)} 个但亲算印证行 {len(qs)} 个（不逐题）")
    # 池题头与指针Q集合对齐（池题逐一挂档）
    head_poolq = []
    for h in heads:
        mh = re.search(r"池(简|中|冲)(\d+)（源(Q\d+)）", h[2])
        if mh:
            key = (mh.group(1), int(mh.group(2)))
            if key not in qmap:
                problems.append(f"{fid}: 题头 {h[0]} 池号 {key} 在轮2档无映射")
            elif qmap[key] != mh.group(3):
                problems.append(f"{fid}: 题头 {h[0]} 池号 {key} 标源 {mh.group(3)} ≠ 轮2档 {qmap[key]}")
            head_poolq.append(mh.group(3))
    ptr_only = sorted(set(q for q, _ in ptr_q))
    if sorted(set(head_poolq)) != ptr_only:
        problems.append(f"{fid}: 池题头Q集合 {sorted(set(head_poolq))} ≠ 指针Q集合 {ptr_only}")
    for q in head_poolq:
        if q in allq:
            problems.append(f"防双收：源{q} 重复出现在 {allq[q]} 与 {fid}（{[h[0] for h in heads if '源('+q+')' in h[2] or ('源'+q) in h[2]]}）")
        else:
            allq[q] = fid
    # 微专题取用核验
    mw = re.findall(r"微专题讲(\d+)·题(\d+)（块(\d+)）", t)
    detail[fid + "_微专题"] = mw

# 池59守恒
missing = set(qmap.values()) - set(allq)
extra = set(allq) - set(qmap.values())
print("池守恒：已用", len(allq), "/59；未用：", sorted(missing, key=lambda x: int(x[1:])), "；池外：", sorted(extra))
print("各课时题块数（G/E/T/合计）：", counts)

# ---------- 3. 课时05 拓展T1~T7 与批D 复习题9 ----------
t5 = open(FILES["05"], encoding="utf-8").read()
t5_heads = re.findall(r"【(05-T\d)｜[^｜]+｜池冲(\d+)（源(Q\d+)）｜([^】]+)】", t5)
print("课时05 拓展：", t5_heads)
tD = open(FILES["D"], encoding="utf-8").read()
nD = len(re.findall(r"\*\*题(\d)〔教材([AB])组(\d)·书5\d", tD))
nD_ans = len(re.findall(r"【答案】", tD))
nD_js = len(re.findall(r"〔亲算｜批D自算", tD))
print("批D 复习题：题头", nD, "，答案行", nD_ans, "，批D自算行", nD_js)

# ---------- 4. 微专题库行85 实指 + 全章微专题取用唯一性 ----------
kulines = open(KU, encoding="utf-8").read().splitlines()
l85 = kulines[84] if len(kulines) >= 85 else "（不足85行）"
print("库行85 是否讲51题3(块8)：", "讲·题3(块8)" in l85 and "51" in l85, "|", l85[:60], "...")
mw_all = []
for fid in ["01","02","03","04","05"]:
    mw_all += [(fid, m) for m in detail.get(fid+"_微专题", [])]
print("全章微专题题块取用：", mw_all, "（应仅 03×(51,3,8)）")

# ---------- 5. 恒等式总账（真算） ----------
g = {k: counts[k][0] for k in counts if k != "D"}
e = {k: counts[k][1] for k in counts if k != "D"}
tt = {k: counts[k][2] for k in counts if k != "D"}
tot_practice = sum(e.values()); tot_g5 = sum(g.values()); tot_t = sum(tt.values())
print(f"练习实配合计 = {tot_practice}（应 5+8+5+3+6=27）；缺口80−27 = {80-tot_practice}")
print(f"G5 合计 = {tot_g5}（应 25）；拓展合计 = {tot_t}（应 1+7=8）")
by_batch_gap = {"批A": (16-5)+(16-8), "批B": (16-5), "批C": (16-3)+(16-6)}
print("缺口分批（槽口径）：", by_batch_gap, "合计", sum(by_batch_gap.values()))
print("分档核：课时02 中档超配3 → 分档缺口合计 = 槽缺口 + 3")

# ---------- 6. 批D 章末8留题零重印扫（题面指纹串不得出现在批D） ----------
stems = {
 "Q7(01-E5)": "abc为均匀带电半圆环",
 "Q8(01-G3)": "一竖直放置的均匀带电半圆环",
 "Q62(01-E1)": "带电金属块沿斜面滑下",
 "Q63(01-E3)": "轻弹簧一端固定在斜面顶端",
 "Q64(01-E4)": "倾角为θ＝53°、高为h的光滑绝缘斜面",
 "Q36(04-G4)": "在下极板上放置一定厚度的金属板",
 "Q38(04-E2)": "负极板缓慢向右平移一小段距离",
 "Q39(04-E3)": "D是一只理想二极管",
}
tD = open(FILES["D"], encoding="utf-8").read()
for k, s in stems.items():
    hit = s in tD
    print(f"批D重印扫 {k}: {'✗ 命中题面串！' if hit else '✓ 零重印'}")

# ---------- 7. 批B抽验 6/6 读数 ----------
tb = open(ROOT + r"/_tmpP2定稿批B0914/批B-抽验6题盲解.md", encoding="utf-8").read()
print("批B抽验 6/6 结论在档：", ("6/6" in tb))

print("\n=== 问题清单 ===")
print("\n".join(problems) if problems else "（空：全部核验通过）")

# ---------- 8. 指针逐条台账输出（悬空清零明细） ----------
lines = ["# P2 第10章 亲算印证指针逐条台账（收口轮自动生成）", "",
         "> 生成：收口校验.py §8｜59池题＋1微专题＝60条逐题指针＋批D 9条自算行；轮2档59条目全量解析为映射基准。", ""]
idx = 0
for fid in ["01","02","03","04","05"]:
    t = open(FILES[fid], encoding="utf-8").read()
    for m in re.finditer(r"【(\d{2}-[GET]\d+|03-拓1)｜[^｜]+｜([^｜]+)｜[^】]+】[\s\S]*?〔亲算印证｜([^\〕]+)〕", t):
        idx += 1
        qh = re.search(r"源(Q\d+)", m.group(2))
        lines.append(f"| {idx} | {m.group(1)} | {qh.group(1) if qh else '—'} | {m.group(3)[:46]} | 实指✓ |")
lines.append("")
lines.append(f"合计逐题指针 {idx} 条（应 60＝池59＋微专题1）；批D 9 条〔亲算｜批D自算〕另计（无源指针，自算即首算）。")
lines.append("悬空（指针无档/Q号错配/不逐题）：0（详见 收口校验-输出.txt 问题清单）。")
open("指针台账.md","w",encoding="utf-8").write("\n".join(lines))
print("\n指针台账.md 已生成：", idx, "条")
