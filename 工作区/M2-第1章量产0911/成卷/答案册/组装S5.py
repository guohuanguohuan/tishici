# -*- coding: utf-8 -*-
r"""组装S5.py —— 答案册 body.tex ＋ 值快照.json 组装器（M2 轮4 成卷 S5）。

值源：导学件批1~6 值台账＋S2就绪报告附录A/B＋练习件批1~3 值台账＋拓展册值台账（主表
124 题）＋S5 缺值亲算档 35 题（拓-057 撤下后余 35，亲算 sympy 批验在案）＋卷件值台账
§一/二/三＋滚A/滚B 13~16 命制档＋题面库课时01 第11题换题注（P0 修复值）。
流程：建 631 键值表 → 分册前缀断言（check_pairs.collect_expected 子集比对）→ 钉值门
run（生效 5 门）→ 写 body.tex（每键一行 `% pair:键` 标记）→ 写 值快照.json。
跑法：python 组装S5.py
零 git；模块文件（qp-answ-*）零改动；骨架 body.tex 被本器整件替换（骨架头注口径）。
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ============================================================
# 值表：V[键] = (值串, 解析串 or None)。LaTeX 串；向量缩写 \ov{X}（body 头局部定义）。
# ============================================================
V = {}


def put(key, val, note=None):
    assert key not in V, '重复键：%s' % key
    V[key] = (val, note)


# ------------------------------------------------------------
# 【甲】导学件（10 课时：预习填空聚合槽＋判1~5＋探K-例1/变式N＋评1~5；衔接29；章末28）
# ------------------------------------------------------------

# ---- 课时01（批1值台账 §1.3/1.4）----
put('导-课时01-预习填空',
    r'知识点一：大小、方向；长度；零；0、\(\overrightarrow{0}\)、1、相反、平行、重合、模相等。'
    r'知识点二：三角形、平行四边形；相同；相反；唯一。知识点三：同一平面；不共线。')
for i, v in enumerate(['×', '√', '×', '√', '×'], 1):
    put('导-课时01-判%d' % i, v)
put('导-课时01-探1-例1', 'B')
put('导-课时01-探1-变式1', 'D')
put('导-课时01-探2-例1', r'\(\overrightarrow{b}-\overrightarrow{a}-\overrightarrow{c}\)')
put('导-课时01-探2-变式1', r'\(\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\)')
put('导-课时01-探3-例1', r'\(x=1\)，\(y=\dfrac{1}{4}\)')
put('导-课时01-探3-变式1', r'\(x=1\)，\(y=\dfrac{1}{2}\)')
put('导-课时01-探4-例1', r'C（①③）')
put('导-课时01-探4-变式1', '共面')
put('导-课时01-评1', 'C')
put('导-课时01-评2', r'B（2）')
put('导-课时01-评3', r'D（\(\overrightarrow{EF}\)）')
put('导-课时01-评4', r'\(-\overrightarrow{a}+\dfrac{1}{2}\overrightarrow{b}+\dfrac{1}{2}\overrightarrow{c}\)')
put('导-课时01-评5', '3')

# ---- 课时02（S2就绪报告 附录A/B；v11 冻结域同文）----
put('导-课时02-预习填空',
    r'知识点一：\(0^{\circ}\le\langle\overrightarrow{a},\overrightarrow{b}\rangle\le180^{\circ}\)；垂直。'
    r'知识点二：零向量；\(\overrightarrow{b}\cdot\overrightarrow{a}\)；\(\lambda\)；'
    r'\(\overrightarrow{a}\cdot\overrightarrow{c}+\overrightarrow{b}\cdot\overrightarrow{c}\)。知识点三：无空。')
put('导-课时02-判1', '×')
put('导-课时02-判2', '×')
put('导-课时02-判3', '×')
put('导-课时02-判4', '×')
put('导-课时02-判5', r'×\quad (6)√')      # 件内 6 判折叠：判5 承 (5)×＋(6)√——2026-09-12 S7收尾批：去「知识点三」行文，六槽干净（值序列 ×××××√ 不变；body.tex L67 同步）
put('导-课时02-探1-例1', 'AD')
put('导-课时02-探1-变式1', r'\(-11\)')
put('导-课时02-探2-例1', r'\(60^{\circ}\)')
put('导-课时02-探2-变式1', r'\(\dfrac{\sqrt{10}}{5}\)')
put('导-课时02-探3-例1', r'\((-1-\sqrt{3},\,-1+\sqrt{3})\)')
put('导-课时02-探3-变式1', r'\(-\dfrac{3}{2}\)')
put('导-课时02-探4-例1', 'D')
put('导-课时02-探4-变式1', r'\(\sqrt{2}\)')
put('导-课时02-探5-例1', 'A')
put('导-课时02-探5-变式1', r'\(\dfrac{\sqrt{7}}{2}\)')   # 钉-1（v11 P0 勘误钉值）
put('导-课时02-评1', r'A（\(-1\)）')                      # 以下评1~5：S2就绪报告 附录A 亲算档
put('导-课时02-评2', 'C（充要）')
put('导-课时02-评3', r'C（\(60^{\circ}\)）')
put('导-课时02-评4', '2')
put('导-课时02-评5', '0')

# ---- 课时03（批1值台账 §2.4/2.5）----
put('导-课时03-预习填空',
    r'知识点一：不共面；唯一；基底；基向量；两个不共线；三个不共面。'
    r'知识点二：两两互相垂直；1；两两垂直。知识点三：同一平面；1。')
for i, v in enumerate(['√', '×', '√', '×', '√'], 1):
    put('导-课时03-判%d' % i, v)
put('导-课时03-探1-例1', 'D')
put('导-课时03-探1-变式1', 'A')
put('导-课时03-探2-例1', 'BC')
put('导-课时03-探2-变式1', r'\(x=-\dfrac{1}{2}\)')
put('导-课时03-探3-例1', r'(1)证明见解析；(2)\(x+y+z=\dfrac{1}{3}\)')
put('导-课时03-探3-变式1', r'\(-\dfrac{1}{6}\)')
put('导-课时03-探4-例1', 'B',
    r'C 项所涉夹角 \(\cos\langle\overrightarrow{B_{1}C},\overrightarrow{AA_{1}}\rangle=-\dfrac{1}{2}\)'
    r'，夹角恰 \(120^{\circ}\)；'
    r'C 项不正确系另有错点，故选 B。')  # 义2-1已撤销／钉-3；目验修红0913：解析剥内部过程语（日期串/逻辑闸/S2改字义务/亲算·盲解·numpy·三重验证/讲部详解/键B指称），键值与数学量（cos −1/2、120°、选B）零改动
put('导-课时03-探4-变式1', '3')
put('导-课时03-评1', 'B')
put('导-课时03-评2', 'C')
put('导-课时03-评3', 'B')
put('导-课时03-评4', r'\(m=2\)，\(n=4\)')
put('导-课时03-评5', r'\(-2\)')

# ---- 课时04（批2值台账 §1.3/1.4；变式2×2 落探一/探三）----
put('导-课时04-预习填空',
    r'知识点一：单位正交基底；空间直角坐标系 \(Oxyz\)；原点；坐标向量；坐标平面；八；'
    r'\(135^{\circ}\)（或 \(45^{\circ}\)）；\(90^{\circ}\)；\(x\) 轴正方向；\(y\) 轴正方向；\(z\) 轴正方向。'
    r'知识点二：有序实数组 \((x,y,z)\)；\(A(x,y,z)\)；横坐标；唯一；\(\overrightarrow{a}=(x,y,z)\)。'
    r'知识点三：\((a_{1}+b_{1},a_{2}+b_{2},a_{3}+b_{3})\)；\((a_{1}-b_{1},a_{2}-b_{2},a_{3}-b_{3})\)；'
    r'\((\lambda a_{1},\lambda a_{2},\lambda a_{3})\)；\(a_{1}b_{1}+a_{2}b_{2}+a_{3}b_{3}\)；'
    r'\(\sqrt{(a_{2}-a_{1})^{2}+(b_{2}-b_{1})^{2}+(c_{2}-c_{1})^{2}}\)；'
    r'\(\left(\dfrac{x_{1}+x_{2}}{2},\dfrac{y_{1}+y_{2}}{2},\dfrac{z_{1}+z_{2}}{2}\right)\)。')
for i, v in enumerate(['√', '×', '√', '×', '√'], 1):
    put('导-课时04-判%d' % i, v)
put('导-课时04-探1-例1',
    r'\(A(0,0,0)\)，\(B(2,0,0)\)，\(C(0,2,0)\)，\(P(0,0,3)\)；'
    r'\(Q\left(0,1,\dfrac{3}{2}\right)\)；\(M\left(0,t,3-\dfrac{3}{2}t\right)\)（\(0\le t\le 2\)）')
put('导-课时04-探1-变式1', r'\(C_{1}(2,3,2)\)；\(M\left(1,\dfrac{3}{2},1\right)\)')
put('导-课时04-探1-变式2',
    r'\(A(0,0,0)\)，\(B(2,0,0)\)，\(C(2,2,0)\)，\(D(0,2,0)\)，\(P(0,0,2)\)')
put('导-课时04-探2-例1', r'C（\(\overrightarrow{BC}=(0,-4,-2)\)）')
put('导-课时04-探2-变式1', r'\(P_{1}(-2,-1,3)\)；\(P_{2}(2,1,-3)\)')
put('导-课时04-探3-例1', r'A（\(\sqrt{3}\)）')
put('导-课时04-探3-变式1', r'\(M(1,3,2)\)；\(|OM|=\sqrt{14}\)')
put('导-课时04-探3-变式2', r'距离 \(2\)；\(\sqrt{5}\)')
put('导-课时04-评1', 'A')
put('导-课时04-评2', r'C（\(2\sqrt{3}\)）')
put('导-课时04-评3', r'C（\(yOz\) 坐标平面内）')
put('导-课时04-评4', r'\((-1,2,3)\)')
put('导-课时04-评5', r'\(2\sqrt{2}\)')

# ---- 课时05（批2值台账 §2.4/2.5）----
put('导-课时05-预习填空',
    r'知识点一：\(\lambda b_{1}\)；\(\lambda b_{2}\)；\(\lambda b_{3}\)；\(a_{1}b_{1}+a_{2}b_{2}+a_{3}b_{3}=0\)。'
    r'知识点二：\(\sqrt{a_{1}^{2}+a_{2}^{2}+a_{3}^{2}}\)；\(\dfrac{\overrightarrow{a}\cdot\overrightarrow{b}}{|\overrightarrow{a}||\overrightarrow{b}|}\)；'
    r'\(\dfrac{\overrightarrow{a}\cdot\overrightarrow{b}}{|\overrightarrow{b}|}\)。'
    r'知识点三：\(1-\lambda\)；\(\overrightarrow{DC}\)；互相平分。')  # 2026-09-12 S7收尾批：课05预习填空 同步快照（AD→DC）
for i, v in enumerate(['√', '×', '√', '×', '√'], 1):
    put('导-课时05-判%d' % i, v)
put('导-课时05-探1-例1', r'\((2,-2,4)\) 或 \((-2,2,-4)\)')
put('导-课时05-探1-变式1', r'\(\left(\dfrac{2}{3},\dfrac{1}{3},-\dfrac{2}{3}\right)\)')
put('导-课时05-探2-例1', r'B（\(-\dfrac{\sqrt{6}}{6}\)）')
put('导-课时05-探2-变式1', r'\(\dfrac{\sqrt{2}}{2}\)')
put('导-课时05-探3-例1', r'(1)\(x=6\)，\(y=\dfrac{15}{2}\)；(2)\((x,y)=(-4,2)\) 或 \(\left(\dfrac{116}{41},-\dfrac{142}{41}\right)\)')
put('导-课时05-探3-变式1', r'\(\overrightarrow{n}=(1,-1,1)\)（不唯一）')
put('导-课时05-探4-例1', r'(1)\(|PM|=\dfrac{2\sqrt{13}}{3}\)；(2)最小值 \(\dfrac{\sqrt{6}}{4}\)')
put('导-课时05-探4-变式1', r'\(P(2,2,0)\)；\(|OP|=2\sqrt{2}\)')
put('导-课时05-探5-例1', r'(1)\([0,3,5]\)；(2)①\([-2,2,\dfrac{3}{2}]\)；②\(t=-2\)，\(|AM|=2\)')
put('导-课时05-探5-变式1', r'\(\overrightarrow{a}\cdot\overrightarrow{b}=\dfrac{5}{2}\)；\(|\overrightarrow{a}+\overrightarrow{b}|=\sqrt{11}\)')
put('导-课时05-评1', 'A')
put('导-课时05-评2', r'B（\(3\sqrt{2}\)）')
put('导-课时05-评3', r'A（\((3,2,4)\)）')
put('导-课时05-评4', r'\(\dfrac{1}{2}\)')
put('导-课时05-评5', r'\(m=-2\)')

# ---- 课时06（批3值台账 §1.4/1.5）----
put('导-课时06-预习填空',
    r'知识点一：\(\overrightarrow{OP}\)；非零；平行；\(\overrightarrow{OA}+t\overrightarrow{a}\)。'
    r'知识点二：\(\lambda\overrightarrow{u_{2}}\)；\(\overrightarrow{u_{1}}\cdot\overrightarrow{u_{2}}=0\)。'
    r'知识点三：\(0^{\circ}\le\theta\le90^{\circ}\)；'
    r'\(\left|\cos\langle\overrightarrow{v_{1}},\overrightarrow{v_{2}}\rangle\right|\)。')
for i, v in enumerate(['×', '√', '×', '√', '×'], 1):
    put('导-课时06-判%d' % i, v)
put('导-课时06-探1-例1', '证明见解析')
put('导-课时06-探1-变式1', r'C（\((-1,0,2)\)）')
put('导-课时06-探2-例1', r'A（\(30^{\circ}\)）')
put('导-课时06-探2-变式1', r'B（\(\dfrac{\sqrt{2}}{4}\)）',
    r'题设「\(\triangle ABC\) 为等边三角形」，结果 \(\dfrac{\sqrt{2}}{4}\)。')  # 义2-2；2026-09-13 修红2：值尾补全角 ）（原 \) 收束不印字）；目验修红0913：剥「首句按题面改／讲部详解误作」过程语，值不动
put('导-课时06-探3-例1', r'\(\dfrac{\pi}{4}\)；\(\dfrac{\sqrt{2}}{2}a\)')
put('导-课时06-探3-变式1', r'\(\dfrac{5}{6}\)')
put('导-课时06-探4-例1', r'\(M\) 在线段 \(FH\) 上（答案不唯一）')
put('导-课时06-探4-变式1', r'\(DM\perp PC\)（或 \(BM\perp PC\)）')
put('导-课时06-探5-例1', 'AD')
put('导-课时06-探5-变式1', 'AC')
put('导-课时06-评1', 'A')
put('导-课时06-评2', r'C（\(60^{\circ}\)）')
put('导-课时06-评3', r'C（充要）')
put('导-课时06-评4', r'\(-\dfrac{\sqrt{3}}{3}\)；\(\dfrac{\sqrt{3}}{3}\)')
put('导-课时06-评5', r'\((5,-1,5)\) 或 \((-3,3,-3)\)（写一个即可）')  # 2026-09-12 S7收尾批：同步快照新值（末点 −1→−3）

# ---- 课时07（批4值台账 §1.4/1.5）----
put('导-课时07-预习填空',
    r'知识点一：①\(\overrightarrow{OA}+x\overrightarrow{AB}+y\overrightarrow{AC}\)；②法向量、\(\overrightarrow{AP}\)；③平行。'
    r'知识点二：①\(\overrightarrow{u}\cdot\overrightarrow{n}=0\)；②\(\overrightarrow{n_{1}}\parallel\overrightarrow{n_{2}}\)；'
    r'③存在 \(\lambda\in\mathbb{R}\) 使 \(\overrightarrow{u}=\lambda\overrightarrow{n}\)；④\(\overrightarrow{n_{1}}\cdot\overrightarrow{n_{2}}=0\)。'
    r'知识点三：①射影、斜线；③公共部分。')
for i, v in enumerate(['×', '×', '×', '√', '√'], 1):
    put('导-课时07-判%d' % i, v)
put('导-课时07-探1-例1', 'A')
put('导-课时07-探1-变式1', 'A')
put('导-课时07-探2-例1', '(1)(2)证明见解析')
put('导-课时07-探2-变式1', '证明见解析',
    r'两面法向量均 \((1,1,-1)\)（共线），且验证 \(A\) 不在面 \(BC_{1}D\) 内——两平面不重合，故平行。')
put('导-课时07-探3-例1', r'(1)存在；(2)不存在')
put('导-课时07-探3-变式1', '不存在')
put('导-课时07-探4-例1', 'ABC（选错误项）')
put('导-课时07-探4-变式1', 'AD')
put('导-课时07-探5-例1', 'B')
put('导-课时07-探5-变式1', 'D')
put('导-课时07-评1', r'A（\(l\perp\alpha\)）')
put('导-课时07-评2', r'C（相交但不垂直）')
put('导-课时07-评3', r'B（直角梯形）')
put('导-课时07-评4', r'\(d=-3\)')
put('导-课时07-评5', r'\(m=0\)')

# ---- 课时08（批4值台账 §2.4/2.5）----
put('导-课时08-预习填空',
    r'知识点一：\(90^{\circ}\)；\(0^{\circ}\)；\(\angle ABA^{\prime}\)；\([0^{\circ},90^{\circ}]\)；所有直线；\(AB\cos\theta\)。'
    r'知识点二：\(\sin\langle\overrightarrow{v},\overrightarrow{n}\rangle\)；'
    r'\(\left|\cos\langle\overrightarrow{v},\overrightarrow{n}\rangle\right|\)。'
    r'知识点三：\(\cos\angle AOB\cdot\cos\angle BOC\)。')
for i, v in enumerate(['×', '×', '×', '√', '√'], 1):
    put('导-课时08-判%d' % i, v)
put('导-课时08-探1-例1', r'\(\dfrac{\sqrt{3}}{3}\)')
put('导-课时08-探1-变式1', r'\(45^{\circ}\)')
put('导-课时08-探2-例1', r'①\(\lambda=\dfrac{1}{2}\) 或 \(1\)；②③不存在')
put('导-课时08-探2-变式1', r'A（\(30^{\circ}\)）')
put('导-课时08-探3-例1', r'\(45^{\circ}\)')
put('导-课时08-探3-变式1', r'(1)证明见解析；(2)\(\dfrac{\sqrt{7}}{7}\)')
put('导-课时08-探4-例1', r'\(\sqrt{2}\)')
put('导-课时08-探4-变式1', r'\(\left(\dfrac{1}{2},1\right)\)')
put('导-课时08-探5-例1', r'(1)证明见解析；(2)最大值 \(\dfrac{\sqrt{6}}{3}\)')
put('导-课时08-探5-变式1', r'\([45^{\circ},90^{\circ}]\)')
put('导-课时08-评1', r'C（\([0^{\circ},90^{\circ}]\)）')
put('导-课时08-评2', 'A')
put('导-课时08-评3', r'C（\(60^{\circ}\)）')
put('导-课时08-评4', '无数')
put('导-课时08-评5', r'\(\dfrac{4}{9}\)')

# ---- 课时09（批5值台账 §1.3/1.4）----
put('导-课时09-预习填空',
    r'知识点一：两个半平面；棱。知识点二：任一（棱上）；与棱垂直；\([0^{\circ},180^{\circ}]\)。'
    r'知识点三：\(\dfrac{\overrightarrow{n_{1}}\cdot\overrightarrow{n_{2}}}{|\overrightarrow{n_{1}}||\overrightarrow{n_{2}}|}\)；相等；'
    r'\(\dfrac{S^{\prime}}{S}\)；\(\dfrac{\cos\gamma-\cos\alpha\cos\beta}{\sin\alpha\sin\beta}\)；\(\cos\alpha\cos\beta\)。')
for i, v in enumerate(['×', '√', '×', '√', '√'], 1):
    put('导-课时09-判%d' % i, v)
put('导-课时09-探1-例1', r'\(-\dfrac{\sqrt{3}}{3}\)',
    r'\(\angle APD=90^{\circ}\)（\(\angle ADP=45^{\circ}\)，故 \(PD\perp PA\)）。')  # 义2-3；目验修红0913：剥「实算/结论仍真」对账语
put('导-课时09-探1-变式1', r'\(\dfrac{2\sqrt{7}}{7}\)',
    r'求的是平面 \(FAD\) 与平面 \(ADC\) 的夹角。')  # 义2-4；目验修红0913：剥「与字两处按源件勘正」括注
put('导-课时09-探2-例1', r'(1)\(\sqrt{2}\)；(2)\(\dfrac{\sqrt{3}}{2}\)',
    '方程组法独立可解（叉乘法从略）。')  # 义2-5；目验修红0913：剥「删法一仅留法二与题后反思」编辑过程语
put('导-课时09-探2-变式1', r'\(\dfrac{6\sqrt{13}}{13}\)')
put('导-课时09-探3-例1', r'\(-\dfrac{\sqrt{5}}{5}\)')
put('导-课时09-探3-变式1', r'\(120^{\circ}\)')
put('导-课时09-探4-例1', r'\(\dfrac{\sqrt{6}}{4}\)',
    '空间余弦定理先证后用（建系可另证）。')  # 义2-6；目验修红0913：剥「注记随册」
put('导-课时09-探4-变式1', r'\(\dfrac{\sqrt{2}}{4}\)')
put('导-课时09-探5-例1', r'\(\dfrac{\sqrt{3}}{3}\)')
put('导-课时09-探5-变式1', r'\(\sqrt{6}\)')
put('导-课时09-评1', 'B')
put('导-课时09-评2', 'C')
put('导-课时09-评3', 'A')
put('导-课时09-评4', '1')
put('导-课时09-评5', r'\(\dfrac{\sqrt{3}}{3}\)')

# ---- 课时10（批5值台账 §2.3/2.4）----
put('导-课时10-预习填空',
    r'知识点一：\(\overrightarrow{AP}\cdot\overrightarrow{u}\)；\(\dfrac{\overrightarrow{AP}\cdot\overrightarrow{u}}{|\overrightarrow{u}|}\)；'
    r'\(\dfrac{|\overrightarrow{AB}\cdot\overrightarrow{n}|}{|\overrightarrow{n}|}\)。'
    r'知识点二：\(m\)；任一点；任一点；垂直；相交。知识点三：\(\dfrac{3V}{S}\)；\(\dfrac{\sqrt{6}a}{3}\)；\(\dfrac{\sqrt{6}a}{12}\)；\(3:1\)。')
for i, v in enumerate(['×', '√', '√', '×', '×'], 1):
    put('导-课时10-判%d' % i, v)
put('导-课时10-探1-例1', r'B（\(d=2\)）')
put('导-课时10-探1-变式1', r'\(\dfrac{8}{3}\)')
put('导-课时10-探2-例1', r'(1)\(4\)；(2)\(\sqrt{3}\)')
put('导-课时10-探2-变式1', r'\(\sqrt{6}\)')
put('导-课时10-探3-例1', r'(1)\(\dfrac{2\sqrt{5}}{5}\)；(2)\(\sqrt{2}\)',
    r'\(AB\parallel DC\)，\(DC\subset\) 平面 \(EFCD\)；点到面 \(EFCD\) 的距离。')  # 义2-7；目验修红0913：剥「源详解衍字已正」
put('导-课时10-探3-变式1', r'\(\dfrac{5}{3}\)')
put('导-课时10-探4-例1', r'C（\(5\sqrt{2}\)）')
put('导-课时10-探4-变式1', r'\(\sqrt{2}\)')
put('导-课时10-探5-例1', r'\(\dfrac{\sqrt{6}a}{12}\)')
put('导-课时10-探5-变式1', r'C（\(\dfrac{1}{4}\)）')
put('导-课时10-评1', 'A')
put('导-课时10-评2', 'A')
put('导-课时10-评3', 'B')
put('导-课时10-评4', r'\(\dfrac{3\sqrt{2}}{2}\)')
put('导-课时10-评5', r'\(\dfrac{3-\sqrt{3}}{3}\)')

# ---- 衔接 29 题（批3值台账 §2.3 全表；义2-19~22 随行落墨）----
XJ = [
    (r'\(\dfrac{3}{7}\)', None),
    (r'\(1:3\)', None),
    (r'\(\dfrac{2}{3}\)', None),
    (r'\(1:4\)', None),
    (r'证明见解析', r'\(\angle OAB=\angle ODC\)＋对顶角 \(\Rightarrow\triangle OAB\sim\triangle ODC\) '
     r'\(\Rightarrow OA:OD=OB:OC\Rightarrow\triangle OAD\sim\triangle OBC\Rightarrow\angle DAC=\angle CBD\)。'),
    (r'\(\dfrac{4}{5}\)；\(\dfrac{16}{9}\)', None),
    (r'(1)\(30^{\circ}\)；(2)\(8\sqrt{3}\)', None),
    (r'B（\(6\)）', None),
    (r'\(816/25\)', None),   # 钉-5（源同值两制留分数一制，小数版注销）
    (r'(1)\(20\)，\(12\)，\(16\) cm；(2)\(\dfrac{36}{5}\)，\(\dfrac{64}{5}\) cm', None),
    (r'证明见解析', r'双射影：\(AE\cdot AB=AD^{2}=AF\cdot AC\)；(2) 共角夹边成比例逆相似。'),
    (r'证明见解析', r'内角平分线定理：过 \(C\) 作平行线法（面积法同源）。'),
    (r'\(\dfrac{35}{9}\)', None),
    (r'证明见解析', r'外角平分线定理；合比定理：\(BD:DC=AB:AC\Rightarrow BD:(BD+DC)=AB:(AB+AC)\)。'),  # 义2-21；目验修红0913：「合比一步补足」改学生语「合比定理」
    (r'\(\dfrac{55}{3}\)', None),
    (r'证明见解析', r'重心三等分（向量/中位线双链）；取 \(AC\) 中点。'),  # 义2-22；目验修红0913：剥「源详解…应作 AC」括注
    (r'证明见解析', r'双高 \(\Rightarrow H\)、\(D\)、\(C\)、\(E\) 与 \(A\)、\(B\)、\(D\)、\(E\) 两组四点共圆，转角即得 \(CH\) 延长线\(\perp AB\)。'),
    (r'(1)\(\angle BPC=90^{\circ}+\dfrac{1}{2}\angle BAC\)；(2)\(\angle BOC=2\angle BAC\)；(3)\(4\angle BPC-\angle BOC=360^{\circ}\)', None),
    (r'证明见解析', r'切线长相等三元一次 \(\Rightarrow AE=AF=\dfrac{b+c-a}{2}\)。'),
    (r'\(r=\dfrac{2S}{a+b+c}\)', None),
    (r'证明见解析', r'重心＝内心 \(\Rightarrow\) 中线即角平分线 \(\Rightarrow\) 逐向等腰 \(\Rightarrow\) 等边。'),
    (r'(1)\(S=2\sqrt{2}\)，\(BE=\dfrac{4\sqrt{2}}{3}\)；(2)\(r=\dfrac{\sqrt{2}}{2}\)；(3)\(R=\dfrac{9\sqrt{2}}{8}\)',
     r'(2) 即用衔接-20 公式；(3) \(R=\dfrac{abc}{4S}\)。'),  # 义2-19；目验修红0913：剥「答案栏按详解栏重建」对账语
    (r'\(\sqrt{5}\)', None),
    (r'\(20\sqrt{3}\)', None),
    (r'\(45^{\circ}\)', r'\(AH=2R|\cos A|=BC=2R\sin A\)（\(A\) 钝）\(\Rightarrow A=135^{\circ}\Rightarrow\angle BHC=180^{\circ}-A\)。'),  # 义2-20；目验修红0913：剥「源同值两制留一制」对账尾注
    (r'\(75^{\circ}\)', None),
    (r'\(\sqrt{6}\)', None),
    (r'证明见解析', r'垂心＝重心 \(\Rightarrow\) 中线\(\perp\)对边 \(\Rightarrow\) 等腰循环 \(\Rightarrow\) 正三角形。'),
    (r'证明见解析', r'五点共圆链；定值 (1)\(120^{\circ}\) (2)\(240^{\circ}\)（\(A=60^{\circ}\) 条件下）。'),
]
for i, (v, n) in enumerate(XJ, 1):
    put('导-衔接-%d' % i, v, n)

# ---- 章末 28 题（批6值台账 §一表＋高考题组）----
put('导-章末-例1', 'B（仅②真）')
put('导-章末-变式1', 'C（③④）')
put('导-章末-例2', r'(1)\(90^{\circ}\)；(2)\(45^{\circ}\)')
put('导-章末-变式2', r'(1)\(\pi\)；(2)\(\dfrac{\pi}{3}\)；(3)\(\dfrac{2\pi}{3}\)；(4)\(\dfrac{\pi}{2}\)')
put('导-章末-例3', r'ABC（\(D\) 支 \(D=b^{2}\) 恒正）')
put('导-章末-变式3', r'最小值 \(-\dfrac{3}{2}\)；\(P\) 为高线 \(AM\) 中点（\(M\) 为 \(BC\) 中点）')
put('导-章末-例4', 'C（①②真③假）')
put('导-章末-变式4', '证明见解析')
put('导-章末-例5', '④（逐条对称律验）')
put('导-章末-变式5',
    r'\(A_{1}(-1,-2,0)\)，\(B_{1}(3,-1,-2)\)，\(C_{1}(4,1,-1)\)，\(D_{1}(0,0,1)\)')
put('导-章末-例6', r'(1)\(\dfrac{1}{2}\)；(2)\(\dfrac{\sqrt{6}}{3}\)')
put('导-章末-变式6', r'(1)\(\sqrt{3}\)；(2)\(a=1\)，\(\cos=\dfrac{1}{6}\)')
put('导-章末-例7', r'\(m=-2\)')
put('导-章末-变式7', r'C（\(x+y=-4\)）')
put('导-章末-例8', r'B（\(\lambda=2\)）')
put('导-章末-变式8', r'存在；\(|MN|=\dfrac{\sqrt{6}}{3}\)',
    r'\(D\) 原点系 \(D(0,0,0)\)，\(A(2,0,0)\)，\(B(2,2,0)\)，\(D_{1}(0,0,1)\)：\(M\left(\dfrac{2}{3},0,\dfrac{2}{3}\right)\)，'
    r'\(N\left(\dfrac{1}{3},\dfrac{1}{3},0\right)\)。')
put('导-章末-例9', 'D')
put('导-章末-变式9', 'AD')
put('导-章末-例10', r'(1)\(3\sqrt{3}\)；(2)\(5\sqrt{2}\)')
put('导-章末-变式10', r'\(\dfrac{2\sqrt{30}}{15}\)')
put('导-章末-例11', r'\(\dfrac{3\sqrt{3}}{2}\)')
put('导-章末-变式11', r'(1)\(\dfrac{3}{2}\)；(2)\(-\dfrac{2\sqrt{7}}{7}\)')
put('导-章末-例12', r'A（\(\dfrac{2\sqrt{2}}{3}\)）')
put('导-章末-变式12', 'BC')
put('导-章末-高考1', r'\(P\) 为 \(CC_{1}\) 中点（答案不唯一，开放条件填充）')
put('导-章末-高考2', r'①\(\Leftrightarrow\)③（①作条件③作结论、③\(\Rightarrow\)①亦可；②不能作条件也不能作结论）')
put('导-章末-高考3', r'(1)证明见解析；(2)\(\dfrac{2}{3}\)（①②两路同值）')
put('导-章末-高考4', r'(1)证明见解析；(2)存在，\(\dfrac{PM}{PD}=\dfrac{1}{3}\)')

# ------------------------------------------------------------
# 【乙】练习件（10 课时×16 题；批1~3 值台账 §一值表；义2-8~2-18 随行落墨）
# ------------------------------------------------------------
LX = {
'01': [
 ('C', None),
 (r'\(\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\)', None),
 (r'\(x=1\)，\(y=\dfrac{1}{2}\)', None),
 (r'\(-11\)', None),
 (r'\(\dfrac{\sqrt{10}}{5}\)', r'\(C\) 在底面！\(AB_{1}=(2,0,1)\)、\(AC=(2,2,0)\)，\(\cos=\dfrac{4}{\sqrt{5}\cdot 2\sqrt{2}}=\dfrac{\sqrt{10}}{5}\)。'),
 (r'\(\overrightarrow{b}-\overrightarrow{a}-\overrightarrow{c}\)', None),
 ('共面', r'\(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\) 系数和 \(3+(-2)=1\)。'),
 (r'\(\sqrt{2}\)', None),
 ('AD', None),
 (r'\(\dfrac{\sqrt{7}}{2}\)', None),   # 钉-2（答案册 v1 旧键 √13/2 修键）
 (r'(1)\(2\overrightarrow{AG}\)；(2)\(\overrightarrow{MD}\)', None),   # P0 换题值（题面库换题注亲算）
 ('A', r'\(AB\) 与 \(A_{1}C_{1}\) 成 \(45^{\circ}\)；B \(135^{\circ}\)、C \(90^{\circ}\)、D \(180^{\circ}\) 逐项坐标验。'),
 (r'\(\overrightarrow{MN}=-\dfrac{1}{2}\overrightarrow{a}+\dfrac{1}{2}\overrightarrow{c}\)',
  r'\(=\dfrac{1}{2}(\overrightarrow{BB_{1}}+\overrightarrow{A_{1}D_{1}})\)。'),
 ('证明见解析', r'\(MN\parallel BD\) 且 \(MN=\dfrac{1}{2}BD\)（中位线）。'),
 (r'(1)\(\dfrac{a^{2}}{2}\)；(2)\(-\dfrac{a^{2}}{2}\)；(3)\(-\dfrac{a^{2}}{2}\)；(4)\(\dfrac{a^{2}}{4}\)；(5)\(-\dfrac{a^{2}}{4}\)；(6)\(\dfrac{a^{2}}{4}\)', None),
 (r'最小值 \(-\dfrac{3}{2}\)；\(P\) 为高线 \(AM\) 中点', r'\(f=2\left[x^{2}+y^{2}-\sqrt{3}y\right]\) 配方。'),
],
'02': [
 ('B（仅②真）', None),
 ('C（③④）', None),
 ('B（平行四边形）', None),
 (r'\(\overrightarrow{0}\)', None),
 (r'\(\dfrac{5}{6}\overrightarrow{a}+\dfrac{9}{2}\overrightarrow{b}-\dfrac{7}{6}\overrightarrow{c}\)', None),
 (r'(1)共面；(2)共面；(3)不共面', None),
 (r'(1)\(90^{\circ}\)；(2)\(45^{\circ}\)', None),
 (r'\(\dfrac{3\pi}{4}\)', None),
 (r'B（\(-\overrightarrow{a}+\overrightarrow{b}+\overrightarrow{c}\)）', None),
 (r'A（\(A\)、\(B\)、\(D\)）', None),
 (r'C（\(1\)）', None),
 (r'D（\(0\)）', None),
 ('ABC', None),
 (r'(1)\(\pi\)；(2)\(\dfrac{\pi}{3}\)；(3)\(\dfrac{2\pi}{3}\)；(4)\(\dfrac{\pi}{2}\)', None),
 (r'(1)\(\lambda=\dfrac{3}{4}\)，\(h=2\)；(2)\(\dfrac{3\sqrt{5}}{25}\)',
  r'\(1+h^{2}(1-\lambda)=0\) 与 \(1+h^{2}(1-\lambda)^{2}=\dfrac{5}{4}\) 联立 \(\Rightarrow h^{2}=4\)、\(\lambda=\dfrac{3}{4}\)。'),
 (r'(1)证明 \(\overrightarrow{PB}+2\overrightarrow{PC}=3\overrightarrow{PM}\)；(2)最小值 \(-\dfrac{5}{3}\)，\(P\) 为 \(AM\) 中点',
  r'\(M\) 定点，系数和 \(1+2=3\)。'),
],
'03': [
 ('D', None),
 ('C（2 个真）', None),
 ('ABC', None),
 ('BC', None),
 (r'B（\(\dfrac{1}{2}\overrightarrow{a}-\overrightarrow{b}+\dfrac{1}{2}\overrightarrow{c}\)）', None),
 (r'C（\((3,1,3)\)）', None),
 (r'\(x=1\)，\(y=-3\)', None),
 (r'\(x=3\)，\(y=-2\)，\(z=1\)', None),
 (r'\(\overrightarrow{OE}=\dfrac{1}{2}\overrightarrow{a}+\dfrac{1}{4}\overrightarrow{b}+\dfrac{1}{4}\overrightarrow{c}\)', None),
 (r'(1)证明 \(A\)、\(E\)、\(C_{1}\)、\(F\) 共面；(2)\(x+y+z=\dfrac{1}{3}\)', None),
 (r'\(\lambda=\dfrac{65}{7}\)', None),
 (r'\(\overrightarrow{PG}=\dfrac{1}{3}\overrightarrow{i}+\dfrac{2}{3}\overrightarrow{j}-\dfrac{2}{3}\overrightarrow{k}\)；'
  r'\(\overrightarrow{BG}=-\dfrac{2}{3}\overrightarrow{i}+\dfrac{2}{3}\overrightarrow{j}+\dfrac{1}{3}\overrightarrow{k}\)；'
  r'\(\overrightarrow{AG}=\dfrac{1}{3}\overrightarrow{i}+\dfrac{2}{3}\overrightarrow{j}+\dfrac{1}{3}\overrightarrow{k}\)', None),
 (r'B（\(AC_{1}\cdot BD=0\) 恒）', None),
 ('证明见解析', r'\(EF\parallel B_{1}D_{1}\parallel BD\)，故共面。'),
 (r'共面（\(\overrightarrow{p}-\overrightarrow{q}=\overrightarrow{b}-\overrightarrow{c}=\overrightarrow{r}\)）', None),
 ('充要条件证明', None),
],
'04': [
 (r'(1)\((-1,1,-2)\)；(2)\((1,-1,0)\)；(3)\((0,2,3)\)', None),
 (r'(1)\((-8,8,4)\)；(2)\((-6,-9,-2)\)', None),  # 2026-09-12 S7收尾批：练04-2 同步快照新值（−6→−8）
 (r'(1)\((1,1,-1)\)；(2)\((1,1,1)\)', None),
 (r'\(\left(2,3,\dfrac{7}{2}\right)\)', None),
 (r'\(|OM|=\sqrt{x^{2}+y^{2}+z^{2}}\)', None),
 (r'(1)\((13,-4,3)\)；(2)\(7\)；(3)\(-121\)', None),
 (r'C（\((0,-4,-2)\)）', None),
 ('④（仅④真）', None),
 ('开放题（常见建系位逐顶点坐标）', None),
 (r'D（\(\left(2,2,\dfrac{4}{3}\right)\)）', None),  # 2026-09-12 S7收尾批：练04-10 同步快照新值（C·2/3→D·4/3）
 (r'(1)\(A(0,0,0)\)，\(B(2,0,0)\)，\(C(0,2,0)\)，\(P(0,0,3)\)；(2)\(Q\left(0,1,\dfrac{3}{2}\right)\)；'
  r'(3)\(M\left(0,t,3-\dfrac{3}{2}t\right)\)，\(t\in[0,2]\)', None),
 (r'A（\((1,1,1)\)）', None),
 (r'\(A_{1}(-1,-2,0)\)，\(B_{1}(3,-1,-2)\)，\(C_{1}(4,1,-1)\)，\(D_{1}(0,0,1)\)', None),  # 2026-09-12 S7收尾批：练04-13 同步快照新值（四点对位重排）
 (r'①\(\Leftrightarrow\)③（②不作条件，不作结论）', None),
 (r'(1)\((x-2)^{2}+(y-2)^{2}=4\)（\(m=12\)），圆，长 \(4\pi\)；(2)\(m=12\) 或 \(16\)；(3)\(|PB_{1}|\in\{4,\ 4\sqrt{2},\ 4\sqrt{3}\}\)', None),  # 2026-09-12 S7收尾批：练04-15(3) 同步快照新值（区间→三值集）
 (r'(1)\(-1\)；(2)\(t=0\) 或 \(-2\)；(3)\(t=0\)：\(45^{\circ}\)；\(t=-2\)：\(135^{\circ}\)', None),
],
'05': [
 (r'(1)(2) 均平行', None),
 (r'(1)(2) 均垂直', None),
 (r'\((2,-2,4)\) 或 \((-2,2,-4)\)', None),
 (r'C\(\left(\dfrac{5}{3},2,-4\right)\)', None),
 (r'D\((5,13,-3)\)', None),
 (r'\(m=-2\)', None),
 (r'C（\(-4\)）', None),
 (r'(1)\(\dfrac{1}{2}\)；(2)\(\dfrac{\sqrt{6}}{3}\)', None),
 (r'\(\overrightarrow{n}=\lambda(1,1,1)\)（\(\lambda\neq 0\)）', None),
 (r'\(\dfrac{17\sqrt{29}}{29}\)', None),
 (r'(1)\(\sqrt{3}\)；(2)\(a=1\)，\(\cos=\dfrac{1}{6}\)', None),
 (r'(1)\(\dfrac{2\sqrt{13}}{3}\)；(2)\(\dfrac{\sqrt{6}}{4}\)', None),
 (r'(1)\(x=6\)，\(y=\dfrac{15}{2}\)；(2)\((-4,2)\) 或 \(\left(\dfrac{116}{41},-\dfrac{142}{41}\right)\)', None),
 (r'(1)\([0,3,5]\)；①\(\left[-2,2,\dfrac{3}{2}\right]\)；②\(|AM|=2\)', None),
 (r'(1)\(m=\pm 1\)；(2)不存在；(3)\(\left[-\dfrac{2}{5},\dfrac{2}{5}\right)\)', None),
 (r'(1)\((1-\lambda)^{2}+\mu^{2}=\dfrac{1}{4}\)，\(\lambda\in\left[\dfrac{1}{2},1\right]\)；(2)\([-2\sqrt{2},-2]\)', None),
],
'06': [
 ('A', None),
 (r'\((1,-1,0)\) 的任一非零倍数', None),
 (r'(1)(2) 均平行', None),
 (r'B（\(\lambda=2\)）', None),
 (r'B（\(m=2\)）', None),
 (r'C\((9,12,10)\)', None),
 (r'C\((-1,0,2)\)', None),
 (r'\(90^{\circ}\)', None),
 (r'(1)\(BC\)、\(CD\)、\(B^{\prime}C^{\prime}\)、\(C^{\prime}D^{\prime}\)；(2)\(60^{\circ}\)／\(150^{\circ}\)／\(90^{\circ}\)', None),  # 2026-09-12 S7收尾批：练06-9 同步快照新值（120°→150°）
 (r'证明见解析（\(\overrightarrow{MN}=\dfrac{1}{2}\overrightarrow{B_{1}C}\)）',
  r'正方形对角线互相平分——中点 \(M\)、\(N\) 为对角线交点链。'),  # 义2-9；目验修红0913：剥「【知识点】按向量口径重标」
 (r'(1)(2) 证明见解析', None),
 (r'B（\(\dfrac{\sqrt{2}}{4}\)）',
  r'\(\cos\langle\overrightarrow{PD},\overrightarrow{AC}\rangle=\dfrac{|\overrightarrow{PD}\cdot\overrightarrow{AC}|}{|\overrightarrow{PD}||\overrightarrow{AC}|}=\dfrac{\sqrt{2}}{4}\)。'),  # 义2-8；目验修红0913：「等号后补分隔」排版注记改算式连写（√2/4 与分式值零改动）
 (r'\(45^{\circ}\)、\(\dfrac{\sqrt{2}}{2}a\)',
  r'\(\cos\langle\overrightarrow{EF},\overrightarrow{AB}\rangle=\dfrac{\overrightarrow{EF}\cdot\overrightarrow{AB}}{|\overrightarrow{EF}||\overrightarrow{AB}|}\)。'),  # 义2-8；目验修红0913：剥「（补分隔）」
 (r'\(M\) 在线段 \(FH\) 上（例 \(M=F\)，答案不唯一）', None),
 ('AD', None),
 (r'存在：\(\overrightarrow{AM}=\dfrac{2}{3}\overrightarrow{AD_{1}}\)、\(\overrightarrow{BN}=\dfrac{5}{6}\overrightarrow{BD}\)，\(|MN|=\dfrac{\sqrt{6}}{3}\)', None),
],
'07': [
 (r'A\((-1,2,-1)\)', None),
 (r'A\((2,3,3)\)', None),
 ('D', None),
 ('AD', None),
 ('A（平行）', None),
 (r'(1)(2) 均 \(\alpha\parallel\beta\)', None),
 ('垂直', None),
 (r'\(-3\)', None),
 (r'\(P\) 为 \(CC_{1}\) 中点（答案不唯一）', None),
 ('证明见解析', r'末句 \(DB\cap DM=D\)。'),  # 义2-10；目验修红0913：剥「源详解…勘正」，正确式原样保留
 (r'(1)(2) 证明见解析',
  r'法向量共线 \(\Rightarrow\) 平行或重合；又两平面不重合，故平行。'),  # 义2-11；目验修红0913：「补完备句」编辑语改为正文句
 (r'(1)存在，\(PE=\dfrac{a^{2}+c^{2}}{2a^{2}+c^{2}}PC\)；(2)不存在', None),
 (r'D（\(\left(0,\dfrac{2}{3}\right]\)）', None),
 (r'B（\(2\) 个）', r'④按相似比讲解。'),  # 义2-12；目验修红0913：剥「维持…口径」
 (r'(1)(2) 证明见解析', None),
 (r'(1)证明见解析；(2)\(V=\dfrac{8}{3}\)', None),
],
'08': [
 (r'(1)\(3\sqrt{3}\)；(2)\(5\sqrt{2}\)', None),
 (r'\(\langle\overrightarrow{v_{1}},\overrightarrow{v_{2}}\rangle=\theta\) 或 \(\pi-\theta\)，即 \(\cos\theta=\left|\cos\langle\overrightarrow{v_{1}},\overrightarrow{v_{2}}\rangle\right|\)', None),
 (r'(1)\(60^{\circ}\)；(2)\(45^{\circ}\)；(3)\(0^{\circ}\)；(4)\(90^{\circ}\)', None),
 (r'\(45^{\circ}\)', None),
 (r'\(\dfrac{\sqrt{3}}{3}\)', None),
 (r'\(\dfrac{2\sqrt{30}}{15}\)', None),
 (r'选①：\(\lambda=\dfrac{1}{2}\) 或 \(1\)；选②③：\(\lambda\) 不存在', None),
 (r'(1)证明见解析；(2)\(\dfrac{\sqrt{7}}{7}\)',
  r'二面角定义法可行。'),  # 义2-13；目验修红0913：剥「前序合法（基准表第18行判例）」门档语
 (r'(1)证明见解析；(2)\(\dfrac{2}{3}\)（选①②同值）', None),
 (r'(1)证明见解析；(2)最大值 \(\dfrac{\sqrt{6}}{3}\)',
  r'方法二「平面 \(QDC\)」。'),  # 义2-14；目验修红0913：剥「源详解勘正；值无误」
 (r'\(BC=\sqrt{100-24\sqrt{3}}\) 或 \(\sqrt{100+24\sqrt{3}}\) cm', None),
 (r'A（\(\angle PCA\)）', None),
 (r'\(30^{\circ}\)', None),
 (r'C（\(60^{\circ}\)）', None),
 (r'\(\dfrac{2}{3}\)', None),
 (r'(1)\(C(2,2,0)\)、\(P(0,0,2)\)；(2)\(\dfrac{\sqrt{3}}{3}\)', None),
],

'09': [
 (r'\(\dfrac{3\sqrt{3}}{2}\)', None),
 (r'\(7\sqrt{2}\)', None),
 (r'(1)证明见解析；(2)\(\dfrac{2\sqrt{7}}{7}\)', None),
 (r'(1)证明见解析；(2)\(-\dfrac{\sqrt{3}}{3}\)', None),
 (r'(1)证明见解析；(2)\(\dfrac{2\sqrt{5}}{5}\)', None),
 (r'(1)证明见解析；(2)存在，\(\dfrac{PM}{PD}=\dfrac{1}{3}\)', None),
 (r'(1)\(\dfrac{3}{2}\)；(2)\(-\dfrac{2\sqrt{7}}{7}\)',
  r'(2) 钝制 \(-\dfrac{2\sqrt{7}}{7}\)（取锐 \(\dfrac{2\sqrt{7}}{7}\)，两制并存）。'),  # 义6-4/钉-7 随册口径；目验修红0913：剥「印／两制并存挂账——教材PDF无答案栏／钉-7保持待钉并呈报」过程语，钝制·取锐两值原样保留
 (r'(1)证明见解析；(2)\(30^{\circ}\)；(3)\(SE:EC=2:1\)', None),
 (r'C（\(MP\perp l\) 且 \(NP\perp l\)）', None),
 (r'\(90^{\circ}\)', None),
 ('5', None),
 (r'C（\(60^{\circ}\)）', None),
 ('12', None),
 (r'\(60^{\circ}\)', None),
 (r'(1)证明见解析；(2)\(30^{\circ}\)', None),
 (r'B（\(45^{\circ}\)）', None),
],
'10': [
 (r'B（d=2）', None),
 (r'C（\(\dfrac{1}{3}\)）', r'\(ACD_{1}\) 面 \(x-2y+2z=0\)，\(d=\dfrac{1}{3}\)。'),  # 目验修红0913：剥「y轴两处按源件勘正」
 (r'A（\(\dfrac{2\sqrt{2}}{3}\)）', r'\(|\overrightarrow{BA}\times\overrightarrow{BC}|=2\sqrt{2}\)、\(|BC|=3\)；向量坐标不加模线。'),  # 目验修红0913：剥「（源详解勘正）」，书写规范句保留
 (r'\(\dfrac{2\sqrt{3}}{3}\) cm', None),
 (r'\(\dfrac{2\sqrt{3}}{3}\)', None),
 (r'(1)\(\dfrac{\sqrt{3}}{3}\)；(2)\(\dfrac{\sqrt{3}}{3}\)', None),
 (r'\(\dfrac{\sqrt{6}a}{12}\)', None),
 (r'C（\(\dfrac{1}{4}\)）', None),
 (r'(1)\(4\)；(2)\(\sqrt{3}\)', None),
 (r'(1)\(\dfrac{2\sqrt{5}}{5}\)；(2)\(\sqrt{2}\)', None),
 (r'C（\(5\sqrt{2}\)）', None),
 ('BC', r'D 项 \(\dfrac{5}{6}\)（嵌套绝对值与括号易错）。'),  # 目验修红0913：剥「应为／源详解…错位勘正」，5/6 与易错点保留
 (r'(1)\(\dfrac{5\sqrt{34}}{34}\)；(2)\(0\)；(3)\(\dfrac{4}{5}\)', None),
 (r'\(\dfrac{\sqrt{2}}{6}\)', None),
 ('A（2）', None),
 (r'\(\sqrt{3}\)',
  r'应为连线段 CP（\(\overrightarrow{CP}=(1,1,1)\parallel\overrightarrow{n}\) 实为垂线段），且垂足恰为 C，\(d=|PC|=\sqrt{3}\) 第二路可验。'),
],
}
for hh in sorted(LX):
    for i, (v, n) in enumerate(LX[hh], 1):
        put('练-课时%s-%d' % (hh, i), v, n)

# ------------------------------------------------------------
# 【丙】拓展册（拓-001~160，跳 057；有值 124 题转录自 拓展册/值台账.md 主表，
#   缺值 35 题亲算值入册；义5-1 口径，057 撤下＝义A-1/钉-6）
# ------------------------------------------------------------
TUO = {
'001': ('C（①②③⑤假；④真）', None),  # 2026-09-12 S7收尾批：同步快照新值（真假位重判，原「①③⑤真；②④假」）
'002': ('D', None),
'003': (r'A（\(4\ov{PG}\)）', None),
'004': (r'(1)\(0\)；(2)\(1\)；(3)\(1\)；(4)\(-1\)', None),
'005': (r'\(-2\)', None),
'006': (r'\(\sqrt{3}\)', None),
'007': (r'\(\sqrt{13}\)', None),
'008': (r'D（\(\arccos\dfrac{1}{4}\approx 75.5^{\circ}\)，非特殊角）', None),
'009': (r'\(0\)', None),  # 2026-09-12 S7收尾批：同步快照新值（1→0）
'010': (r'B（\(k=2\)）', None),
'011': (r'C（系数和 \(11-6-4=1\)，\(M\in\) 平面 \(BA_{1}D_{1}\)）', None),
'012': (r'(1)(2)证明见解析；(3)\(\ov{OM}=\dfrac{1}{4}(\ov{OA}+\ov{OB}+\ov{OC}+\ov{OD})\)', None),
'013': (r'\(\ov{OG}=\dfrac{1}{6}\ov{a}+\dfrac{1}{3}\ov{b}+\dfrac{1}{3}\ov{c}\)', None),
'014': (r'共面（\(\ov{c}=-2\ov{a}+\ov{b}\)）', None),
'015': (r'A（\(\ov{AM}\cdot\ov{MN}=-\dfrac{4}{3}\)）', None),
'016': ('一定共面', None),
'017': (r'\(\ov{OC}\)', None),
'018': (r'\(F(0,0,0)\)、\(A(0,4,0)\)、\(B(-3,0,0)\)、\(C(3,0,0)\)、'
        r'\(A_{1}(0,4,5)\)、\(B_{1}(-3,0,5)\)、\(C_{1}(3,0,5)\)、\(E(3,0,\dfrac{5}{2})\)', None),
'019': (r'\((\pm\dfrac{1}{2},\pm\dfrac{1}{2},\pm\dfrac{1}{2})\)（8 个顶点取遍正负号组合）', None),
'020': (r'\(P\left(\dfrac{2}{3},\dfrac{2}{3},\dfrac{1}{3}\right)\)（\(D\) 为原点系）', None),
'021': (r'A（\(P(1,1,-1)\)，\(|\ov{OP}|=\sqrt{3}\)）', None),
'022': (r'D（\(2\sqrt{14}\)；\(A^{\prime}(3,3,-1)\)）', None),
'023': (r'(1)\(9\)；(2)\(-454\)', None),
'024': (r'\(|\ov{a}+\ov{b}|^{2}=307\)，\(|\ov{a}-\ov{b}|^{2}=107\)', None),
'025': (r'\(\lambda=3\)（\(-2\) 由 \(\lambda>0\) 舍）', None),
'026': (r'(1)\(0^{\circ}\)；(2)\(180^{\circ}\)；(3)\(90^{\circ}\)；(4)\(60^{\circ}\)；'
        r'(5)\(150^{\circ}\)；(6)\(45^{\circ}\)', None),
'027': (r'B（\(\lambda=-\dfrac{\sqrt{6}}{6}\)）', None),
'028': (r'(1)证明见解析；(2)\(\dfrac{\sqrt{30}}{15}\)；(3)\(\dfrac{\sqrt{22}}{3}\)', None),
'029': (r'\(xy=-16\)', None),
'030': (r'B（\(x=\dfrac{1}{2}\)，\(y=-4\)）', None),
'031': (r'\(\left(\dfrac{3}{2},\dfrac{3}{2},\dfrac{3\sqrt{2}}{2}\right)\)', None),
'032': (r'(1)\(60^{\circ}\)；(2)\(\dfrac{\sqrt{2}}{2}\)', None),
'033': (r'(1)\(\left(\dfrac{2}{\sqrt{38}},-\dfrac{3}{\sqrt{38}},\dfrac{5}{\sqrt{38}}\right)\)；'
        r'(2)\(\left(0,-\dfrac{3}{5},\dfrac{4}{5}\right)\)', None),
'034': (r'A（\(\left[\dfrac{\sqrt{6}}{2},\sqrt{2}\right]\)）', None),
'035': (r'\(k=\dfrac{7}{5}\)', None),
'036': (r'\(D(2,0,5)\)', None),
'037': (r'存在，\(x=-\dfrac{86}{51}\)', None),
'038': (r'A（\(30^{\circ}\)）', None),
'039': (r'(1)\(\sqrt{2}\)；(2)\(\dfrac{\sqrt{14}}{7}\)', None),
'040': (r'C（\(\dfrac{\sqrt{3}}{3}\)）', None),
'041': (r'\(\ov{DM}\perp\ov{PC}\)（或 \(\ov{BM}\perp\ov{PC}\)）', None),
'042': ('证明见解析', None),
'043': ('ABC（错误结论为 A、B、C）', None),
'044': (r'(1)证明见解析；(2)存在，\(\ov{DG}=2\ov{GB}\)', None),
'045': ('BC', None),
'046': ('证明见解析', None),
'047': ('证明见解析', None),
'048': ('ACD', None),
'049': (r'(1)证明见解析（\(n=(0,2,1)\)）；(2)\(\dfrac{\sqrt{5}}{5}\)', None),
'050': (r'\(\ov{BN}/\ov{NC}=1\)，轨迹长 \(6\)（答案不唯一，\(k=2\) 时长 \(4\) 亦可）', None),
'051': (r'\(45^{\circ}\)', None),
'052': (r'\(\sqrt{2}\)', None),
'053': (r'\(\left(\dfrac{1}{4},\dfrac{1}{2}\right)\)', None),  # 2026-09-12 S7收尾批：同步快照新值（½→¼）
'054': (r'(1)证明见解析；(2)\(\dfrac{9}{13}\)', None),
'055': (r'三面所成角均为 \(\arccos\dfrac{\sqrt{6}}{3}\)（余弦值均 \(\dfrac{\sqrt{6}}{3}\)）', None),
'056': (r'\(45^{\circ}\)', None),
'058': (r'\(\dfrac{\sqrt{3}}{3}\)', None),
'059': (r'(1)\(\sqrt{2}\)；(2)\(\dfrac{\sqrt{3}}{2}\)', None),
'060': (r'(1)证明见解析；(2)\(\dfrac{\sqrt{5}}{5}\)', None),
'061': (r'(1)证明见解析；(2)\(\dfrac{11}{13}\)', None),
'062': (r'(1)证明见解析；(2)\(\dfrac{1}{3}\)；(3)\(\dfrac{\pi}{4}\)', None),
'063': (r'(1)\(D\) 为棱 \(CC_{1}\) 的中点（\(CD=2\)）；(2)\(\dfrac{\pi}{4}\)', None),
'064': (r'(1)证明见解析；(2)\(\dfrac{\pi}{2}\)', None),
'065': (r'(1)证明见解析；(2)①\(\dfrac{1}{3}\)；②\(\dfrac{\sqrt{6}}{3}\)', None),
'066': (r'\(\dfrac{\sqrt{6}}{4}\)', None),
'067': (r'\(-\dfrac{\sqrt{5}}{5}\)', None),
'068': (r'(a)\(\dfrac{1}{3}\)；(b)\(\left(\dfrac{\sqrt{10}}{10},\dfrac{\sqrt{2}}{2}\right)\)', None),
'069': (r'(1)证明见解析；(2)\(\dfrac{\sqrt{3}}{3}\)', None),
'070': (r'(1)证明见解析；(2)\(\dfrac{\sqrt{111}}{8}\)；(3)\(\dfrac{5\sqrt{37}}{37}\)', None),
'071': (r'(1)证明见解析；(2)\(\dfrac{\sqrt{6}}{3}\)', None),
'072': ('BD', None),
'073': (r'(1)证明见解析；(2)三支均证出', None),
'074': (r'(1)证明见解析；(2)①\(\dfrac{2\sqrt{7}}{7}\)；②\(-\dfrac{2\sqrt{19}}{19}\)；③\(\dfrac{2\sqrt{51}}{17}\)', None),
'075': (r'(1)证明见解析；(2)选①③或②③；(3)\(\dfrac{\sqrt{10}}{10}\)', None),
'076': (r'(1)证明见解析；(2)三支同答 \(\dfrac{4\sqrt{53}}{53}\)', None),
'077': (r'(1)\(\dfrac{1}{3}\)；(2)不存在', None),
'078': (r'(1)证明见解析；(2)存在，\(M\) 为棱 \(SA\) 上靠近 \(A\) 的三等分点'
        r'（\(\ov{AM}=\dfrac{1}{3}\ov{AS}\)）', None),
'079': (r'与 \(yOz\) 面 \(\dfrac{6}{7}\)、\(zOx\) 面 \(\dfrac{3}{7}\)、\(xOy\) 面 \(\dfrac{2}{7}\)', None),
'080': (r'\(\dfrac{\sqrt{6}}{4}a\)', None),
'081': (r'A（\(36\pi\)）', None),
'082': (r'C（\(\sqrt{2}\)）', None),
'083': (r'D（\(\dfrac{3\sqrt{2}}{2}\)）', None),
'084': (r'\(\dfrac{3}{2}+\dfrac{\sqrt{6}}{6}\)', None),
'085': (r'\(\dfrac{4\sqrt{3}}{3}\)', None),
'086': (r'\(\sqrt{6}\pi\)', None),
'087': (r'C（\(\dfrac{5\pi}{2}\)）', None),
'088': (r'\(2\sqrt{2}\)', None),
'089': (r'D（\(1\)）', None),
'090': (r'\(\dfrac{32\pi}{3}\)', None),
'091': (r'\(4\)', None),
'092': (r'A（\(25\pi\)）', None),
'093': (r'\(36\pi-16\sqrt{2}\pi\)', None),
'094': (r'D（\(\dfrac{20\pi}{3}\)）', None),
'095': (r'\(\dfrac{28\pi}{3}\)', None),
'096': (r'D（\(112\pi\)）', None),
'097': (r'D（\(\dfrac{52\pi}{3}\)）', None),
'098': (r'\(2\sqrt{2}-2\)；\(\dfrac{3}{2}\)', None),
'099': (r'\(32\sqrt{3}\pi\)', None),
'100': (r'C（\((3-2\sqrt{2})\pi\)）', None),
'101': (r'\(\dfrac{6\sqrt{3}}{\pi}\)', None),
'102': (r'\(8\pi\)', None),
'103': (r'C（\(\dfrac{2\pi}{3}\)）', None),
'104': (r'D（\(\dfrac{9}{4}\)）', None),
'105': (r'\((2-\sqrt{2})a\)', None),
'106': (r'\(6\sqrt{3}\)', None),
'107': (r'A（\(\dfrac{\sqrt{3}}{2}\pi\)）', None),
'108': (r'C（\(\dfrac{\sqrt{6}}{12}\)）', None),
'109': ('ABC', None),
'110': (r'B（\(\dfrac{4}{3}\)）', None),
'111': (r'\(4\)', None),
'112': (r'\(2\sqrt{6}\)', None),
'113': (r'\(\left[0,\dfrac{4}{3}\right]\)', None),
'114': (r'B（\(4\sqrt{6}\)）', None),
'115': (r'A（\(\sqrt{2}\)）', None),
'116': (r'B（\(\sqrt{2}\)）', None),
'117': (r'B（\(6\pi\)）', None),
'118': (r'A（\(2:1\)）', None),
'119': (r'\(12\sqrt{3}\)', None),
'120': (r'A（\(81\pi\)）', None),
'121': (r'A（\(\dfrac{13\pi}{6}\)）', None),
'122': (r'C（\(2\pi\)）', None),
'123': (r'D（\(\left[\dfrac{16\pi}{9},3\pi\right]\)）', None),
'124': (r'B（\(\left[\dfrac{8\pi}{9},\dfrac{3\pi}{2}\right]\)）', None),
'125': (r'\(\dfrac{7\pi}{3}\)', None),
'126': (r'\(4\sqrt{3}\pi\)；\(2\sqrt{2}\pi\)', None),
'127': (r'\(\sqrt{5}\)；\(\dfrac{65\sqrt{10}\pi}{3}\)', None),
'128': (r'D（\(4\)）', None),
'129': (r'A（\(12+4\sqrt{3}\)）', None),
'130': (r'A（\(\dfrac{1}{4}\)）', None),
'131': ('BC', None),
'132': (r'\(2\sqrt{3}\)', None),
'133': (r'\(\dfrac{\sqrt{13}}{2}\)', None),
'134': (r'\(11\)', None),
'135': (r'D（\(\sqrt{7}+1\)）', None),
'136': (r'C（\(\dfrac{16\sqrt{2}\pi}{3}\)）', None),
'137': (r'A（\(r=1\)）', None),
'138': (r'D（\(\dfrac{7\pi}{2}\)）', None),
'139': (r'\(2\sqrt{3}\)；\(\dfrac{9}{4}\)', None),
'140': ('B（圆）', None),
'141': ('B（圆）', None),
'142': ('D（四条直线）', None),
'143': (r'\(\dfrac{2\sqrt{5}}{3}\)', None),
'144': (r'\(m=1\)；\(0<m<\sqrt{2}\) 且 \(m\neq 1\)', None),
'145': (r'\(\dfrac{\sqrt{2}+1}{2}\)', None),
'146': (r'\(\sqrt{2}\)', None),
'147': (r'\(\dfrac{1}{4}\)', None),
'148': (r'(1)证明成立；(2)\(B_{1}D=\dfrac{1}{2}\)（此时 \(\sin\theta_{\min}=\dfrac{\sqrt{3}}{3}\)）', None),
'149': (r'(1)成立；(2)\(\dfrac{\sqrt{6}}{6}\)', None),
'150': (r'C（\(\dfrac{7}{8}\)）', None),
'151': (r'C（\(\dfrac{5\sqrt{2}a^{3}}{12}\)）', None),
'152': (r'\(\dfrac{46\sqrt{2}}{3}\)；\(22\pi\)', None),
'153': (r'B（\(a>b>d>c\)）', None),
'154': ('②③④（①假）', None),
'155': (r'C（\(45^{\circ}\) 或 \(60^{\circ}\)）', None),
'156': (r'(1)成立（\(AD\parallel\) 平面 \(B_{1}PQ\)）；(2)\(\dfrac{\sqrt{6}}{2}\)', None),
'157': (r'(1)\(4\)；(2)\(\dfrac{\sqrt{5}}{2}\)', None),
'158': (r'\(\dfrac{\sqrt{2}}{2}\)', None),
'159': (r'\(\dfrac{30\sqrt{233}}{233}\)', None),
'160': (r'\(\dfrac{3\sqrt{13}}{2}\)', None),
}
assert '057' not in TUO and len(TUO) == 159, 'TUO 应 159 题（跳 057）'
for _n in sorted(TUO):
    put('拓-%s' % _n, *TUO[_n])

# ------------------------------------------------------------
# 【丁】卷件（测-1~19＝卷件值台账 §一；滚A/滚B-1~16＝§二/三＋命制档；
#   义7-2：测15~19、滚A/B 13~16 解析行承载卷末速查「略」全解）
# ------------------------------------------------------------
CE = {
'1': ('D', None),
'2': (r'B（\(45^{\circ}\)）', None),
'3': (r'A（\(\angle PCA\)）', None),
'4': (r'A（\(2\)）', None),
'5': ('C', None),
'6': (r'C（\(60^{\circ}\)）', None),
'7': (r'A（\(\dfrac{\sqrt{77}}{3}\)）', None),
'8': (r'A（\(\left(-\dfrac{4}{5},3,\dfrac{4}{5}\right)\)）', None),
'9': ('ABC', None),
'10': ('ABC', None),
'11': ('ABD', None),
'12': (r'\(\dfrac{7}{5}\)', None),
'13': (r'\(x=\dfrac{1}{6}\)，\(y=-\dfrac{3}{2}\)', None),
'14': (r'\(\sqrt{3}\)', None),
'15': (r'\(\left(0,\dfrac{\sqrt{2}}{2},\dfrac{\sqrt{2}}{2}\right)\)（方向可反）',
       r'\(\ov{AB}=(-1,1,-1)\)、\(\ov{AC}=(-1,0,0)\)。设 \(\ov{n}=(x,y,z)\)：'
       r'\(\ov{n}\cdot\ov{AC}=0\) 得 \(x=0\)；\(\ov{n}\cdot\ov{AB}=0\) 得 \(y=z\)。'
       r'取 \(\ov{n}=(0,1,1)\)，\(|\ov{n}|=\sqrt{2}\)，单位化得 \(\left(0,\dfrac{\sqrt{2}}{2},\dfrac{\sqrt{2}}{2}\right)\)（方向可反）。'),
'16': (r'\(90^{\circ}\)',
       r'以 \(D\) 为原点、棱长为 \(1\)：\(\ov{A_{1}D}=(-1,0,-1)\)、\(\ov{BD_{1}}=(-1,-1,1)\)，'
       r'\(\cos\langle\ov{A_{1}D},\ov{BD_{1}}\rangle=\dfrac{1-1}{\sqrt{2}\cdot\sqrt{3}}=0\)，所成角 \(90^{\circ}\)。'),
'17': (r'\(60^{\circ}\)',
       r'\(\angle AMB=90^{\circ}\)（直径所对圆周角），故 \(BM\perp AM\)；又 \(PA\perp\) 圆面得 \(BM\perp PA\)，'
       r'于是 \(BM\perp\) 平面 \(PAM\)，\(PM\perp BM\)——\(\angle PMA\) 即二面角 \(A\text{-}BM\text{-}P\) 的平面角。'
       r'\(AM=AB\cos 60^{\circ}=2\)，\(\mathrm{Rt}\triangle PAM\) 中 \(\tan\angle PMA=\dfrac{PA}{AM}=\dfrac{2\sqrt{3}}{2}=\sqrt{3}\)，\(\angle PMA=60^{\circ}\)。'),
'18': (r'(1)\(45^{\circ}\)；(2)\(90^{\circ}\)；(3)\(\dfrac{2\sqrt{5}}{5}\)',
       r'设棱长 \(a\)，\(B\) 为原点、\(BC\) 为 \(x\) 轴、面 \(BCD\) 为 \(xy\) 面（两平面垂直、交线 \(BC\)）：'
       r'\(C(a,0,0)\)、\(D\left(-\dfrac{a}{2},\dfrac{\sqrt{3}a}{2},0\right)\)、\(A\left(-\dfrac{a}{2},0,\dfrac{\sqrt{3}a}{2}\right)\)。'
       r'(1) \(A\) 到面 \(BCD\) 距离 \(\dfrac{\sqrt{3}a}{2}\)、\(|\ov{AD}|=\dfrac{\sqrt{6}a}{2}\)，\(\sin\theta=\dfrac{\sqrt{2}}{2}\)，\(45^{\circ}\)。'
       r'(2) \(\ov{AD}\cdot\ov{BC}=0\)，\(90^{\circ}\)。'
       r'(3) 面 \(ABD\) 法向量 \(\ov{n}=(3,\sqrt{3},\sqrt{3})\)，与面 \(BCD\) 法向量 \((0,0,1)\) 夹角余弦 \(\dfrac{\sqrt{3}}{\sqrt{15}}=\dfrac{\sqrt{5}}{5}\)，正弦 \(\dfrac{2\sqrt{5}}{5}\)。'),
'19': (r'(1)\((x-2)^{2}+(y-2)^{2}=4\)，内切圆，\(4\pi\)；(2)\(m=12\) 或 \(16\)；(3)\(4\)、\(4\sqrt{2}\)、\(4\sqrt{3}\)',
       r'设 \(P(x,y,0)\)：\(\ov{PA_{1}}\cdot\ov{PC_{1}}=(x-2)^{2}+(y-2)^{2}+8=m\)，轨迹为底面内以 \((2,2)\) 为心、'
       r'\(r^{2}=m-8\) 的圆（\(m\ge 8\)）。(1) \(m=12\)：\(r=2\)＝边心距，圆为底面内切圆，长 \(2\pi\times 2=4\pi\)。'
       r'(2) 按 \(r\) 对 \(2\)、\(2\sqrt{2}\) 双门槛分档：恰 \(4\) 个公共点 \(\iff m=12\)（四边各相切）或 \(m=16\)（过四顶点）。'
       r'(3) \(m=16\) 时轨迹缩为四顶点，\(|\ov{PB_{1}}|\) 依次为 \(4\sqrt{2}\)、\(4\)、\(4\sqrt{2}\)、\(4\sqrt{3}\)，可能值 \(4\)、\(4\sqrt{2}\)、\(4\sqrt{3}\)。'),
}
assert len(CE) == 19
for _n in sorted(CE, key=int):
    put('测-%s' % _n, *CE[_n])
GUN = {
'A': {
'1': ('A', None), '2': ('A', None), '3': ('D', None), '4': ('A', None),
'5': ('D', None), '6': ('A', None), '7': ('D', None),
'8': ('ABC', None), '9': ('ABC', None),
'10': (r'\((3,0,0)\)', None),
'11': (r'\(\dfrac{1}{6}\)', None),
'12': (r'(1)平行；(2)\(\cos\varphi\)；(3)\(90^{\circ}\)', None),
'13': (r'证明：\(|\ov{AC}|^{2}+|\ov{BD}|^{2}=2|\ov{a}|^{2}+2|\ov{b}|^{2}\)（＝四边平方和）',
       r'设 \(\ov{AB}=\ov{a}\)、\(\ov{AD}=\ov{b}\)，则 \(\ov{AC}=\ov{a}+\ov{b}\)、\(\ov{BD}=\ov{b}-\ov{a}\)。'
       r'\(|\ov{AC}|^{2}+|\ov{BD}|^{2}=|\ov{a}+\ov{b}|^{2}+|\ov{b}-\ov{a}|^{2}=2|\ov{a}|^{2}+2|\ov{b}|^{2}\)；'
       r'而四边平方和 \(=2(|\ov{a}|^{2}+|\ov{b}|^{2})\)，两式相等，证毕。'),
'14': (r'(1)\(\ov{AP}=\dfrac{1}{3}\ov{a}+\dfrac{1}{3}\ov{b}+\dfrac{1}{3}\ov{c}\)；(2)不共线',
       r'(1) \(E\) 为 \(CD\) 中点，\(\ov{AE}=\dfrac{1}{2}(\ov{b}+\ov{c})\)；\(BP=\dfrac{2}{3}\ov{BE}\)，'
       r'\(\ov{AP}=\ov{a}+\dfrac{2}{3}(\ov{AE}-\ov{a})=\dfrac{1}{3}\ov{a}+\dfrac{1}{3}\ov{b}+\dfrac{1}{3}\ov{c}\)。'
       r'(2) \(\ov{a},\ov{b},\ov{c}\) 不共面＝空间基底，分解唯一；若 \(A,P,Q\) 共线，\(\ov{AQ}=k\ov{AP}\) '
       r'按基底比较给 \(k=2\) 且 \(k=1\)，矛盾，故不共线。'),
'15': (r'(1)\(A(2,0,0)\)、\(C(0,2,0)\)、\(B_{1}(2,2,2)\)、\(D_{1}(0,0,2)\)；'
       r'(2)六棱均 \(2\sqrt{2}\)，正四面体；(3)\(G\left(\dfrac{2}{3},\dfrac{4}{3},\dfrac{4}{3}\right)\)，\(|\ov{AG}|=\dfrac{4\sqrt{3}}{3}\)',
       r'(2) 六棱逐对计算均 \(2\sqrt{2}\)，四面体 \(ACB_{1}D_{1}\) 为正四面体。'
       r'(3) 设 \(G(x,y,z)\)，由 \(\ov{GC}+\ov{GB_{1}}+\ov{GD_{1}}=\ov{0}\) 得 \((2-2x,4-3y,4-3z)=\ov{0}\)，'
       r'解得 \(G\left(\dfrac{2}{3},\dfrac{4}{3},\dfrac{4}{3}\right)\)；\(\ov{AG}=\left(-\dfrac{4}{3},\dfrac{4}{3},\dfrac{4}{3}\right)\)，'
       r'\(\ov{AG}\cdot\ov{CB_{1}}=\ov{AG}\cdot\ov{CD_{1}}=0\)（均垂直），\(|\ov{AG}|=\sqrt{3\cdot\dfrac{16}{9}}=\dfrac{4\sqrt{3}}{3}\)。'),
'16': (r'(1)\(4\)；\(4+t^{2}\)；\(8+t^{2}\)；(2)恒为以 \(B\) 为直角顶点的直角三角形，等腰仅 \(t=0\)；'
       r'(3)\(\tan\theta\in\left[\dfrac{2\sqrt{13}}{13},1\right]\)，最大 \(45^{\circ}\)（\(t=0\)）',
       r'(1) \(P(0,2,t)\)：\(|\ov{AB}|^{2}=4\)、\(|\ov{PB}|^{2}=4+t^{2}\)、\(|\ov{PA}|^{2}=8+t^{2}\)。'
       r'(2) 三顶点分类：\(A\) 处 \(\ov{AB}\cdot\ov{AP}=4\neq0\)；\(P\) 处 \(\ov{PA}\cdot\ov{PB}=4+t^{2}>0\) 恒正；'
       r'仅 \(B\) 处 \(\ov{BA}\cdot\ov{BP}=0\) 对一切 \(t\in[0,3]\) 成立，且三点恒不共线——恒为以 \(B\) 为直角顶点的直角三角形。'
       r'等腰三分支：\(|AB|=|PB|\iff t=0\)，另两支无解——等腰仅 \(t=0\)。'
       r'(3) \(\tan\theta=\dfrac{|\ov{AB}|}{|\ov{BP}|}=\dfrac{2}{\sqrt{4+t^{2}}}\)，\(4+t^{2}\in[4,13]\)，'
       r'\(\tan\theta\in\left[\dfrac{2\sqrt{13}}{13},1\right]\)，最大值 \(1\) 在 \(t=0\) 取得（\(\theta=45^{\circ}\)）。'),
},
'B': {
'1': ('A', None), '2': ('A', None), '3': ('B', None), '4': ('A', None),
'5': ('C', None), '6': ('C', None),
'7': ('AC', None), '8': ('ABC', None), '9': ('AB', None),
'10': (r'\((0)\)', None),
'11': (r'\(\dfrac{7}{2}\)', None),
'12': (r'\(\dfrac{2\sqrt{3}}{3}\)', None),
'13': (r'(1)\(A(2,0,0)\)、\(B_{1}(2,2,4)\)、\(E(2,2,2)\)；(2)\(\dfrac{\sqrt{10}}{5}\)',
       r'(2) \(\ov{AE}=(0,2,2)\)、\(\ov{CB_{1}}=(2,0,4)\)，'
       r'\(\cos\langle\ov{AE},\ov{CB_{1}}\rangle=\dfrac{8}{2\sqrt{2}\cdot 2\sqrt{5}}=\dfrac{\sqrt{10}}{5}\)。'),
'14': (r'(1)\(\ov{n}=(6,3,2)\)；(2)\(t=-2\)；(3)\(\dfrac{13}{7}\)',
       r'(1) \(\ov{AB}=(-1,2,0)\)、\(\ov{AC}=(-1,0,3)\)，联立 \(\ov{n}\cdot\ov{AB}=\ov{n}\cdot\ov{AC}=0\) 取 \(\ov{n}=(6,3,2)\)。'
       r'(2) \(\ov{AQ}=(0,t,3)\)，\(\ov{n}\cdot\ov{AQ}=3t+6=0\)，\(t=-2\)。'
       r'(3) \(\ov{AD}=(1,1,2)\)，\(d=\dfrac{|\ov{n}\cdot\ov{AD}|}{|\ov{n}|}=\dfrac{13}{\sqrt{49}}=\dfrac{13}{7}\)。'),
'15': (r'(1)\(BC\perp\) 面 \(PAB\)、\(AE\perp\) 面 \(PBC\)（\(AE\) 长即距离）；(2)\(AB=2\sqrt{3}\)；(3)\(\dfrac{\sqrt{5}}{5}\)',
       r'(1) \(PA\perp\) 面 \(ABC\) 得 \(PA\perp BC\)，又 \(AB\perp BC\)，故 \(BC\perp\) 平面 \(PAB\)；'
       r'于是 \(BC\perp AE\)，结合 \(AE\perp PB\) 得 \(AE\perp\) 平面 \(PBC\)，垂足在面内——\(AE\) 长即点 \(A\) 到面 \(PBC\) 的距离。'
       r'(2) 设 \(AB=x\)：\(\mathrm{Rt}\triangle PAB\) 中 \(AE=\dfrac{PA\cdot AB}{PB}=\dfrac{2x}{\sqrt{x^{2}+4}}=\sqrt{3}\)，'
       r'解得 \(x^{2}=12\)，\(AB=2\sqrt{3}\)。'
       r'(3) \(PB\) 为 \(PC\) 在面 \(PAB\) 内的射影，\(\sin\angle CPB=\dfrac{BC}{PC}=\dfrac{2}{\sqrt{16+4}}=\dfrac{\sqrt{5}}{5}\)。'),
'16': (r'(1)\(120^{\circ}\)；(2)\(\dfrac{\sqrt{3}}{2}\)；(3)\(\dfrac{\sqrt{3}}{4}\)',
       r'(1) 取 \(AC\) 中点 \(O\)：\(BO\perp AC\)、\(DO\perp AC\)，\(BO=DO=1\)，'
       r'\(\cos\angle BOD=\dfrac{1+1-3}{2\cdot 1\cdot 1}=-\dfrac{1}{2}\)，二面角 \(B\text{-}AC\text{-}D\) 为 \(120^{\circ}\)。'
       r'(2) \(AC\perp\) 平面 \(BOD\)，面 \(BOD\perp\) 面 \(ACD\)、交线 \(OD\)；作 \(BH\perp OD\)，'
       r'则 \(BH\perp\) 面 \(ACD\)，\(BH=BO\sin 60^{\circ}=\dfrac{\sqrt{3}}{2}\) 即距离。'
       r'(3) \(\sin\theta=\dfrac{BH}{AB}=\dfrac{\sqrt{3}/2}{2}=\dfrac{\sqrt{3}}{4}\)。'),
},
}
for _x in ('A', 'B'):
    assert len(GUN[_x]) == 16
    for _n in sorted(GUN[_x], key=int):
        put('滚%s-%s' % (_x, _n), *GUN[_x][_n])

# ============================================================
# 分册前缀断言 → 钉值门 → body.tex → 值快照.json
# ============================================================
ZH = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五'}
KSH = {'01': '第一课时', '02': '第二课时', '03': '第三课时', '04': '第四课时', '05': '第五课时',
       '06': '第六课时', '07': '第七课时', '08': '第八课时', '09': '第九课时', '10': '第十课时'}


def _tex(s):
    r"""判断符号转 LaTeX（宏包无 amssymb：\surd 为 kernel 符号；其余值已为 LaTeX 串）。"""
    return s.replace('√', r'\(\surd\)').replace('×', r'$\times$')


def _mark(key):
    return '%% pair:%s' % key          # 对号契约：行首 `% pair:键`（check_pairs 扫描口径）


def _sanity():
    for k, (v, n) in V.items():
        assert '%' not in v and '%' not in (n or ''), '裸 %% 入值：%s' % k
        assert v.count(r'\(') == v.count(r'\)'), r'\( 不配对：%s' % k
        assert v.count('{') == v.count('}'), '花括号不配对：%s' % k


def keshi_body(hh):
    L = ['%% ---- %s（1.1.x/1.2.x 同构槽序：预习→判断→探究→评价）----' % KSH[hh]]
    b = '导-课时%s-' % hh
    L.append(_mark(b + '预习填空'))
    L.append(r'\ansline{预习填空}{%s}' % _tex(V[b + '预习填空'][0]))
    for i in range(1, 6):
        L.append(_mark('%s判%d' % (b, i)))
    L.append(r'\ansline{答案}{%s}' % r'\quad '.join(
        '(%d)%s' % (i, _tex(V['%s判%d' % (b, i)][0])) for i in range(1, 6)))
    eks = [k for k in V if k.startswith(b + '探')]
    pts = sorted(set(int(k.split('-')[2][1:]) for k in eks))
    for p in pts:
        grp = sorted((k for k in eks if '-探%d-' % p in k),
                     key=lambda k: (0 if '例' in k else 1,
                                    int(''.join(c for c in k.split('-')[3] if c.isdigit()))))
        for k in grp:
            L.append(_mark(k))
        L.append(r'\ansline{探究%s}{%s}' % (ZH[p], '；'.join(
            r'%s %s' % (k.split('-')[3], _tex(V[k][0])) for k in grp)))
        for k in grp:
            if V[k][1]:
                L.append(r'\ansline{解析}{%s}' % _tex(V[k][1]))
    for i in range(1, 6):
        L.append(_mark('%s评%d' % (b, i)))
    L.append(r'\ansline{评价}{%s}' % '；'.join(
        '%d．%s' % (i, _tex(V['%s评%d' % (b, i)][0])) for i in range(1, 6)))
    return L


def items(prefix, nums, macro=r'\ansitem{%s}{%s}', note_label='解析'):
    L = []
    for n in nums:
        k = '%s-%s' % (prefix, n)
        L.append(_mark(k))
        L.append(macro % (n, _tex(V[k][0])))
        if V[k][1]:
            L.append(r'\ansline{%s}{%s}' % (note_label, _tex(V[k][1])))
    return L


def build_body():
    import io
    import datetime
    L = []
    L.append('% ============================================================')
    L.append('% body.tex —— 答案册·M2 轮4 S5【组装器产出】——勿手改（组装S5.py 为唯一值源，防 6g 回卷）')
    L.append('%% 生成：%s｜键数：%d｜对号契约：每键一行 `%%%% pair:键`（check_pairs 扫描口径）'
             % (datetime.date.today().isoformat(), len(V)))
    L.append('% 版式：册首行/章标/节标/分区组行/条目宏五模块在 main.tex＋qp-answ-*（骨架口径原样）；'
             '悬挂两档＝单号 5.8mm／双位 7.6mm。')
    L.append('% ============================================================')
    L.append(r'\setcounter{page}{1}   % 独立册起页 1；装配轮按四本跨本连续页码（G7）改写')
    L.append(r'\par\nointerlineskip')
    L.append(r'{\centering\fontsize{16.88pt}{22pt}\selectfont\hejie 参考答案\par}')
    L.append(r'\vspace{2.4mm}')
    L.append(r'\zhangtitle{第一章\quad 空间向量与立体几何}')
    L.append('')
    L.append(r'% ---- body 局部宏：值串向量缩写 \ov{X}（提供式——重名时让位）；'
             r'判断符号用 \(\surd\)/$\times$（宏包无 amssymb，均为 kernel 符号） ----')
    L.append(r'\providecommand{\ov}[1]{\overrightarrow{#1}}')
    L.append(r'% ---- 目验修红0913：\dansitem 标签叠印修复（body 局部重定义；qp-answ-extra.tex 原宏零改动）----')
    L.append(r'% 缺陷：中文号标签（例N/变式N/高考N）11.4pt 实宽约 6.0～12.2mm＞原宏固定悬挂 \anshang 5.8mm，')
    L.append(r'%   零宽标签盒压「[答案]」首字（册93＝章末段 28 处实证）。修法：settowidth 测标签实宽，')
    L.append(r'%   悬挂取 max(\anshang, 实宽＋0.6mm)——续行缩进 \qpind、答距 0.5em 口径不变。')
    L.append(r'\newdimen\danshang')
    L.append(r'\renewcommand{\dansitem}[2]{\par\glueguard{1}\addvspace{4pt}%')
    L.append(r'  {\everypar{\hangindent\qpind\hangafter=1\setlength{\parindent}{\qpind}}%')
    L.append(r'  \settowidth{\danshang}{{\fontsize{11.4pt}{13pt}\selectfont\heihao #1}}%')
    L.append(r'  \ifdim\danshang<\anshang \danshang\anshang\fi')
    L.append(r'  \noindent')
    L.append(r'  \makebox[0pt][l]{{\fontsize{11.4pt}{13pt}\selectfont\heihao #1}}%')
    L.append(r'  \hspace*{\dimexpr\danshang+0.6mm\relax}{\anlabel [答案]}\hspace{0.5em}#2\par}}')

    # ============ 【甲】导学件 ============
    L.append('')
    L.append('% ============================================================')
    L.append('% 【甲】导学件答案（10 课时＋1.1.1 前衔接填空六条（不计题）＋衔接-1~29＋章末 28）')
    L.append('% ============================================================')
    L.append(r'\jietitle{1.1.1\quad 空间向量及其运算(导学件答案)}')
    L.append(r'\begin{multicols}{2}')
    L.append(r'\raggedcolumns')
    L.append(r'\emergencystretch=1em')
    L.append(r'\qufen{第一课时\quad 空间向量及其运算(课1)}{课前预习＋课中探究（例1×4／变式1×4）＋课堂评价5}')
    L += keshi_body('01')
    L.append(r'\qufen{第二课时\quad 空间向量及其运算(课2·数量积域)}{课前预习＋课中探究（例1×5／变式1×5）＋课堂评价5}')
    L += keshi_body('02')
    L.append(r'\qufen{1.1.1 前·衔接：平面向量必会}{纯知识点填空六条——不计题、不占衔接-号段}')
    # 2026-09-12 S7收尾批：衔接14空回填（盲解键源＝逻辑闸/导学-课1-3-glm.md §衔接填空①～⑥；
    # 不计题、不加 pair 对号键——键数 631／快照 633 不变）
    L.append(r'\ansline{衔接填空}{① \(\ov{AC}\)；对角线。② \(|\lambda||\ov{a}|\)；\(\lambda\ov{a}+\mu\ov{a}\)；'
             r'\(\lambda\ov{a}+\lambda\ov{b}\)。③ 一；\(\lambda\ov{a}\)。④ 不共线；'
             r'\(\lambda_{1}\ov{e_{1}}+\lambda_{2}\ov{e_{2}}\)。⑤ \(|\ov{a}||\ov{b}|\cos\theta\)；'
             r'\(\ov{b}\cdot\ov{a}\)；\(\ov{a}\cdot\ov{b}=0\)。⑥ \(|\ov{a}|\cos\theta\)；正、0、负。}')
    L.append(r'\jietitle{1.1.2\quad 空间向量基本定理(导学件答案)}')
    L.append(r'\qufen{第三课时\quad 空间向量基本定理}{课前预习＋课中探究（例1×4／变式1×4）＋课堂评价5}')
    L += keshi_body('03')
    L.append(r'\jietitle{1.1.3\quad 空间向量及其运算的坐标表示(导学件答案)}')
    L.append(r'\qufen{第四课时\quad 空间直角坐标系与坐标(课1)}{课前预习＋课中探究（例1×3／变式×5 含变式2）＋课堂评价5}')
    L += keshi_body('04')
    L.append(r'\qufen{第五课时\quad 坐标表示(课2)}{课前预习＋课中探究（例1×5／变式1×5）＋课堂评价5}')
    L += keshi_body('05')
    L.append(r'\jietitle{1.2.1\quad 空间中的点、直线与空间向量(导学件答案)}')
    L.append(r'\qufen{1.2.1 前·几何衔接位}{衔接-1～衔接-29 同号段——五组排布、组内四约束}')
    L += items('导-衔接', [str(i) for i in range(1, 30)],
               macro=r'\ansline{衔接-%s}{%s}')
    L.append(r'\qufen{第六课时\quad 空间中的点、直线与空间向量}{课前预习＋课中探究（例1×5／变式1×5）＋课堂评价5}')
    L += keshi_body('06')
    L.append(r'\jietitle{1.2.2\quad 空间中的平面与空间向量(导学件答案)}')
    L.append(r'\qufen{第七课时\quad 空间中的平面与空间向量}{课前预习＋课中探究（例1×5／变式1×5）＋课堂评价5}')
    L += keshi_body('07')
    L.append(r'\jietitle{1.2.3\quad 直线与平面的夹角(导学件答案)}')
    L.append(r'\qufen{第八课时\quad 直线与平面的夹角}{课前预习＋课中探究（例1×5／变式1×5）＋课堂评价5}')
    L += keshi_body('08')
    L.append(r'\jietitle{1.2.4\quad 二面角(导学件答案)}')
    L.append(r'\qufen{第九课时\quad 二面角}{课前预习＋课中探究（例1×5／变式1×5）＋课堂评价5}')
    L += keshi_body('09')
    L.append(r'\jietitle{1.2.5\quad 空间中的距离(导学件答案)}')
    L.append(r'\qufen{第十课时\quad 空间中的距离}{课前预习＋课中探究（例1×5／变式1×5）＋课堂评价5}')
    L += keshi_body('10')
    L.append(r'\jietitle{本章总结提升(导学件答案)}')
    L.append(r'\qufen{章末·题型归类}{题型 12 型（例12／变式12）＋精选高考题组 4 题}')
    L += items('导-章末', ['例%d' % i for i in range(1, 13)] + ['变式%d' % i for i in range(1, 13)]
               + ['高考%d' % i for i in range(1, 5)], macro=r'\dansitem{%s}{%s}')
    L.append(r'\end{multicols}')
    return L


def build_body_rest(L):
    # ============ 【乙】练习件 ============
    L.append('')
    L.append('% ============================================================')
    L.append('% 【乙】练习件答案（10 课时×16 题＝160；题号 1~9 单号档、题 10~16 双位档）')
    L.append('% ============================================================')
    jie = [(r'1.1.1\quad 空间向量及其运算(练习件答案)',
            [(r'01', r'第一课时\quad 1.1.1(课1)'), (r'02', r'第二课时\quad 1.1.1(课2)')]),
           (r'1.1.2\quad 空间向量基本定理(练习件答案)', [(r'03', r'第三课时\quad 1.1.2')]),
           (r'1.1.3\quad 空间向量及其运算的坐标表示(练习件答案)',
            [(r'04', r'第四课时\quad 1.1.3(课1)'), (r'05', r'第五课时\quad 1.1.3(课2)')]),
           (r'1.2.1\quad 空间中的点、直线与空间向量(练习件答案)', [(r'06', r'第六课时\quad 1.2.1')]),
           (r'1.2.2\quad 空间中的平面与空间向量(练习件答案)', [(r'07', r'第七课时\quad 1.2.2')]),
           (r'1.2.3\quad 直线与平面的夹角(练习件答案)', [(r'08', r'第八课时\quad 1.2.3')]),
           (r'1.2.4\quad 二面角(练习件答案)', [(r'09', r'第九课时\quad 1.2.4')]),
           (r'1.2.5\quad 空间中的距离(练习件答案)', [(r'10', r'第十课时\quad 1.2.5')])]
    for t, ks in jie:
        L.append(r'\jietitle{%s}' % t)
        L.append(r'\begin{multicols}{2}')
        L.append(r'\raggedcolumns')
        L.append(r'\emergencystretch=1em')
        for hh, q in ks:
            L.append(r'\setlength{\anshang}{5.8mm}')
            L.append(r'\qufen{%s}{本课时共16题——题号与练习件同号}' % q)
            L += items('练-课时' + hh, [str(i) for i in range(1, 10)])
            L.append(r'\setlength{\anshang}{7.6mm}   % 题 10 起双位档')
            L += items('练-课时' + hh, [str(i) for i in range(10, 17)])
        L.append(r'\end{multicols}')

    # ============ 【丙】拓展册 ============
    L.append('')
    L.append('% ============================================================')
    L.append('% 【丙】拓展册答案（拓-001~160 连续流水、057 撤下＝义A-1/钉-6 哨兵，159 题）')
    L.append('% ============================================================')
    L.append(r'\jietitle{拓展册(答案)}')
    L.append(r'\begin{multicols}{2}')
    L.append(r'\raggedcolumns')
    L.append(r'\emergencystretch=1em')
    L.append(r'\setlength{\anshang}{7.6mm}   % 拓-三位号＝双位档起')
    doms = [('一、1.1.1 域', 1, 10, '拓-001～010'), ('二、1.1.2 域', 11, 17, '拓-011～017'),
            ('三、1.1.3 域', 18, 37, '拓-018～037'), ('四、1.2.1 域', 38, 42, '拓-038～042'),
            ('五、1.2.2 域', 43, 50, '拓-043～050'), ('六、1.2.3 域', 51, 58, '拓-051～056、058'),
            ('七、1.2.4 域', 59, 79, '拓-059～079'), ('八、1.2.5 域', 80, 160, '拓-080～160')]
    # 目验修红0913：六/八域说明剥「057 撤下／已撤·域外不涉」内部撤号语，改学生可读号段
    for t, lo, hi, desc in doms:
        L.append(r'\qufen{%s}{%s}' % (t, desc))
        L += items('拓', ['%03d' % n for n in range(lo, hi + 1) if n != 57])
    L.append(r'\end{multicols}')

    # ============ 【丁】卷件 ============
    L.append('')
    L.append('% ============================================================')
    L.append('% 【丁】测评卷＋滚动卷A/B 答案（解答位全解＝义7-2，承卷末速查「略」）')
    L.append('% ============================================================')
    rolls = [('测评卷(答案)', '测', [(1, 8, r'\qufen{一、单项选择题}{本组共8题}'),
             (9, 11, r'\qufen{二、多项选择题}{本组共3题}'),
             (12, 14, r'\qufen{三、填空题}{本组共3题}'),
             (15, 19, r'\qufen{四、解答题}{本组共5题}')]),
             ('滚动测评卷A(答案)', '滚A', [(1, 7, r'\qufen{一、单项选择题}{本组共7题}'),
             (8, 9, r'\qufen{二、多项选择题}{本组共2题}'),
             (10, 12, r'\qufen{三、填空题}{本组共3题}'),
             (13, 16, r'\qufen{四、解答题}{本组共4题}')]),
             ('滚动测评卷B(答案)', '滚B', [(1, 6, r'\qufen{一、单项选择题}{本组共6题}'),
             (7, 9, r'\qufen{二、多项选择题}{本组共3题}'),
             (10, 12, r'\qufen{三、填空题}{本组共3题}'),
             (13, 16, r'\qufen{四、解答题}{本组共4题}')])]
    for t, pf, secs in rolls:
        L.append(r'\jietitle{%s}' % t)
        L.append(r'\begin{multicols}{2}')
        L.append(r'\raggedcolumns')
        L.append(r'\emergencystretch=1em')
        for k, (lo, hi, q) in enumerate(secs):
            if k == 2:
                L.append(r'\setlength{\anshang}{7.6mm}')
            else:
                L.append(r'\setlength{\anshang}{5.8mm}')
            L.append(q)
            L += items(pf, [str(n) for n in range(lo, hi + 1)])
        L.append(r'\end{multicols}')
    return L


def main():
    # 两断言模块导入时各自包装 sys.stdout——用中转对象承接、保活其包装防 GC 关底缓冲，
    # 顶部另挂自管行缓冲包装（读数不丢、退出即刷）
    class _NS:
        pass
    buf = sys.stdout.buffer
    ns = _NS()
    ns.buffer = buf
    keep = []
    saved = sys.stdout
    sys.stdout = ns
    import check_pairs as cp
    keep.append(sys.stdout)
    import 钉值门 as gate
    keep.append(sys.stdout)
    sys.stdout = saved
    sys.stdout = io.TextIOWrapper(buf, encoding='utf-8', line_buffering=True)
    print('==== 组装S5：值表 %d 键 ====' % len(V))
    _sanity()
    # ① 分册前缀断言（拓 侧按撤重 159 档＝义A-1；其余 160/全量档）
    exp160, exp159 = cp.collect_expected(), cp.collect_expected(tuo159=True)
    for p, exp in [('导', exp160), ('练', exp160), ('拓', exp159),
                   ('测', exp160), ('滚A', exp160), ('滚B', exp160)]:
        want = {k for k in exp if k.split('-')[0] == p}
        got = {k for k in V if k.split('-')[0] == p}
        assert got == want, '分册断言 %s 不等：缺 %s 多 %s' % (p, sorted(want - got)[:8], sorted(got - want)[:8])
        print('分册断言 %s：%d 键相等零缺漏 ✓' % (p, len(want)))
    # ② 钉值门（键式两制：门表用中文号探位别名）
    snap = {k: V[k][0] for k in V}
    snap['导-课时02-探五变式1'] = V['导-课时02-探5-变式1'][0]
    snap['导-课时03-探四例1'] = V['导-课时03-探4-例1'][0]
    gate.run(gate.GATES, snap)
    print('钉值门：生效门 %d 项全过 ✓'
          % sum(1 for g in gate.GATES if g['status'] == '生效' and g['want'] is not None))
    # ③ body.tex
    L = build_body()
    build_body_rest(L)
    # 栏平衡消 Overfull vbox：条目行后挂微收缩胶（宏族零改动，body 内自医；不可见——
    # 仅当栏高超出时启用收缩。目验修红0913：甲册章末悬挂加宽＋解析剥语致后段页界微移，
    # 收缩上限 1.2pt→1.6pt 复零 Overfull（扫胶 1.2/1.6/2.0/2.8/3.2 实测仅 1.6 与 2.0 双零，
    # 取近原值 1.6）；非超压态行距零变化）
    OUT = []
    for x in L:
        OUT.append(x)
        if x.startswith((r'\ansitem', r'\ansline', r'\dansitem')):
            OUT.append(r'\vskip 0pt minus 1.6pt')
    L = OUT
    marks = [x for x in L if x.startswith('% pair:')]
    assert len(marks) == len(V) == len(set(marks)), 'pair 标记数 %d ≠ 键数 %d' % (len(marks), len(V))
    f = os.path.join(HERE, 'body.tex')
    with io.open(f, 'w', encoding='utf-8', newline='\n') as w:
        w.write('\n'.join(L) + '\n')
    print('body.tex：%d 行（pair 标记 %d）' % (len(L), len(marks)))
    # ④ 值快照.json（含钉门中文号别名 2 键）
    sj = os.path.join(HERE, '值快照.json')
    with io.open(sj, 'w', encoding='utf-8', newline='\n') as w:
        json.dump(snap, w, ensure_ascii=False, indent=0, sort_keys=True)
    print('值快照.json：%d 键（631 对号键＋钉门别名 2）' % len(snap))
    print('组装完成 ✓（下一步：check_pairs --拓159 --strict ／ 钉值门 --strict 值快照.json ／ xelatex×2）')


if __name__ == '__main__':
    main()
