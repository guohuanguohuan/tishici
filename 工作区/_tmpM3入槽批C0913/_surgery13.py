# -*- coding: utf-8 -*-
# M3 批C-课时13 入槽手术：中5~6 两块整块移拓展册（改头不改身）、简9~10 命制两块照录插入、区头/自查更账
# 注：本件 §9 题块头为裸【13-…】行（无 ** 包裹），匹配按 startswith("【13-")
import io

P = r"C:\提示词\工作区\M3-第2章量产0913\定稿\批C-课时13-2.6.1双曲线的标准方程.md"
MZ = r"C:\提示词\工作区\M3-第2章量产0913\命制\轮4回修与01新命-0913.md"
HZ = r"C:\提示词\工作区\M3-第2章量产0913\定稿\定稿汇总-第2章.md"

def lines(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read().split("\n")

L = lines(P); mzl = lines(MZ); hzl = lines(HZ)

def find(src, pred):
    return next(k for k, x in enumerate(src) if pred(x))

# --- 1. 提取命制两块：13-命1（汇总§九9.3原案）、13-命2改（命制件§二回修版） ---
i = find(hzl, lambda x: x.startswith("**13-命1（定义辨析变式·填空·简）**"))
j = find(hzl[i+1:], lambda x: x.startswith("**13-命2（")) + i + 1
ming1 = hzl[i+1:j]
while ming1 and ming1[-1].strip() == "": ming1.pop()
assert ming1[0].startswith("题面"), ming1[0][:20]

k = find(mzl, lambda x: x.startswith("### 13-命2（求方程基础题·解答·简）"))
m = find(mzl[k+1:], lambda x: x.startswith("### ") or x.startswith("## ")) + k + 1
ming2 = mzl[k+1:m]
while ming2 and ming2[0].strip() == "": ming2.pop(0)
while ming2 and ming2[-1].strip() == "": ming2.pop()
assert ming2[0].startswith("题面"), ming2[0][:20]

xin_jian = (
 ["【13-简9｜练习·填空｜命制·13-命1（§九9.3原案照录·0913批C置换入槽）｜简】"] + ming1 +
 ["【注】本席与 13-简1（成品卷③2.6.1.2-1 定义存在性五问说理）同属「双曲线定义辨析」组合＝2件限内，两式异：简1 多问说理（判存在并说理）、本席求方程填空（2a 与 2c 比较后直接落标准方程）；退化位辨析（差=6 两射线、差＞6 无轨迹）照原案注随行，与§0 课时口径一致。", "",
  "【13-简10｜练习·解答｜命制·13-命2改（轮4回修版照录·0913批C置换入槽）｜简】"] + ming2 +
 ["【注】轮4回修：题面「实轴长6、虚轴长8」改「2a＝6、2b＝8」并明示标准方程形如 x²/a²−y²/b²＝1（a＞0，b＞0），去除 2.6.2 术语前引，答案键不变；与 13-简4（成品卷③2.6.1.8-11 多条件组待定·多问计1）同属「求标准方程」组合＝2件限内，两式异：简4 多条件组方程、本席 2a/2b 直给落式。", ""])

# --- 2. 摘出中5/中6（至「### 四」前），改头不改身 ---
k5 = find(L, lambda x: x.startswith("【13-中5｜"))
k4 = find(L, lambda x: x.startswith("### 四、"))
moved = L[k5:k4]
while moved and moved[-1].strip() == "": moved.pop()
moved.append("")
L = L[:k5] + L[k4:]

def relabel(lines_, old_prefix, new_head):
    hit = False
    for n, x in enumerate(lines_):
        if x.startswith(old_prefix):
            assert not hit, old_prefix
            lines_[n] = new_head; hit = True
    assert hit, "head not found: " + new_head[:24]

relabel(moved, "【13-中5｜", "【13-拓5｜拓展册｜成品卷③2.6.1.7-10（0913置换自原中5席移入）｜中】")
relabel(moved, "【13-中6｜", "【13-拓6｜拓展册｜成品卷③2.6.1.9-13（0913置换自原中6席移入）｜中】")
# 块内旧席位自指（"13-中6"类）扫描——本件中5/中6 块文内无自指，断言零残留由末尾统一核

# --- 3. 插入简9~10（「### 三、」之前＝简区末） ---
k3 = find(L, lambda x: x.startswith("### 三、"))
L = L[:k3] + xin_jian + L[k3:]

# --- 4. 拓5~6 追加至「### 六、本区自查」前 ---
k6 = find(L, lambda x: x.startswith("### 六、"))
L = L[:k6] + moved + L[k6:]

# --- 5. 区头/自查行更账（精确全行替换，唯一性断言） ---
def rep(old, new):
    global L
    hits = [n for n, x in enumerate(L) if x == old]
    assert len(hits) == 1, (old[:30], len(hits))
    L[hits[0]] = new

rep("### 二、练习件·正文简单8席（13-简1~简8，照本件§3顺序）",
    "### 二、练习件·正文简单10席（13-简1~简10，照本件§3顺序；简9~10＝0913 命制置换入槽照录）")
rep("### 三、练习件·正文中档6席（13-中1~中6，照本件§3顺序）",
    "### 三、练习件·正文中档4席（13-中1~中4，照本件§3顺序；原中5~6 两席 0913 置换移出→§五 拓5~6，题块整块迁出不改内容）")
rep("### 五、拓展册4席（13-拓1~拓4，照本件§5顺序）",
    "### 五、拓展册6席（13-拓1~拓6，照本件§5顺序；拓5~6＝0913 置换移入〔原中5~6〕）")
rep("2. 净域恒等：本区题块 25＝G5 5＋正文 16＋拓展 4 ✓（`grep -c '^【13-'`＝25；正文 16＝简8＋中6＋难2 照§3席位；拓展 4 照§5席位：成品-7/-14/-16＋件8-#8）；件13 其余20题＋件10×7 未产块（批D遗留，§6 登记）。",
    "2. 净域恒等：本区题块 27＝G5 5＋正文 16＋拓展 6 ✓（`grep -c '^【13-'`＝27；正文 16＝简10＋中4＋难2 照§3席位，简9~10＝命制照录、中5~6 出块不移内容只改头；拓展 6 照§5席位：成品-7/-14/-16/-10/-13＋件8-#8）；件13 其余20题＋件10×7 未产块（批D遗留，§6 登记）。〔0913 入槽轮更账，原读数 25＝简8＋中6＋拓4 留档。〕")
def rep_sub(old_start, old_sub, new_sub):
    """行前缀唯一定位后在该行内替换子串（§六自查长行，免整行重录）"""
    global L
    hits = [n for n, x in enumerate(L) if x.startswith(old_start)]
    assert len(hits) == 1, (old_start[:30], len(hits))
    n = hits[0]
    assert L[n].count(old_sub) == 1, (old_sub[:30], L[n].count(old_sub))
    L[n] = L[n].replace(old_sub, new_sub)

rep_sub("3. 双曲线闸（本课时主闸）：", "25 个题块内", "27 个题块内")
rep_sub("4. **档位与结构**：", "本区不改表列、不补位；",
        "本区不改表列、不补位；〔0913 入槽销：简缺2 已闭（命制两题入简9~10，题文逐字照录命制件／汇总§九9.3），中溢随置换消（中6→4，溢两席移拓5~6），§8.1 已挂闭合注——本件正文满配 10/4/2。〕")

# 席位改号对照注（追加在自查区末行之后，行内旧称按此对照读；不改写历史注记原文）
klast = len(L) - 1
while klast >= 0 and L[klast].strip() == "": klast -= 1
assert L[klast].startswith("5. **图缺失**"), L[klast][:30]
L[klast+1:klast+1] = ["", "〔0913 批C置换入槽·席位改号对照〕原 **13-中5**（成品卷③2.6.1.7-10 多选）→ **13-拓5**、原 **13-中6**（成品卷③2.6.1.9-13）→ **13-拓6**（题块整块迁出，只改块头）；**13-简9**（命制13-命1）、**13-简10**（命制13-命2改）为新增席。本区以上自查与注记内的旧席位称（如「13-中5」「13-中6」）按本对照读，不回改原文。"]

with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(L))
print("OK 课时13 surgery; total lines:", len(L))
heads = [x for x in L if x.startswith("【13-")]
import collections
c = collections.Counter(x.split("｜")[0] for x in heads)
print("heads total:", len(heads))
for grp in ["简", "中", "难", "拓", "单", "填"]:
    n = sum(1 for x in heads if x.startswith("【13-" + grp))
    print(" 13-" + grp + ":", n)
print("residue 中5/中6:", sum(1 for x in L if x.startswith("【13-中5")), sum(1 for x in L if x.startswith("【13-中6")))
print("dup check:", [kk for kk, vv in c.items() if vv > 1])
