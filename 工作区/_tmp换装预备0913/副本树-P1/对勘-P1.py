# -*- coding: utf-8 -*-
"""试迁对勘-P1（9.1电荷）：题序/题面锚序/P1特有元素/答案值/尾块，PDF 文本层机械对勘。"""
import json, os, re
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(HERE, "导学件", "9.1电荷")
ORIG = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/导学件/9.1电荷/main.pdf"

def text_of(pdf):
    doc = pymupdf.open(pdf)
    return "\n".join(p.get_text() for p in doc), len(doc)

t_orig, n_orig = text_of(ORIG)
t_true, n_true = text_of(os.path.join(PIECE, "main-换装-true.pdf"))
t_false, n_false = text_of(os.path.join(PIECE, "main-换装-false.pdf"))
print("页数: 原=%d true=%d false=%d  (false≤true: %s)" % (n_orig, n_true, n_false, n_false <= n_true))

def norm(s):
    return re.sub(r"\s+", "", s)

o, u, f = norm(t_orig), norm(t_true), norm(t_false)

# ① 题面锚序（题干/选项 distinctive 片段，件面序）
anchors = [
    "自然界中只存在两种电荷", "摩擦起电的实质是", "接触起电：两个完全相同的金属球",
    "用丝绸摩擦过的玻璃棒带正电，说明摩擦", "摩擦起电的实质是电子从一个物体",
    "取一对用绝缘支柱支持的金属导体", "感应起电的实质：", "把带正电的球C移近相互接触",
    "移走带电体后，导体上的感应电荷", "电荷守恒定律：电荷既不会", "元电荷：", "比荷：电子的电荷量与其质量之比",
    "所有带电体的电荷量都等于元电荷", "某带电体的电荷量可能是", "甲、乙、丙是三个完全相同的金属小球",
    "乙、丙相互排斥", "乙、丙也相互吸引", "甲、丙之间没有力的作用",
    "甲、乙、丙是三个用丝线悬挂的轻质小球", "丙一定带正电", "丙一定带负电", "丙一定不带电", "丙可能不带电",
    "不带电的金属导体A和B放在绝缘支柱", "移走小球C后分开导体", "移动小球C与导体", "将导体A接地后移走", "将导体B接地后移走",
    "规范答题区", "若两个完全相同的金属球分别带电荷量",
    "完全相同的金属球甲、乙，甲带电荷量", "用干燥的塑料梳子梳头后", "梳子与头发摩擦的过程中创造了电荷",
    "梳子带电后，能吸引轻小的不带电物体", "质子从头发转移到梳子上",
    "把一个带正电的金属球A", "B球靠近A的一端带正电", "B球上的自由电子向靠近A", "B球两端出现的感应电荷电性相同", "B球的电荷量因感应而变大",
    "已知元电荷", "不可能是某一带电体的电荷量", "先让甲、乙接触后再分开", "某带电体所带电荷量为",
]
def order_idx(txt):
    idx, pos = [], 0
    for a in anchors:
        i = txt.find(norm(a), pos)
        assert i >= 0, "缺锚: %s" % a
        idx.append(i); pos = i
    return idx

io, iu, if_ = order_idx(o), order_idx(u), order_idx(f)
print("题面锚: 原=%d true=%d false=%d 全中；三档沿件面锚序单调一致（题序/题面零漂移）" % (
    len(io), len(iu), len(if_)))

# ② P1 特有元素守恒（计数：true 应＝原＋预期增量〔答案块〕；false＝原恒等）
def cnt(txt, s):
    return txt.count(norm(s))
elems = [  # (元素, true 预期增量, false 预期增量)
    ("[教材链接]", 0, 0), ("[物理观念]", 0, 0), ("[科学探究]", 0, 0),
    ("[科学推理]", 0, 0), ("[科学思维]", 0, 0),
    ("[反思感悟]", 0, 0), ("规范答题区", 0, 0), ("自评项目", 0, 0),
    ("【课堂评价】", 0, 0), ("本组共5题", 0, 0), ("时间:15分钟", 0, 0),
    ("此处书写", 0, 0), ("判断正误", 0, 0),
    ("知识点一", 1, 0), ("知识点二", 1, 0), ("知识点三", 1, 0),  # ＋1＝预习填空答案块组头
]
ok = True
for e, dt, df in elems:
    a, b, c = cnt(o, e), cnt(u, e), cnt(f, e)
    good = (b == a + dt) and (c == a + df)
    if not good: ok = False
    print("  %-12s 原=%d true=%d(期%d) false=%d(期%d) %s" % (e, a, b, a + dt, c, a + df,
          "OK" if good else "漂!"))
print("P1 特有元素守恒: %s" % ("恒等（含 accounted 增量）" if ok else "有漂移!"))

# ③ 换装新增语义元素（true/false 期望计数）
for s, et, ef, desc in [("[答案]", 19, 0, "题后答案条"), ("[详解]", 2, 0, "随键详解"),
                        ("笔记与错题整理", 1, 1, "尾页填充块（\\iftailfillused 渲染面证据）")]:
    a, b, c = cnt(o, s), cnt(u, s), cnt(f, s)
    good = (b == et and c == ef)
    print("  %-10s 原=%d true=%d(期%d) false=%d(期%d)  %s  %s" % (s, a, b, et, c, ef, desc,
          "OK" if good else "异常!"))

# ④ 素养小结（讲解层开关化：原＝3\\xiaojie＋1花形副标；true 4 全守恒；false 仅花形 1）
print("  素养小结     原=%d true=%d false=%d  (true=4 守恒；false=1＝花形副标留、\\xiaojie×3 隐＝换装语义)" % (
    cnt(o, "素养小结"), cnt(u, "素养小结"), cnt(f, "素养小结")))

# ⑤ 答案值抽检（值片段；true 独有、false/原 无）
spots = ["创生", "A正／B负", "先移棒后分", "代数和正负决定", "3.0", "保持不变"]
for s in spots:
    ss = norm(s)
    a, b, c = cnt(o, ss), cnt(u, ss), cnt(f, ss)
    print("  值片 %-12s 原=%d true=%d false=%d  %s" % (s, a, b, c,
          "OK" if (b >= 1 and c == 0) else "核"))

# ⑥ 对号：log ANSKEY 键清单两档恒等
ktrue = sorted(re.findall(r"M3-ANSKEY: (.+)", open(os.path.join(PIECE, "main-换装-true.log"), encoding="utf-8", errors="ignore").read()))
kfalse = sorted(re.findall(r"M3-ANSKEY: (.+)", open(os.path.join(PIECE, "main-换装-false.log"), encoding="utf-8", errors="ignore").read()))
man = json.load(open(os.path.join(HERE, "试迁键账-9.1.json"), encoding="utf-8"))
print("对号: true=%d false=%d 清单diff=%s 与键账一致=%s" % (
    len(ktrue), len(kfalse), set(ktrue) ^ set(kfalse) or "零", set(ktrue) == set(man["键值"])))
