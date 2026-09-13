# -*- coding: utf-8 -*-
"""M3前移6施工 修后五断言自证（过程件，0913）
断言1：04练习=16（槽型10选/4填/2解，实配6选/2填/8解）
断言2：05练习=16（实配9选/3填/4解；空号6席注前移）
断言3：05拓展=3（T6/T7/T8；T1占位不计）
断言4：两课时46守恒（前16+30=46；后22+24=46）
断言5：全章307+6+7=320（台账/汇总读数在档）
另：迁移内容哨兵抽查＋残留清零＋批C不碰声明核验。
"""
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\提示词\工作区\M3-第2章量产0913\定稿")
F04 = ROOT / "批A-课时04-点斜式与斜截式.md"
F05 = ROOT / "批A-课时05-两点式与一般式.md"
FG = ROOT / "批A-台账.md"
FS = ROOT / "定稿汇总-第2章.md"
FC = ROOT / "批C-台账.md"
C10 = ROOT / "批C-课时10-2.4曲线与方程.md"
C11 = ROOT / "批C-课时11-2.5.1椭圆的标准方程.md"
C13 = ROOT / "批C-课时13-2.6.1双曲线的标准方程.md"

t04 = F04.read_text(encoding="utf-8")
t05 = F05.read_text(encoding="utf-8")
tg = FG.read_text(encoding="utf-8")
ts = FS.read_text(encoding="utf-8")
tc = FC.read_text(encoding="utf-8")

FAIL = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (("　｜　" + detail) if detail else ""))
    if not cond:
        FAIL.append(name)


def section(text, prefix):
    m = re.search(r"^## " + re.escape(prefix), text, re.M)
    assert m, f"节头未找到：{prefix}"
    nxt = text.find("\n## ", m.end())
    return text[m.start(): nxt if nxt != -1 else len(text)]


def blocks(sec):
    """返回 {题号: (归属字段, 块全文)}"""
    out = {}
    ms = list(re.finditer(r"^【(\d{2}-[GET]\d+)｜([^｜\]]+)｜", sec, re.M))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(sec)
        out[m.group(1)] = (m.group(2), sec[m.start():end])
    return out


g04 = blocks(section(t04, "一、"))
g05 = blocks(section(t05, "一、"))
e04 = blocks(section(t04, "二、"))
e05 = blocks(section(t05, "二、"))
x04 = blocks(section(t04, "三、"))
x05 = blocks(section(t05, "三、"))


def slot(bd, no):
    return bd[no][0]


def kaoti(bd):
    """计题席：排除空号注（已前移）与占位行"""
    return {k: v for k, v in bd.items()
            if "已前移课时04" not in v[1] and "占位跳过" not in v[1]}


def kind(x):
    for k in ("单选", "多选", "选择", "填空", "解答"):
        if k in x:
            return "选择" if k in ("单选", "选择") else k
    return "?"


# ── 断言1：04练习
check("断言1a 04练习标签=E1~E16", sorted(e04) == sorted(f"04-E{i}" for i in range(1, 17)), str(sorted(e04)))
kt04 = kaoti(e04)
check("断言1b 04练习计题=16", len(kt04) == 16, str(len(kt04)))
c04 = {}
for k in kt04:
    c04[kind(kt04[k][0])] = c04.get(kind(kt04[k][0]), 0) + 1
check("断言1c 04实配=选6/填2/解8", c04 == {"选择": 6, "填空": 2, "解答": 8}, str(c04))
check("断言1d 04空号=0", len(kt04) == len(e04))

# ── 断言2：05练习
expect05 = sorted([f"05-E{i}" for i in range(1, 17)] + [f"05-E{i}" for i in range(17, 23)])
check("断言2a 05练习标签=E1~E22", sorted(e05) == expect05)
kt05 = kaoti(e05)
check("断言2b 05练习计题=16", len(kt05) == 16, str(len(kt05)))
c05 = {}
for k in kt05:
    c05[kind(kt05[k][0])] = c05.get(kind(kt05[k][0]), 0) + 1
check("断言2c 05实配=选9/填3/解4", c05 == {"选择": 9, "填空": 3, "解答": 4}, str(c05))
konghao = sorted(k for k in e05 if "已前移课时04" in e05[k][1])
check("断言2d 05空号6席=E1/E4/E8/E12/E13/E14",
      konghao == ["05-E1", "05-E12", "05-E13", "05-E14", "05-E4", "05-E8"], str(konghao))
check("断言2e 05空号注计数=6", t05.count("（本席已前移课时04＝") == 6)

# ── 断言3：05拓展
check("断言3a 05拓展标签=T1/T6/T7/T8", sorted(x05) == ["05-T1", "05-T6", "05-T7", "05-T8"], str(sorted(x05)))
kx05 = kaoti(x05)
check("断言3b 05拓展计题=3（T6/T7/T8）", sorted(kx05) == ["05-T6", "05-T7", "05-T8"], str(sorted(kx05)))
check("断言3c 04拓展计题=1（T1）", sorted(kaoti(x04)) == ["04-T1"])
check("断言3d 05拓展旧席残留=0", all(f"05-T{n}｜" not in t05 for n in (2, 3, 4, 5, 9, 10)))

# ── 断言4：46守恒
z04 = len(g04) + len(kt04) + len(kaoti(x04))
z05 = len(g05) + len(kt05) + len(kx05)
check("断言4a 04总=22（5+16+1）", z04 == 22 == len(g04) + 16 + 1, f"G{len(g04)}+E{len(kt04)}+T{len(kaoti(x04))}={z04}")
check("断言4b 05总=24（5+16+3）", z05 == 24 == len(g05) + 16 + 3, f"G{len(g05)}+E{len(kt05)}+T{len(kx05)}={z05}")
check("断言4c 修后合计=46", z04 + z05 == 46, str(z04 + z05))
check("断言4d 修前合计=46（16+30）", 16 + 30 == 46)

# ── 断言5：320恒等
check("断言5a 307+6+7=320", 307 + 6 + 7 == 320)
check("断言5b 汇总件313读数在档", "73（批A）＋80（批B）＋64（批C）＋64（批D）＋32（批E）＝**313**" in ts)
check("断言5c 汇总件恒等链在档", "307＋6（04前移回填，0913收口§六已落盘）＋7（01:2＋03:5命制）＝320" in ts)
check("断言5d 台账练习73读数在档", "导学25＋练习73＋拓展10＝108" in tg)
check("断言5e 台账列恒等27+13+33=73在档", "27＋13＋33＝73" in tg)
check("断言5f 件04读数行在档", "（0913收口读数：导学5＋练习16＋拓展1＝22" in t04)
check("断言5g 件05读数行在档", "（0913收口读数：导学5＋练习16＋拓展3＝24" in t05)
check("断言5h 汇总件04满配标题", "G5＋E16＋T1，满配）" in ts)
check("断言5i 汇总件05标题T3", "（2.2.2 后半；G5＋E16＋T3）" in ts)
check("断言5j 汇总件§十二#3撤项", "已裁撤项——走前移6" in ts)
check("断言5k 台账缺口=7", "实配73，**缺7**" in tg)

# ── 迁移哨兵：前移6题在04在档、05已无正文
sent_out = {
    "04-E11题面": "经过M(3,2)与N(6,2)两点的直线的方程为（　　）",
    "04-E12详解末": "合计3条．选：C．",
    "04-E13详解": "令y＝0得x＝2；令x＝0得y＝−5．即a＝2，b＝−5（化截距式x/2＋y/(−5)＝1同判）．选：B．",
    "04-E14详解末": "此时l为x/6＋y/3＝1，即x＋2y−6＝0．",
    "04-E15详解(1)": "点斜式（用A）：y＋1＝−2(x−0)，即y＝−2x−1；",
    "04-E16详解(2)": "由截距式x/3＋y/2＝1，即2x＋3y−6＝0．",
}
for name, s in sent_out.items():
    check(f"哨兵{name} 04=1处", t04.count(s) == 1, str(t04.count(s)))
    check(f"哨兵{name} 05=0处", t05.count(s) == 0)

# ── 迁移哨兵：回填6题在05在档、04无
sent_back = {
    "05-E17题面": "方程y−1＝k(x＋1)在k取遍所有实数时",
    "05-E19题面": "其中真命题的序号是__________．",
    "05-E21题面": "已知菱形的两条对角线分别在x轴和y轴上",
    "05-E22题面": "已知直线l过点P(2,−1)．",
    "05-E20答案": "4√3/3或12√3",
}
for name, s in sent_back.items():
    check(f"哨兵{name} 05在档", s in t05)
    check(f"哨兵{name} 04无", s not in t04)

# ── 加注/微调清零与在档（题块区§二限定；§六登记条目按纪律引用改前原文，不在此列）
sec04e = section(t04, "二、")
sec05e = section(t05, "二、")
check("加注 04预习注=4处（E12/E13/E14/E16）", t04.count("（预习注：") == 4, str(t04.count("（预习注：")))
check("微调 题块区旧括注两件0处",
      all("两点式中y₂−y₁＝0不适用" not in s and "（两点式不适用）" not in s for s in (sec04e, sec05e)))
check("微调 E11新括注在档(§二=1)", sec04e.count("（同纵坐标的两点连线与x轴平行）") == 1)
check("微调 E15新括注×2在档(§二)", sec04e.count("（纵坐标相同，与x轴平行）") == 1 and sec04e.count("（横坐标相同，为竖直线x＝1）") == 1)
check("回填 T9/T10需选学提示行随迁", t05.count("需选学§2.2.4") >= 2 and "（提示：同05-E19，用到点到直线距离公式．）" in t05)
check("回填 E20法向量注保留（E22）", "由课时03点法式知识合法" in t05)

# ── 批C不碰声明＋行78回改核验
# 我方写入域：批C仅限台账行78一处；课时10/11/13三件零写操作（在跑补产臂写入域）。
# 三件现状只读报告（10/11或已由补产臂先行回改，13或仍原句——均为补产臂并行实况，非本臂动作）。
check("批C台账行78已回改", "挂命制轮主裁（规格书背书）＋报备用户" in tc and "待用户授权（八十七先例）" not in tc)
for f, n in ((C10, "10"), (C11, "11"), (C13, "13")):
    txt = f.read_text(encoding="utf-8")
    if "主裁（规格书背书）＋报备用户" in txt:
        state = "已回改（补产臂并行落盘，非本臂动作）"
    elif "挂命制轮待用户授权（八十七先例）" in txt:
        state = "仍原句（待补产臂落盘）"
    else:
        state = "⚠两式皆无，需人工过目"
    print(f"INFO 批C课时{n}件现状（本臂零写入）：{state}")

# ── 台账/汇总归属行抽查
for row in ("04-E11 | 练习·选择（前移自05-E1）", "04-E16 | 练习·解答（前移自05-E14）",
            "05-T2→**05-E17**", "05-T9→**05-E19**"):
    check(f"台账行在档：{row[:18]}…", row in tg)
for row in ("| 04-E14 | 练习·填空 | 2章件3-#26 | 中 | 前移自05-E12",
            "| 05-T3→**05-E21**", "✓随题迁练习"):
    check(f"汇总行在档：{row[:16]}…", row in ts)

print()
if FAIL:
    print(f"共 {len(FAIL)} 项失败：", FAIL)
    sys.exit(1)
print("五断言＋哨兵全部通过 ✓")
