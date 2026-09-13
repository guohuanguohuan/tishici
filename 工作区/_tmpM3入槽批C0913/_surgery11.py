# -*- coding: utf-8 -*-
# M3 批C-课时11 入槽手术：中5~7 三块整块移拓展册（改头不改身）、简8~10 命制三块照录插入、拓2 撤位登记、区头/9.6更账
import io

P = r"C:\提示词\工作区\M3-第2章量产0913\定稿\批C-课时11-2.5.1椭圆的标准方程.md"
HZ = r"C:\提示词\工作区\M3-第2章量产0913\定稿\定稿汇总-第2章.md"

def lines(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read().split("\n")

L = lines(P); hzl = lines(HZ)

def find(src, pred):
    return next(k for k, x in enumerate(src) if pred(x))

# --- 1. 从汇总 §九9.2 逐字提取 11-命1/命2/命3 三块（§九头注口径：内容一字未动） ---
def grab_hz(head_marker, end_pred):
    i = find(hzl, lambda x: x.startswith(head_marker))
    j = find(hzl[i+1:], lambda x: end_pred(x)) + i + 1
    blk = hzl[i+1:j]
    while blk and blk[-1].strip() == "": blk.pop()
    assert blk[0].startswith("题面"), blk[0][:20]
    return blk

end93 = lambda x: x.startswith("### 9.3")
ming1 = grab_hz("**11-命1（定义辨析变式·填空·简）**", lambda x: x.startswith("**11-命2（"))
ming2 = grab_hz("**11-命2（焦点位置辨识·解答·简）**", lambda x: x.startswith("**11-命3（"))
ming3 = grab_hz("**11-命3（依条件求方程基础题·解答·简）**", end93)

xin_jian = (
 ["**【11-简8｜练习·简｜命制·11-命1（§九9.2原案照录·0913批C置换入槽）｜简·填空】**"] + ming1 +
 ["【题型】依定义求轨迹方程（基础位·退化情形辨析注随行）｜【亲算】汇总§九9.2原案照录（内容一字未动）｜【注】与简1（成品-22 待定系数：距离和＋通径双条件）、简10（命3 待定系数：e＋过点）判别——本席直接由定义读 a、c，不作方程组；与G5单1/单2定义辨析组合注随§7。", "",
  "**【11-简9｜练习·简｜命制·11-命2（§九9.2原案照录·0913批C置换入槽）｜简】**"] + ming2 +
 ["【题型】含参方程焦点位置辨识（逆求参数范围）｜【亲算】汇总§九9.2原案照录（内容一字未动）｜【注】本席入槽按置换律挤出原中7（成品2.5.1.6-21 三段分类，整块移11-拓17）——正文「焦点位置看大分母」组合由2件降1件（§7更账）。", "",
  "**【11-简10｜练习·简｜命制·11-命3（§九9.2原案照录·0913批C置换入槽）｜简】**"] + ming3 +
 ["【题型】依条件求标准方程（离心率＋过点·待定系数基础题）｜【亲算】汇总§九9.2原案照录（内容一字未动）｜【注】⚠「离心率」系2.5.2概念前引（与难2 -14先例同型；轮4复核未点该席，红线照录不改题面）——S4装配可换问「求a/c或(|PF₁|+|PF₂|)/|F₁F₂|之比」消前引。", ""])

# --- 2. 摘出 9.3 中5/6/7 三块（至 9.4 前），整块改头移拓展册 ---
k5 = find(L, lambda x: x.startswith("**【11-中5｜"))
k94 = find(L, lambda x: x.startswith("### 9.4"))
moved = L[k5:k94]
while moved and moved[-1].strip() == "": moved.pop()
moved.append("")
L = L[:k5] + L[k94:]

def relabel(lines_, old_head_pred, new_head):
    for n, x in enumerate(lines_):
        if old_head_pred(x):
            lines_[n] = new_head; return
    raise AssertionError("head not found: " + new_head[:24])

relabel(moved, lambda x: x.startswith("**【11-中5｜"), "**【11-拓15｜拓展｜成品②2.5.1.3.1-11（焦点三角形面积通式·0913置换自原中5席移入）｜中档】**")
relabel(moved, lambda x: x.startswith("**【11-中6｜"), "**【11-拓16｜拓展｜成品②2.5.1.4.1-13（内心模型面积法·0913置换自原中6席移入）｜中档】**")
relabel(moved, lambda x: x.startswith("**【11-中7｜"), "**【11-拓17｜拓展｜成品②2.5.1.6-21（含参三段分类·0913置换自原中7席移入）｜中档】**")

# --- 3. 插入简8~10（9.3 之前、简7 块后） ---
k93 = find(L, lambda x: x.startswith("### 9.3"))
L = L[:k93] + xin_jian + L[k93:]

# --- 4. 拓2 块整体替换为撤位登记块 ---
kt2 = find(L, lambda x: x.startswith("**【11-拓2｜"))
kt3 = find(L, lambda x: x.startswith("**【11-拓3｜"))
che = ["**【11-拓2｜撤位登记（原拓展席·成品②2.5.1.2.2-3 交叉索引席，不设题）｜0913 案2令2执行】**",
 "案2裁「撤席让位（成品版留正文）」：本席题面与 11-简7（富矿3章件3-#21）**逐字同题**（条件①②任选＋(2)问三段分类，答案全同）——实证＝`工作区/_tmpM3前置闸0913/sl-件3-21.txt`（docx对象层提取）对卷②dump L532~569 逐行比对；查重②判件3-#21为新增时漏对卷②指针（件7-#23先例同族）。",
 "本席撤：题面/答案/详解以 11-简7（9.2）唯一活位为准，不重录；域成品23→22（§1/§7更账）、拓展14→13（置换入拓15~17后再至16）；源号2.5.1.2.2-3翻归域外留档，拓2号跳号留痕照 canonical 键名总表§四.2；防双收 B21（汇总§6.4）：卷②/富矿回收侧见此题按同题对处理不再新收；原交叉索引行（简7【注】）随撤闭环为结案注。§5 列头原「-3」项已同步删。", ""]
L = L[:kt2] + che + L[kt3:]

# --- 5. 拓15~17 追加至 9.6 之前 ---
k96 = find(L, lambda x: x.startswith("### 9.6"))
L = L[:k96] + moved + L[k96:]

# --- 6. 区头/计数行同步（精确全行替换，唯一性断言） ---
def rep(old, new):
    global L
    hits = [n for n, x in enumerate(L) if x == old]
    assert len(hits) == 1, (old[:30], len(hits))
    L[hits[0]] = new

rep("### 9.2 练习件·简单席（7题）",
    "### 9.2 练习件·简单席（10题＝成品1＋富矿6＋命制3核录；0913 置换入槽，简档满配）")
rep("### 9.3 练习件·中档席（7题）",
    "### 9.3 练习件·中档席（4题＝富矿4；原中5~7 三席 0913 置换移出→§9.5 拓15~17，题块整块迁出不改内容）")
rep("### 9.5 拓展册（14席，全部成品）",
    "### 9.5 拓展册（16题席，全部成品；0913：拓2撤位登记〔跳号留痕〕、置换入拓15~17 三席）")

# --- 7. §9.6 核账行更账（行首唯一替换＋串替换） ---
def rep_prefix(old_start, new_line):
    global L
    hits = [n for n, x in enumerate(L) if x.startswith(old_start)]
    assert len(hits) == 1, (old_start[:30], len(hits))
    L[hits[0]] = new_line

rep_prefix("- 本区块数＝",
 "- 本区块数＝G5 5＋练习16（简10＋中4＋难2）＋拓展16＝**37**＝净域账37（域37，无删除）✓；另含11-拓2撤位登记块1（不设题，案2令2），不计席。全文题块实产37席，其中命制3席（简8~10）为题文逐字照录§九9.2原案（内容一字未动）。")
rep_prefix("- 源构成：",
 "- 源构成：成品照录校订22（G5 3＋正文3〔简1、难1、难2〕＋拓展16）、富矿自撰12（G5 2＋正文10：件2×10＋件3×2；题面docx对象层提取、详解亲算②为底自撰）、命制3（简8~10，§九9.2原案照录）。恒等：22＋12＋3＝37 ✓；与台账§二「课时11 正文+G5 21席＝成品6＋富矿12＋命制3」逐题对位一致，拓展16全成品另计（§5枚举）✓；成品23→22之差额＝原拓2席撤位（案2），本区已无交叉索引席、无「候裁」字样。")
rep_prefix("  ①**拓2（成品2.5.1.2.2-3）×简7",
 "  ①**拓2（成品2.5.1.2.2-3）×简7（件3-#21）逐字同题双列**（查重②判新增系漏对卷②指针，件7-#23先例同族）——**0913案2结案**：裁撤席让位（成品版留正文），原拓2交叉索引块撤登为撤位登记块，正文简7为唯一活位，域成品23→22，防双收B21（汇总§6.4）；查重总表侧判级回改挂主脑；")

# --- 8. 写回 ---
with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(L))
print("OK 课时11 surgery; total lines:", len(L))
for tag in ["**【11-中5", "**【11-中6", "**【11-中7"]:
    print("residue", tag, sum(1 for x in L if x.startswith(tag)))
for n in ["简8", "简9", "简10", "拓15", "拓16", "拓17"]:
    print("head 11-" + n, sum(1 for x in L if x.startswith("**【11-" + n + "｜")))
print("blocks 11-jian/zhong/nan/tuo/G5:",
      sum(1 for x in L if x.startswith("**【11-简")),
      sum(1 for x in L if x.startswith("**【11-中")),
      sum(1 for x in L if x.startswith("**【11-难")),
      sum(1 for x in L if x.startswith("**【11-拓")),
      sum(1 for x in L if x.startswith("**【11-G")))
