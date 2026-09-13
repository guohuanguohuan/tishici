# -*- coding: utf-8 -*-
"""M3 批A 命制入槽修后断言（派单施工第5条）
断言① 01 练习＝16；断言② 03 练习＝16；断言③ 批A 合计＝115；断言④ 全章 320 账读数一致。
口径：题块计数以件内题头【NN-X..｜】为准；05 六前移席（已前移课时04）与 05-T1 占位行不计题。
另核：E15/E16、E12~E16 键存在性（canonical 占位转实对合）；台账/汇总读数行抽查。零写入定稿层。"""
import io, os, re, sys

BASE = r"C:\提示词\工作区\M3-第2章量产0913"
FILES = {
    "01": r"定稿\批A-课时01-坐标法.md",
    "02": r"定稿\批A-课时02-倾斜角与斜率.md",
    "03": r"定稿\批A-课时03-方向向量与法向量.md",
    "04": r"定稿\批A-课时04-点斜式与斜截式.md",
    "05": r"定稿\批A-课时05-两点式与一般式.md",
}
HEAD = re.compile(r"【(\d\d)-([GET])([^｜]*)｜([^｜]+)｜")

fails = []
def check(name, cond, detail=""):
    print(("  [PASS] " if cond else "  [FAIL] ") + name + ("　" + detail if detail else ""))
    if not cond: fails.append(name)

practice, totals, per, e_ids = {}, {}, {}, {}
print("== 断言①②：01/03 练习题块计数 ==")
for L, fn in FILES.items():
    lines = io.open(os.path.join(BASE, fn), encoding="utf-8").read().splitlines()
    g = e = t = 0
    g_ids, e_ids[L], t_ids = [], [], []
    for i, ln in enumerate(lines):
        m = HEAD.match(ln.strip())
        if not m: continue
        body = "\n".join(lines[i+1:i+6])
        if "已前移课时04" in body or "占位跳过" in body:
            continue  # 05 六前移席／05-T1 占位行不计题
        kind = m.group(2)
        tag = m.group(1) + "-" + kind + m.group(3)
        if kind == "G": g += 1; g_ids.append(tag)
        elif kind == "E": e += 1; e_ids[L].append(tag)
        else: t += 1; t_ids.append(tag)
    practice[L], totals[L], per[L] = e, g + e + t, (g, e, t)
    print("课时%s：G%d＋E%d＋T%d＝%d" % (L, g, e, t, g + e + t))

check("01 练习＝16", practice["01"] == 16, "实数 %d" % practice["01"])
check("01 练习键恰 E1~E16", e_ids["01"] == ["01-E%d" % i for i in range(1, 17)])
check("03 练习＝16", practice["03"] == 16, "实数 %d" % practice["03"])
check("03 练习键恰 E1~E16", e_ids["03"] == ["03-E%d" % i for i in range(1, 17)])

batchA = sum(totals.values())
print("\n== 断言③：批A 合计 ==")
keys = sorted(totals)  # "01".."05"
print("五课时合计：%s＝%d（期望 115）" % ("＋".join(str(totals[L]) for L in keys), batchA))
check("批A 合计＝115", batchA == 115, "实数 %d" % batchA)
check("导学 25", sum(per[L][0] for L in per) == 25)
check("练习 80（5×16）", sum(per[L][1] for L in per) == 80)
check("拓展 10", sum(per[L][2] for L in per) == 10)

print("\n== 断言④：全章 320 账 ==")
other = 80 + 64 + 64 + 32  # 批B（4课时＋06B）＋批C（4）＋批D（4）＋批E（2）练习位恒等账
total320 = sum(per[L][1] for L in per) + other
print("练习位：批A %d＋批B 80＋批C 64＋批D 64＋批E 32＝%d（期望 320）" %
      (sum(per[L][1] for L in per), total320))
check("全章练习位＝320", total320 == 320)

print("\n== 键存在性对合（canonical 占位转实） ==")
t01 = io.open(os.path.join(BASE, FILES["01"]), encoding="utf-8").read()
t03 = io.open(os.path.join(BASE, FILES["03"]), encoding="utf-8").read()
check("01-E15 题块存在", "【01-E15｜" in t01)
check("01-E16 题块存在", "【01-E16｜" in t01)
for i in range(12, 17):
    check("03-E%d 题块存在" % i, ("【03-E%d｜" % i) in t03)
check("01/03 件内无命制占位题头", "命A｜" not in t01 and "命B｜" not in t01 and "命C｜" not in t03)
canon = io.open(os.path.join(BASE, r"成卷\题面库\canonical键名总表.md"), encoding="utf-8").read()
check("canonical 课时01 转实 E1~E16", "`2章-练-课时01-E1`~`E16`" in canon)
check("canonical 课时03 转实 E1~E16", "`2章-练-课时03-E1`~`E16`" in canon)
check("canonical 命制在途销减至 8", "10×3＋11×3＋13×2" in canon)
check("canonical 批A 读数 115", "**115** 题次" in canon)

print("\n== 账面读数行抽查（台账/汇总件） ==")
led = io.open(os.path.join(BASE, r"定稿\批A-台账.md"), encoding="utf-8").read()
summ = io.open(os.path.join(BASE, r"定稿\定稿汇总-第2章.md"), encoding="utf-8").read()
check("台账 §一 合计 115", "**115**" in led)
check("台账 §三 恒等 16＋50＋39＋8＝115", "16＋50＋39＋8＝115" in led)
check("台账 §八 来源比 16:50:8", "16:50:8" in led)
check("汇总 §二 实配 320", "＋32（批E）＝**320**" in summ)
check("汇总 §二 三轨账①轨销 307＋7＝314", "307＋7" in summ and "＝314" in summ)
check("汇总 §一.1 映射含 01-E15/E16", "| 01-E15 |" in summ and "| 01-E16 |" in summ)
check("汇总 §一.3 映射含 03-E12~E16", all(("| 03-E%d |" % i) in summ for i in range(12, 17)))
check("汇总 §九 状态转已入槽", "已入槽（13首轮＋7二轮键合覆盖）" in summ)
check("汇总 授权链注（主裁＋报备用户）", "主裁（规格书背书）＋报备用户" in summ)
check("汇总 §十三 断言二 320 全满", "80＋80＋64＋64＋32＝320" in summ)

print("\n== 结果 ==")
if fails:
    print("未过断言 %d 项：%s" % (len(fails), "；".join(fails))); sys.exit(1)
print("全部断言通过 ✓（01/03 练习各16、批A 合计115、全章练习位320、键对合与账面读数一致）")
