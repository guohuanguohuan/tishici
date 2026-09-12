# -*- coding: utf-8 -*-
r"""组装S5.py —— 答案册 body.tex ＋ 值快照.json 组装器（P1 轮4 成卷 S5·骨架＋注值一体）。

值源（唯一依据，禁凭转述落墨）：
  导-课时91 ← 成卷/就绪报告.md §附录A（9.1 导学件首件）；
  练-课时91 ← 成卷/练习件/批1值台账.md §一；
  导-课时92/练-课时92 ← 成卷/批2值台账.md §一/§二（中4 转导学照用·练习件第2题位略；
    预习填空＝§二-A1〔2026-09-12 收尾轮补登〕）；
  导-课时93/练-课时93 ← 成卷/批3值台账.md §一/§二（练习件第2题位略·简8 出列；
    预习填空＝§二-A1〔收尾轮补登〕）；
  导-课时94/练-课时94 ← 成卷/批4值台账.md §一/§四；
  导-章末 ← 成卷/批5a值台账.md §一（5 题）；学史切片 0 题不入册；
  拓-001~046 ← 成卷/批5b值台账.md §一（印面答案；◐改号件按 §一-3 映射；拓46＝收尾轮改单选 §八-1）；
  测-1~19 ← 成卷/批5b值台账.md §四（测13 单位＝§八-2 勘正值 kg·m³·s⁻⁴·A⁻²）。
收尾轮（2026-09-12）：PENDING 65 键全部转实值、缺账 2 槽随批2/批3 §二-A1 补登回填——
  PRE_GAP／PENDING_KEYS 皆空集，白名单机制保留备用。
流程：建 208 键值表 → 分册断言（check_pairs.collect_expected 子集比对）→ 钉值门 run（生效 15 门）
→ 写 body.tex（每键一行 `% pair:键`）→ 写 值快照.json。
跑法：python 组装S5.py
零 git；PL1 样张原目录零改动（main.tex 绝对路径只读引用）；骨架 body.tex 被本器整件替换。
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ============================================================
# 值表：V[键] = (值串, 解析串 or None)。LaTeX 串；\( \) 配对、无裸 %（_sanity 断言）。
# ============================================================
V = {}


def put(key, val, note=None):
    assert key not in V, '重复键：%s' % key
    V[key] = (val, note)


LQ = r'$\left|\dfrac{3kq}{8R^{2}}-2E\right|$'   # 练-课时93-16／测-19 钉-5/钉-15 值
KUNIT = r'$<$；$\unit{kg\cdot m^{3}\cdot s^{-4}\cdot A^{-2}}$'   # 拓-040／测-13（钉-14）

# ------------------------------------------------------------
# 【甲】导学件 4 节（课时91~94：预习填空＋判6＋探K例1/变式1×3＋拓展＋评5）
# ------------------------------------------------------------

# ---- 课时91（9.1 电荷——就绪报告 §附录A）----
put('导-课时91-预习填空',
    r'知识点一：正；负；排斥；吸引；电子；负；正；平分；中和；平分。'
    r'知识点二：张开；带；闭合；中和；自由电子；负；正。'
    r'知识点三：创生；保持不变；最小；$1.60\times10^{-19}$；整数倍。')
for i, v in enumerate(['×', '√', '√', '×', '√', '×'], 1):
    put('导-课时91-判%d' % i, v)
put('导-课时91-探1-例1', 'C')
put('导-课时91-探1-变式1', 'D')
put('导-课时91-探2-例1', 'B',
    '中3（定稿指定「导学位」取材件）详解 CD 段接地时序按主脑回执②展开：移 C 前先不断地线，'
    '电荷流回大地，导体不带电；若先断地线再移 C，则导体得异号净电荷（就绪报告 §七-2）。')
put('导-课时91-探2-变式1', 'A 正／B 负；分开后 A 正；先移棒后分＝不带')
put('导-课时91-探3-例1',
    r'(1) 各 $+2.0\times10^{-9}\,\unit{C}$；(2) 甲、丙各 $+1.0\times10^{-9}\,\unit{C}$',
    # 收尾轮B（2026-09-12）照逻辑闸裁（导学件片验收档 §四 K1）链式读消歧——值串零动，仅挂解析行
    r'（(2) 中甲承 (1) 之结果）甲带 $+2.0\times10^{-9}\,\unit{C}$ 与不带电丙接触再分开、电荷平分，'
    r'故甲、丙各 $+1.0\times10^{-9}\,\unit{C}$（非取题干原值 $+6.0\times10^{-9}\,\unit{C}$ 独立分配）。')
put('导-课时91-探3-变式1', r'$+3.0\times10^{-9}\,\unit{C}$')
put('导-课时91-拓展', r'各 $-q$（$\dfrac{+q-3q}{2}=-q$；异种电荷接触后电性由代数和正负决定）')
for i, v in enumerate(['B', 'B', 'C', r'甲、丙各 $+2.0\times10^{-9}\,\unit{C}$', r'$3.0\times10^{10}$ 个'], 1):
    put('导-课时91-评%d' % i, v)

# ---- 课时92（9.2 库仑定律——批2值台账 §一/§二；预习填空＝§二-A1 收尾轮补登）----
put('导-课时92-预习填空',
    r'知识点一：点电荷；理想化模型；正；反；连线；$k\dfrac{q_1q_2}{r^2}$；$9.0\times10^{9}$。'
    r'知识点二：排斥；吸引；真空；静止；绝对值。'
    r'知识点三：矢量和。')
for i, v in enumerate(['×', '√', '√', '×', '√', '×'], 1):
    put('导-课时92-判%d' % i, v)
put('导-课时92-探1-例1', 'B')
put('导-课时92-探1-变式1', 'D（$4F$）')
put('导-课时92-探2-例1', r'C（$\dfrac{4F}{3}$）')   # 钉-7（中4 照用件；选项 A 干扰 F/3 防渗入）
put('导-课时92-探2-变式1', 'D（$0$）')
put('导-课时92-探3-例1',
    r'$0.25\,\unit{N}$，方向沿另外两个点电荷连线的垂直平分线向外（教材例2 照用）')
put('导-课时92-探3-变式1', r'大小 $\dfrac{20kq^{2}}{L^{2}}$，方向沿 AB 连线指向 B')
put('导-课时92-拓展', r'$\dfrac{1}{4}$（$F\propto\dfrac{1}{r^{2}}$）')
for i, v in enumerate(['B', r'A（$7.2\times10^{-4}\,\unit{N}$）', 'B（靠近 A 一侧）',
                       r'$\dfrac{F}{4}$', r'$\dfrac{F}{8}$'], 1):
    put('导-课时92-评%d' % i, v)

# ---- 课时93（9.3 电场 电场强度——批3值台账 §一/§二；预习填空＝§二-A1 收尾轮补登）----
put('导-课时93-预习填空',
    r'知识点一：电场；力；电荷量；$\dfrac{F}{q}$；牛顿每库仑；矢量；正；电场；无关。'
    r'知识点二：$k\dfrac{Q}{r^{2}}$；背离；指向；矢量和。'
    r'知识点三：切线；假想；大；相等；相同；平行直线。')
for i, v in enumerate(['√', '×', '√', '√', '×', '×'], 1):
    put('导-课时93-判%d' % i, v)
put('导-课时93-探1-例1', 'C')
put('导-课时93-探1-变式1', r'$5.0\times10^{3}\,\unit{N/C}$，水平向右')
put('导-课时93-探2-例1', '$0$')
put('导-课时93-探2-变式1', r'$\dfrac{40kq}{L^{2}}$，由甲指向乙')
put('导-课时93-拓展', '$0$（对径微元两两等大反向抵消）')
put('导-课时93-探3-例1', 'B')
put('导-课时93-探3-变式1', 'C（保持不变）')
for i, v in enumerate(['A', 'C（$2E$）', r'B（$\dfrac{3kQ}{L^{2}}$，由 B 指向 A）',
                       r'$1.0\times10^{-4}\,\unit{N}$，水平向右',
                       r'$\dfrac{2kQ}{r^{2}}$，由正电荷指向负电荷'], 1):
    put('导-课时93-评%d' % i, v)

# ---- 课时94（9.4 静电的防止与利用——批4值台账 §四）----
put('导-课时94-预习填空',
    '知识点一：相反；处处为零；外表面；大；电离；尖端放电。'
    '知识点二：没有电荷；静电屏蔽；金属网；接地。'
    '知识点三：导走；接地；静电力。')
for i, v in enumerate(['√', '×', '×', '√', '√', '√'], 1):
    put('导-课时94-判%d' % i, v)
put('导-课时94-探1-例1', 'A')
put('导-课时94-探1-变式1', 'B')
put('导-课时94-探2-例1', 'A')
put('导-课时94-探2-变式1', '静电屏蔽；接地')
put('导-课时94-探3-例1', 'A')
put('导-课时94-探3-变式1', 'B')
put('导-课时94-拓展',
    '光滑表面→电荷密度小→场强弱→不易放电（防漏电损失）；尖端→电荷密集→场强大→易放电'
    '（持续放电引雷中和）——同一「尖端密集→强场→易放电」链的两向运用')
for i, v in enumerate(['A', 'B', 'A', '大；大（强）', '静电屏蔽'], 1):
    put('导-课时94-评%d' % i, v)

# ---- 章末·本章易错过关 5 题（批5a值台账 §一；件型词承导学件，键归导-章末-）----
for i, v in enumerate(['C', 'C', 'A', 'D', 'B'], 1):
    put('导-章末-%d' % i, v)

# ------------------------------------------------------------
# 【乙】练习件 4 节（批1~4 值台账 §一；9.2/9.3 第 2 题位＝略位，无键）
# ------------------------------------------------------------
LX = {
'91': [
 ('B', None), ('B', None), ('A', None), ('B', None), ('A（选非）', None),
 ('带负电／带正电／张开', None),
 ('A', None), ('A', None),
 (r'A（$1.76\times10^{11}\,\unit{C/kg}$）', None),   # 钉-1（比荷亲算载值）
 ('A', None),
 (r'$-\dfrac{q}{4}$', None),
 ('AC', None), ('C', None),
 (r'(1) 甲 $+5.0\times10^{-9}\,\unit{C}$、乙 $-5.0\times10^{-9}\,\unit{C}$；(2) P 带负电', None),
 (r'(1) 甲带负电、乙带正电，$q_{1}=q_{2}$（等量异号·电荷守恒），自由电子由乙侧向靠近玻璃棒的'
  r'甲侧移动；(2) $q_{1}=4.0\times10^{-9}\,\unit{C}$；末态甲＝丙＝$-1.0\times10^{-9}\,\unit{C}$、'
  r'乙＝$+2.0\times10^{-9}\,\unit{C}$；(3) 仍能唯一确定，$q_{1}=4.0\times10^{-9}\,\unit{C}$'
  r'（$+1.0$ 一支与感应链矛盾舍去）', None),
 (r'(1) B＝$-8.0\times10^{-9}\,\unit{C}$；(2) C 可能值＝$+4.0$／$+2.0$／$0$／$-2.0$／$-4.0$'
  r'（$\times10^{-9}\,\unit{C}$），依序「AC→AB／BC→AC／AB→BC 与 AB→AC／AC→BC／BC→AB」；'
  r'(3) 不能（三球代数和恒为 $0$）', None),
],
'92': [
 (r'C（$\dfrac{F}{2}$）', None),
 (r'BC', None),
 ('C', None),
 (r'B（$F_{2}$）', None),
 ('D', None),
 (r'D（$\dfrac{2kQql}{h^{3}}$）', None),
 (r'(1) $F_{1}=12\,\unit{N}$；(2) $q_{2}=6\times10^{-5}\,\unit{C}$；(3) $m_{2}=1.6\,\unit{kg}$', None),
 (r'C（$\sqrt{\dfrac{m_{1}}{m_{2}}}$）', None),
 (r'C（$9:8$）', None),
 (r'(1) $F=\dfrac{kq^{2}}{2d^{2}}$，方向由 B 指向 A；(2) $L=\dfrac{3(\sqrt{3}-1)d}{2}$', None),
 (r'D（$F_{2}=F_{1}\cos^{2}\theta$）', None),
 ('BD', '中13 详解侧勘正：错字「出于」→「处于」（用题必改义务，答案值不涉）。'),
 (r'(1) $m=\dfrac{kq^{2}}{gL^{2}}$；(2) $a=2\sqrt{3}g$', None),
 (r'C（AC:BC＝$m_{2}:m_{1}$ 不变）', None),
 (r'A（$f_{\text{地}}=5\sqrt{3}\,\unit{N}$）',
  r'47题11 详解侧摩擦理据已按钉值门抽验重写（$F=5\sqrt{3}\,\unit{N}\to T=10\,\unit{N}\to'
  r'\mu=\dfrac{\sqrt{3}}{6}$ 四级链全复算在案，批2值台账 §四）；答案值不涉。'),
],
'93': [
 (r'C（$2:\sqrt{3}$）', None),
 ('D', None), ('C', None),
 ('D（P 负 Q 正）', None),
 (r'(1) $F=mg\tan\alpha$；(2) $E_{A}=\dfrac{mg\tan\alpha}{q}$，方向水平向右；'
  r'(3) $Q=\dfrac{mgr^{2}\tan\alpha}{kq}$', None),
 (r'B（$\dfrac{E}{2}$，沿 AO 连线斜向上）', None),
 (r'C（$\sqrt{2}E$）', None),
 (r'A（$1.0\times10^{3}\,\unit{N/C}$，沿 QP 连线由 Q 指向 P）', None),
 (r'A（$3.0\times10^{4}\,\unit{N/C}$，与静电力同向）', None),
 (r'D（$x_{B}=0.4\,\unit{m}$）', '中17 详解侧修复：脱符「xB2」→$x_{B}^{2}$（用题必改义务，答案值不涉）。'),
 (r'B（$\dfrac{7kQ}{36R^{2}}$）', None),
 ('C', None),
 ('B（A 负 B 正，$m_{A}=m_{B}$）', None),
 (r'C（$Q_{1}=-2q$，$Q_{2}=+\sqrt{3}q$，$Q_{3}=-2\sqrt{3}q$）', None),
 (r'C（%s）' % LQ,
  r'冲4 详解侧已按亲算补全版重写（$\sigma_{+}$ 核算＋镜像 $2E$ 记账，批3值台账 §四 双层割补'
  r'数值闭合 1.46923687）；答案值不涉。'),
],
'94': [
 ('B', '简9 详解侧驳论补全：D 项「避雷线吸收导入大地＝尖端放电」系窄判读——吸收导地≠尖端放电'
       '（补全或换 D 为静电复印，两读答案 B 均稳；批4值台账 §六-2②）；答案值不涉。'),
 ('D（近指端 $+$、远端 $-$）', None),
 ('A', None), ('B', None),
 ('垂直；沿导体表面定向移动', None),
 ('处处为零；静电屏蔽；相同', None),
 ('B', None),
 ('B（防尖端＝光滑球形）', None),
 ('A（加湿导走静电）', None),
 ('B', None),
 (r'B（感应场向左；正解式 $\dfrac{4kq}{(2R+l)^{2}}$ 随详解在册）',
  '中24 详解侧勘正：错字「该次」→「该处」（用题必改义务，答案值不涉）。'),
 ('B', None),
 ('B', None),
 ('AC', None),
 ('B（A 不偏离＋B 向右偏）', None),
 (r'(1) 内表面 $-3.0\times10^{-9}\,\unit{C}$（均匀）、外表面 $+3.0\times10^{-9}\,\unit{C}$'
  r'（不均匀，背离 $q_{2}$ 侧密）；(2) $E_{A}=300\,\unit{N/C}$，沿 $q_{1}A$ 连线背离 $q_{1}$；'
  r'$E_{B}=0$；(3) S 闭合或先闭合再断开，外表面均由 $+q_{1}$→约 $0$，壳外不再有由 $q_{1}$ 引起的'
  r'电场；与一直不接地（外表面 $+q_{1}$、壳外有由 $q_{1}$ 引起的电场）成三支对照', None),
],
}
for hh in sorted(LX):
    nums = [1] + list(range(3, 17)) if hh in ('92', '93') else list(range(1, 17))
    assert len(LX[hh]) == len(nums), '课时%s 值数 %d ≠ 题数 %d' % (hh, len(LX[hh]), len(nums))
    for n, (v, note) in zip(nums, LX[hh]):
        put('练-课时%s-%d' % (hh, n), v, note)

# ------------------------------------------------------------
# 【丙】拓展册 46 题（批5b值台账 §一 印面答案；◐改号件按 §一-3 映射取值；
#   拓46＝收尾轮改单选（主脑回执④，批5b §八-1）；钉-10～12 落 拓-036/034/032）
# ------------------------------------------------------------
TUO = [
 ('B', '注记位（A-2 式）——题面不重收，见 9.1 导学件课中探究·探究点二 例1（中3·源Q10），'
       '答案 B 在册（批5b §一-2⑨）。'),
 ('D', None), ('C', None), ('B', None), ('A', None), ('C', None), ('A', None),
 ('D', None), ('A', None), ('A', None), ('D', None), ('B', None), ('C', None),
 ('D', None), ('B', None), ('C', None), ('CD', None), ('BD', None), ('AB', None),
 ('C', None), ('D', None), ('C', None), ('C', None), ('D', None), ('A', None),
 ('D', None), ('B', None), ('B', None), ('A', None), ('A', None), ('D', None),
 (r'A（合场强为 $0$）', None),                       # 钉-12（48题11 §三-C）
 ('B', None),
 (r'B（$\dfrac{3kQ}{l_{0}^{2}}$）', None),           # 钉-11（48题9 印面B＝原C §三-B）
 ('B', None),
 (r'B（$\dfrac{45kq}{16h^{2}}$）', None),            # 钉-10（48题1 镜像法 §三-A）
 ('BC', None), ('BC', None), ('BC', None),
 (KUNIT, None),                                      # 47题1 双空（与测-13 同值）
 ('D', None), ('A', None), ('D', None), ('B', None), ('CD', None),
 (r'D（$b$、$c$ 两点的电场强度均为零）',
  r'收尾轮改单选（主脑回执④）：正解取 49题9 详解正确结论（原B取反式）；干扰项错因——'
  r'A 系「腔内无场线$\Rightarrow$感应场亦为零」半截子理解（合场零恰证 $E_{\text{感}}(c)=-E_{0}\neq0$）、'
  r'B 违静电平衡表面场垂直性（壳面切向分量恒零）、C 违极向聚集增强（$a$ 在场轴：'
  r'$E_{a}=E_{0}(1+2R^{3}/x^{3})>E_{0}$）；题号/源号/组行不动（批5b §八-1）。'),
]
assert len(TUO) == 46, '拓展册值数 %d ≠ 46' % len(TUO)
for n, (v, note) in enumerate(TUO, 1):
    put('拓-%03d' % n, v, note)

# ------------------------------------------------------------
# 【丁】测评卷 19 题（批5b值台账 §四；测13 单位＝§八-2 勘正值；钉-13～15 落 测-10/13/19）
# ------------------------------------------------------------
CE = [
 ('B', None), ('A', None), ('C', None), ('D', None), ('C', None), ('D', None),
 ('B', None), ('D', None), ('AC', None),
 ('CD', None),                                        # 钉-13（Q28 §三-D；B 项口径照源 §七-14）
 ('AC', None),
 ('带负电；带正电；张开', None),
 (KUNIT, None),                                       # 钉-14（47题1 §三-E；§四 转录脱符已勘 §八-2）
 (r'处处为零；$\dfrac{4kq}{(2R+l)^{2}}$；水平向左（指向 $q$ 一侧）', None),
 (r'$-\dfrac{q}{4}$', None),
 (r'$mg\tan\alpha$；$\dfrac{mg\tan\alpha}{q}$，水平向右；$\dfrac{mgr^{2}\tan\alpha}{kq}$', None),
 (r'$12\,\unit{N}$；$6\times10^{-5}\,\unit{C}$；$1.6\,\unit{kg}$', None),
 (r'$\dfrac{kq^{2}}{gL^{2}}$；$2\sqrt{3}g$', None),
 (LQ, None),                                          # 钉-15（冲4 §三-F；与钉-5 双席同值互锁）
]
assert len(CE) == 19, '测评卷值数 %d ≠ 19' % len(CE)
for n, (v, note) in enumerate(CE, 1):
    put('测-%d' % n, v, note)

# ------------------------------------------------------------
# 收尾轮后无占位：PENDING 白名单撤项、缺账 2 槽补登回填（机制保留备用）
# ------------------------------------------------------------
PENDING_KEYS = []
PRE_GAP = []

# ============================================================
# body 组装
# ============================================================
ZH = {1: '一', 2: '二', 3: '三'}


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
    L = ['%% ---- 课时%s（同构槽序：预习填空→诊断判断6→探究点一二三→拓展延伸→课堂评价5）----' % hh]
    b = '导-课时%s-' % hh
    L.append(_mark(b + '预习填空'))
    if hh in PRE_GAP:
        L.append(r'\ansline{预习填空}{PENDING——本课时知识梳理填空值批%s值台账未登记（缺账，'
                 r'见《义务清单.md》§五-1）；槽位同构保留，值补登后回填。}' % hh)
    else:
        L.append(r'\ansline{预习填空}{%s}' % _tex(V[b + '预习填空'][0]))
    for i in range(1, 7):
        L.append(_mark('%s判%d' % (b, i)))
    L.append(r'\ansline{答案}{%s}' % r'\quad '.join(
        '(%d)%s' % (i, _tex(V['%s判%d' % (b, i)][0])) for i in range(1, 7)))
    for t in (1, 2, 3):
        k1, k2 = '%s探%d-例1' % (b, t), '%s探%d-变式1' % (b, t)
        L.append(_mark(k1))
        L.append(_mark(k2))
        L.append(r'\ansline{探究%s}{例1 %s；变式1 %s}' % (ZH[t], _tex(V[k1][0]), _tex(V[k2][0])))
        for k in (k1, k2):
            if V[k][1]:
                L.append(r'\ansline{解析}{%s}' % _tex(V[k][1]))
    L.append(_mark(b + '拓展'))
    L.append(r'\ansline{拓展延伸}{%s}' % _tex(V[b + '拓展'][0]))
    for i in range(1, 6):
        L.append(_mark('%s评%d' % (b, i)))
    L.append(r'\ansline{评价}{%s}' % '；'.join(
        '%d．%s' % (i, _tex(V['%s评%d' % (b, i)][0])) for i in range(1, 6)))
    return L


def items(prefix, nums, note_label='解析'):
    L = []
    for n in nums:
        k = '%s-%d' % (prefix, n)
        L.append(_mark(k))
        L.append(r'\ansitem{%d}{%s}' % (n, _tex(V[k][0])))
        if V[k][1]:
            L.append(r'\ansline{%s}{%s}' % (note_label, _tex(V[k][1])))
    return L


def tuo_items(nums, note_label='解析'):
    L = []
    for n in nums:
        k = '拓-%03d' % n
        L.append(_mark(k))
        L.append(r'\ansitem{%d}{%s}' % (n, _tex(V[k][0])))
        if V[k][1]:
            L.append(r'\ansline{%s}{%s}' % (note_label, _tex(V[k][1])))
    return L


def build_body():
    import datetime
    L = []
    L.append('% ============================================================')
    L.append('% body.tex —— 答案册·P1 轮4 S5【组装器产出】——勿手改（组装S5.py 为唯一值源，防回卷）')
    L.append('%% 生成：%s｜现值键：%d｜缺账占位：%d｜PENDING 键：%d｜对号契约：每键一行 `%%%% pair:键`'
             % (datetime.date.today().isoformat(), len(V), len(PRE_GAP), len(PENDING_KEYS)))
    L.append('% 版式：册首行/章标/节标/分区组行/条目宏在 main.tex＋qp-answ-*（PL1 冻结原样）；'
             '悬挂两档＝单号 5.8mm／双位 7.6mm。')
    L.append('% 收尾轮（2026-09-12）：批5b 65 键回填转实值（白名单撤项、钉-8/钉-9 哨兵转生效、'
             '钉-10～15 六值门生效）；导-课时92/93-预习填空随批2/批3 §二-A1 补登回填。')
    L.append('% ============================================================')
    L.append(r'\setcounter{page}{1}   % 独立册起页 1；装配轮按四本跨本连续页码改写')
    L.append(r'\par\nointerlineskip')
    L.append(r'{\centering\fontsize{16.88pt}{22pt}\selectfont\hejie 参考答案\par}')
    L.append(r'\vspace{2.4mm}')
    L.append(r'\zhangtitle{第九章\quad 静电场及其应用}')

    # ============ 【甲】导学件 ============
    L.append('')
    L.append('% ============================================================')
    L.append('% 【甲】导学件答案（4 节：课时91~94＋章末·本章易错过关 5 题）——整册单 multicols')
    L.append('% （节标入栏内，照数学 M2 【甲】同构；栏断由 multicol 自理，页 OTR 不背块序；')
    L.append(r'%   唯一手动栏断＝章末前 \columnbreak，收尾轮消 9.4 尾行溢栏造成的单行空页）')
    L.append('% ============================================================')
    L.append(r'\begin{multicols}{2}')
    L.append(r'\raggedcolumns')
    L.append(r'\emergencystretch=1em')
    jies = [('9.1\\quad 电荷(导学件答案)', '91'),
            ('9.2\\quad 库仑定律(导学件答案)', '92'),
            ('9.3\\quad 电场 电场强度(导学件答案)', '93'),
            ('9.4\\quad 静电的防止与利用(导学件答案)', '94')]
    for t, hh in jies:
        L.append(r'\jietitle{%s}' % t)
        L.append(r'\qufen{第%s课时}{课前预习（填空＋判断6）＋课中探究（例1×3／变式1×3／拓展延伸）＋课堂评价5}'
                 % {'91': '1', '92': '2', '93': '3', '94': '4'}[hh])
        L += keshi_body(hh)
    L.append(r'\columnbreak   % 收尾轮：9.4 尾行溢栏后章末随栏，消单行空页（试验见 _tmpP1成卷0912/_试验-甲页流，6 页五0）')
    L.append(r'\jietitle{本章易错过关(导学件答案)}')
    L.append(r'\qufen{过关题组}{5 题全单选（卷面题号 1～5，与件面同号）}')
    L += items('导-章末', list(range(1, 6)))
    L.append(r'\end{multicols}')

    # ============ 【乙】练习件 ============
    L.append('')
    L.append(r'\clearpage   % 分本切页：甲→乙（multicols 接续页 OTR 溢高根治；四本各起新页，装配轮跨本页码按本切）')
    L.append('% ============================================================')
    L.append('% 【乙】练习件答案（4 节×16 槽；9.2/9.3 第 2 题位＝略位与件面同构）')
    L.append('% ============================================================')
    jies = [('9.1\\quad 电荷(练习件答案)', '91', None),
            ('9.2\\quad 库仑定律(练习件答案)', '92',
             '第 2 题略——原中4（源Q16）转导学件探究二例1 照用，练习件让位防双收（批2值台账 §五-1）。'),
            ('9.3\\quad 电场 电场强度(练习件答案)', '93',
             '第 2 题略——原简8（源Q48）本轮出列报缺，不凑题（批3值台账 §五-1）。'),
            ('9.4\\quad 静电的防止与利用(练习件答案)', '94', None)]
    for t, hh, lue in jies:
        L.append(r'\jietitle{%s}' % t)
        L.append(r'\begin{multicols}{2}')
        L.append(r'\raggedcolumns')
        L.append(r'\emergencystretch=1em')
        L.append(r'\qufen{基础巩固1～10／综合提升11～14／思维探索15～16}{题号与练习件同号}')
        L.append(r'\setlength{\anshang}{5.8mm}')
        L += items('练-课时' + hh, [1] + ([3] if lue else list(range(2, 10))))
        if lue:
            L.append(r'\ansline{说明}{%s}' % lue)
            L += items('练-课时' + hh, list(range(4, 10)))
        L.append(r'\setlength{\anshang}{7.6mm}   % 题 10 起双位档')
        L += items('练-课时' + hh, list(range(10, 17)))
        L.append(r'\end{multicols}')

    # ============ 【丙】拓展册（收尾轮回填——批5b §一 46 题印面答案） ============
    L.append('')
    L.append(r'\clearpage   % 分本切页：乙→丙')
    L.append('% ============================================================')
    L.append('% 【丙】拓展册答案（拓-001~046 值随批5b 台账 §一 回填；◐改号件按 §一-3 映射；')
    L.append('%   拓46＝收尾轮改单选（主脑回执④·批5b §八-1）；题号与拓展册册面同号）')
    L.append('% ============================================================')
    L.append(r'\jietitle{拓展册(答案)}')
    L.append(r'\begin{multicols}{2}')
    L.append(r'\raggedcolumns')
    L.append(r'\emergencystretch=1em')
    L.append(r'\qufen{9.1\quad 电荷}{册面题号 1～2（注记位 1＋单选 1）}')
    L.append(r'\setlength{\anshang}{5.8mm}')
    L += tuo_items([1, 2])
    L.append(r'\qufen{9.2\quad 库仑定律}{册面题号 3～19（单选 14＋多选 3）}')
    L += tuo_items(list(range(3, 10)))
    L.append(r'\setlength{\anshang}{7.6mm}   % 题 10 起双位档')
    L += tuo_items(list(range(10, 20)))
    L.append(r'\qufen{9.3\quad 电场 电场强度}{册面题号 20～40（单选 17＋多选 3＋填空 1）}')
    L += tuo_items(list(range(20, 41)))
    L.append(r'\qufen{9.4\quad 静电的防止与利用}{册面题号 41～46（单选 4＋多选 2 题位；'
             r'拓46 收尾轮改单选、组行不动）}')
    L += tuo_items(list(range(41, 47)))
    L.append(r'\end{multicols}')

    # ============ 【丁】测评卷（收尾轮回填——批5b §四 19 题值） ============
    L.append('')
    L.append(r'\clearpage   % 分本切页：丙→丁')
    L.append('% ============================================================')
    L.append('% 【丁】测评卷答案（测-1~19 值随批5b 台账 §四 回填；卷面题号 1～19 同号；'
             '卷末速查对账＝收尾轮 §八-5/#16）')
    L.append('% ============================================================')
    L.append(r'\jietitle{单元素养测评卷(一)(答案)}')
    L.append(r'\begin{multicols}{2}')
    L.append(r'\raggedcolumns')
    L.append(r'\emergencystretch=1em')
    L.append(r'\qufen{一、选择题}{本题共 8 小题，每小题 4 分，共 32 分（卷面题号 1～8）}')
    L.append(r'\setlength{\anshang}{5.8mm}')
    L += items('测', list(range(1, 9)))
    L.append(r'\qufen{二、选择题}{本题共 3 小题，每小题 6 分，共 18 分（卷面题号 9～11）}')
    L += items('测', [9])
    L.append(r'\setlength{\anshang}{7.6mm}   % 题 10 起双位档')
    L += items('测', list(range(10, 12)))
    L.append(r'\qufen{三、填空题}{本题共 3 小题，每小题 5 分，共 15 分（卷面题号 12～14）}')
    L += items('测', list(range(12, 15)))
    L.append(r'\qufen{四、解答题}{本题共 5 小题，共 35 分（卷面题号 15～19）}')
    L += items('测', list(range(15, 20)))
    L.append(r'\end{multicols}')
    return L


def main():
    # 两断言模块导入时各自包装 sys.stdout——用中转对象承接、保活其包装防 GC 关底缓冲
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
    print('==== 组装S5：值表 %d 键（缺账占位 %d／PENDING %d）===='
          % (len(V), len(PRE_GAP), len(PENDING_KEYS)))
    _sanity()
    # ① 分册断言（现有件键集＝check_pairs 预期；本器 V＋缺账＝预期集）
    exp = cp.collect_expected()
    gap = {'导-课时%s-预习填空' % hh for hh in PRE_GAP}
    books = ['导-课时91', '导-课时92', '导-课时93', '导-课时94', '导-章末',
             '练-课时91', '练-课时92', '练-课时93', '练-课时94', '拓', '测']
    for p in books:
        want = {k for k in exp if k.startswith(p + '-')}
        got = {k for k in set(V) | gap if k.startswith(p + '-')}
        assert got == want, '分册断言 %s 不等：缺 %s 多 %s' % (p, sorted(want - got)[:8], sorted(got - want)[:8])
        print('分册断言 %s：%d 键相等零缺漏 ✓' % (p, len(want)))
    assert set(exp) == set(V) | gap, '值表＋缺账 ≠ 现有件键集'
    print('缺账占位：%s（收尾轮补登回填后＝空集）' % (sorted(gap) or '无'))
    # ② 钉值门（收尾轮：生效 15 门＝值门 13＋段哨兵 2）
    snap = {k: V[k][0] for k in V}
    gate.run(gate.GATES, snap)
    print('钉值门：生效门 %d 项全过 ✓' % sum(1 for g in gate.GATES
          if g['status'] == '生效'))
    # ③ body.tex
    L = build_body()
    # 栏平衡消 Overfull vbox：条目行后挂微收缩胶（宏族零改动，body 内自医；每行 ≤1.2pt）
    OUT = []
    for x in L:
        OUT.append(x)
        if x.startswith((r'\ansitem', r'\ansline')):
            OUT.append(r'\vskip 0pt minus 1.2pt')
    L = OUT
    marks = [x for x in L if x.startswith('% pair:')]
    assert len(marks) == len(V) + len(gap) + len(PENDING_KEYS), \
        'pair 标记数 %d ≠ 值键 %d＋缺账 %d＋PENDING %d' % (len(marks), len(V), len(gap), len(PENDING_KEYS))
    assert len(set(marks)) == len(marks), 'pair 标记重复'
    f = os.path.join(HERE, 'body.tex')
    with io.open(f, 'w', encoding='utf-8', newline='\n') as w:
        w.write('\n'.join(L) + '\n')
    print('body.tex：%d 行（pair 标记 %d）' % (len(L), len(marks)))
    # ④ 值快照.json（全 208 键）
    sj = os.path.join(HERE, '值快照.json')
    with io.open(sj, 'w', encoding='utf-8', newline='\n') as w:
        json.dump(snap, w, ensure_ascii=False, indent=0, sort_keys=True)
    print('值快照.json：%d 键' % len(snap))
    print('组装完成 ✓（下一步：check_pairs --strict ／ 钉值门 --strict 值快照.json ／ xelatex×2）')


if __name__ == '__main__':
    main()
