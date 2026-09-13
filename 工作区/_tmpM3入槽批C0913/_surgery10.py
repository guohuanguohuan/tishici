# -*- coding: utf-8 -*-
# M3 批C-课时10 入槽手术：中5~7 三块整块移拓展册（改头不改身）、简8~10 命制三块照录插入、拓1 撤位登记、区头更账
import io, sys

P = r"C:\提示词\工作区\M3-第2章量产0913\定稿\批C-课时10-2.4曲线与方程.md"
MZ = r"C:\提示词\工作区\M3-第2章量产0913\命制\轮4回修与01新命-0913.md"
HZ = r"C:\提示词\工作区\M3-第2章量产0913\定稿\定稿汇总-第2章.md"

def lines(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read().split("\n")

L = lines(P); mzl = lines(MZ); hzl = lines(HZ)

def cut(src, start_pred, end_pred):
    """return (block_lines, rest) where block = lines from first start match (exclusive of marker if marker_only) ..."""
    i = next(k for k, x in enumerate(src) if start_pred(x))
    j = next(k for k in range(i + 1, len(src)) if end_pred(src[k]))
    return src[i:j], src[:i] + src[j:]

def find(src, pred):
    return next(k for k, x in enumerate(src) if pred(x))

# --- 1. 提取命制回修版两块（10-命1改/10-命3改）：题面行起、至下一节标题前 ---
def grab_mz(head_marker):
    i = find(mzl, lambda x: x.startswith(head_marker))
    j = find(mzl[i+1:], lambda x: x.startswith("### ") or x.startswith("## ")) + i + 1
    blk = mzl[i+1:j]
    while blk and blk[0].strip() == "": blk.pop(0)
    while blk and blk[-1].strip() == "": blk.pop()
    assert blk[0].startswith("题面"), blk[0][:20]
    return blk
ming1 = grab_mz("### 10-命1（判对应辨析变式·单选·简）【改造件")
ming3 = grab_mz("### 10-命3（方程与曲线概念判断·解答·简，三小问计1）【小问(2) 已换")
# --- 汇总 10-命2（未改动席，§九原案全文） ---
i = find(hzl, lambda x: x.startswith("**10-命2（直接法基础轨迹·解答·简）**"))
j = find(hzl[i+1:], lambda x: x.startswith("**10-命3（")) + i + 1
ming2 = hzl[i+1:j]
while ming2 and ming2[-1].strip() == "": ming2.pop()
assert ming2[0].startswith("题面"), ming2[0][:20]

xin_jian = (
 ["**【10-简8｜练习·简｜命制·10-命1（轮4回修版·0913批C置换入槽）｜简·单选】**"] + ming1 +
 ["【题型】判对应辨析·定点式（同解变形判同曲线，纯粹性/完备性正用）｜【亲算】命制件§二回修版照录（内容一字未动），另经命制臂自检第二遍（逐选项异点双向验证，命制件§四表行）｜【注】与新1同考点异构（句式四选一vs四组并列、选项逐字重合清零、圆系vs绝对值根式载体，命制件§一.4差异化自证）——低注「S4隔位」＝军师案1定案。", "",
  "**【10-简9｜练习·简｜命制·10-命2（§九9.1原案照录·0913批C置换入槽）｜简】**"] + ming2 +
 ["【题型】直接法基础轨迹（距离条件·平方同解）｜【亲算】汇总§九9.1原案照录（内容一字未动）｜【注】亲算落账行末「抛物线定义相容」语系教师侧类比注（题面/详解零前引，只用两点距离公式）；S4 装配如入 2.4 当堂卷可去该注。", "",
  "**【10-简10｜练习·简｜命制·10-命3（轮4回修版·0913批C置换入槽）｜简·三小问计1】**"] + ming3 +
 ["【题型】方程与曲线概念判断（三小问计1）｜【亲算】命制件§二回修版照录（内容一字未动），另经命制臂自检第二遍（平方映射 [0,∞) 单射论证，命制件§四表行）｜【注】小问(2)已换「|x|=|y| 的轨迹方程是 y²=x²」完备正向条目——与简3（教材A③）同底层族异向，按军师案1组合乙口径「多问计1、A③＋命3＝2 合限」。", ""])

# --- 2. 从 9.3 摘出中5/6/7 三块 ---
k5 = find(L, lambda x: x.startswith("**【10-中5｜"))
k94 = find(L, lambda x: x.startswith("### 9.4"))
moved = L[k5:k94]
while moved and moved[-1].strip() == "": moved.pop()
moved.append("")
L = L[:k5] + L[k94:]
# 改头（仅头行席位标签，题面/答案/详解逐字未动）
def relabel(lines_, old_head_pred, new_head):
    for n, x in enumerate(lines_):
        if old_head_pred(x):
            lines_[n] = new_head; return
    raise AssertionError("head not found: " + new_head[:24])
relabel(moved, lambda x: x.startswith("**【10-中5｜"), "**【10-拓13｜拓展｜富矿·2章件7-#29（白名单单取·0913置换自原中5席移入）｜0.65中】**")
relabel(moved, lambda x: x.startswith("**【10-中6｜"), "**【10-拓14｜拓展｜教材·习题2-4 B⑦（0913置换自原中6席移入）｜中】**")
relabel(moved, lambda x: x.startswith("**【10-中7｜"), "**【10-拓15｜拓展｜成品②2.4.2.2-3（相关点族·0913置换自原中7席移入）｜中档】**")

# --- 3. 插入简8~10（9.3 之前、简7 块后） ---
k93 = find(L, lambda x: x.startswith("### 9.3"))
L = L[:k93] + xin_jian + L[k93:]

# --- 4. 拓1 块整体替换为撤位登记 ---
kt1 = find(L, lambda x: x.startswith("**【10-拓1｜"))
kt2 = find(L, lambda x: x.startswith("**【10-拓2｜"))
che = ["**【10-拓1｜撤位登记（原拓展席·成品②2.4.2.2-2 交叉索引席，不设题）｜0913 案2令1定性】**",
 "案2令1取证定性＝**真双列撤席让位**（非标签误登）：本席与 G5·单1 同源同题逐字（成品②2.4.2.2-2；证据两行＋改登分支穷尽排除＝过程件 `工作区/_tmpM3入槽批C0913/拓1取证.md`——dump 2.4.2.2 段仅 -2/-3 两题、-3 已位原中7〔现10-拓15〕，改登−3只会再造同题双列；成品 -1~-19 经枚举已逐题恰一席〔G5 4＋正文4＋拓展11〕，无题可改登；§7「4+3+12」之「正文3」系「正文4」之计数笔误，更正后 19 题无空位、教材第8席亦无须顶补）。",
 "本席撤：题面/答案/详解以 10-G1（9.1）唯一活位为准，不重录；域不加计（-2 经 G5单1 已计入成品19）；撤位留痕跳号照 canonical 键名总表§四.2；防双收 B22（汇总§六.4）：卷②/富矿回收侧见此题按同题对处理不再新收。§5 列头原「-2」项已同步删。", ""]
L = L[:kt1] + che + L[kt2:]

# --- 5. 拓13~15 追加至 9.6 之前 ---
k96 = find(L, lambda x: x.startswith("### 9.6"))
L = L[:k96] + moved + L[k96:]

# --- 6. 区头/计数行同步 ---
def rep(old, new):
    global L
    hits = [n for n, x in enumerate(L) if x == old]
    assert len(hits) == 1, (old[:30], len(hits))
    L[hits[0]] = new
rep("### 9.2 练习件·简单席（7题＝教材5＋成品1＋新拟1核录）",
    "### 9.2 练习件·简单席（10题＝教材5＋成品1＋新拟1核录＋命制3核录；0913 置换入槽）")
rep("### 9.3 练习件·中档席（7题＝新拟4核录＋富矿1＋教材1＋成品1）",
    "### 9.3 练习件·中档席（4题＝新拟4核录；原中5~7 三席 0913 置换移出→§9.5 拓13~15，题块整块迁出不改内容）")
rep("### 9.5 拓展册（12席，全部成品）",
    "### 9.5 拓展册（14题席＝成品12＋富矿1＋教材1；0913：拓1撤位登记〔跳号留痕〕、置换入拓13~15 三席）")
rep("## §9 补产全文区（批CA·轮4补产·2026-09-13｜净域33题逐题全文）",
    "## §9 补产全文区（批CA·轮4补产·2026-09-13｜净域33题逐题全文｜0913 批C置换入槽后重数＝净域35题区〔域36−删除1〕，更账见§9.6）")

with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(L))
print("OK 课时10 surgery; total lines:", len(L))
print("check 中5 residue:", sum(1 for x in L if x.startswith("**【10-中5")))
print("check 拓13/14/15:", sum(1 for x in L if x.startswith("**【10-拓13")) , sum(1 for x in L if x.startswith("**【10-拓14")), sum(1 for x in L if x.startswith("**【10-拓15")))
print("check 简8/9/10:", sum(1 for x in L if x.startswith("**【10-简8")), sum(1 for x in L if x.startswith("**【10-简9")), sum(1 for x in L if x.startswith("**【10-简10")))
n_jian = sum(1 for x in L if x.startswith("**【10-简"))
n_zhong = sum(1 for x in L if x.startswith("**【10-中"))
n_tuo = sum(1 for x in L if x.startswith("**【10-拓"))
print("blocks 10-jian/zhong/tuo:", n_jian, n_zhong, n_tuo)
