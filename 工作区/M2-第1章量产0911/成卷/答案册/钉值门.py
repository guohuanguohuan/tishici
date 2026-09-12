# -*- coding: utf-8 -*-
r"""钉值门.py —— 答案册·钉值门配置＋引擎（自 `导学件答案册-v1/组装body.py` ①a 参数化移植，防 6g 回卷）。

原门（v11 勘误0911）：`assert r'\sqrt{7}' in recs['探究点九·变式1']['ans']`——不符即中止、禁静默再生。
本件参数化三件事：
  ① 门表 GATES＝数据（定位键·断言·回卷串·出处·状态）——新增钉值只改表不改引擎；
  ② 引擎 run(gates, values)＝对 {键: 值} 逐门断言，任一不符 raise 钉值门触发（中止组装待人工处置）；
  ③ 自检 selftest()＝正测（种子值零漂移）＋负测（回卷串必拦）——排产单 §五A2「正测零漂移＋负测真拦，
     随册复跑」；S5 组装流程＝组装器取值 → run(值快照) → 过门后写 body.tex。
跑法：python 钉值门.py            # 门表读数＋内置自检（正测/负测）
      python 钉值门.py --strict 值快照.json   # S5 实装：对值快照逐门断言，触发则 exit 2
零 git；样张原目录不动。
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 门表（状态：生效＝S5 注入即断言｜待钉＝值源双制挂账/装配期豁免，到点转生效）
# 键式承《取值映射模板.md》§〇；断言式＝in 子串（R 仅当 regex=True）；
# 回卷串＝历史上出过/防再生的旧值（负测用：把它当期望必拦）。
# ============================================================
GATES = [
    dict(id='钉-1', key='导-课时02-探五变式1',
         want=r'\sqrt{7}', rollback=r'\dfrac{\sqrt{13}}{2}',
         note='v11 P0 勘误钉值（折叠矩形变式1 √13/2→√7/2，补角错五方一致）——原门钉 v11 冻结件探九变式1，'
              '量产线同文迁移课时02 探五；量产组装须随带（S2就绪报告§三·探究点五行）',
         src='看板七十五/七十六；S2就绪报告.md §三', status='生效'),
    dict(id='钉-2', key='练-课时01-10',
         want=r'\sqrt{7}', rollback=r'\sqrt{13}',
         note='答案册 v1 键 √13/2 系错值——练习件钉 √7/2（h=√3/2、足距 1、BD²=7/4），答案册侧修键勿照抄旧键',
         src='练习件/批1值台账.md §一值表/登记1', status='生效'),
    dict(id='钉-3', key='导-课时03-探四例1',
         want='B', rollback='120',
         note='探究四 例1 答案值钉 B（亲算与讲部【答案】一致）；讲部详解 C 项「夹角 120°」与亲算不符'
              '（实算 cos=−√2/4≈110.7°）——详解改字随义务清单§二，答案值不涉；负测拦「120」防详解瑕值渗入答案位',
         src='导学件/批1值台账.md §2.5 ★钉值门登记', status='生效'),
    dict(id='钉-4', key='测-1',
         want='D', rollback='A',
         note='测评 Q1 三点共线→不能构成三角形＝D；答案表初排误填 A 经独立重算自纠（卷件钉值门病例）',
         src='卷件值台账.md §四登记7', status='生效'),
    dict(id='钉-5', key='导-衔接-9',
         want='816/25', rollback='32.64',
         note='源同值两制留分数一制，小数版注销（两制并存禁入册）',
         src='导学件/批3值台账.md §2.3 表', status='生效'),
    dict(id='钉-6', key='拓-057',
         want=None, rollback='拓-057',
         note='集合哨兵：装配轮撤拓-057 撤重（160→159）后，答案册拓号集**不得含拓-057**且 |拓|＝159——'
              '防在产 160 件旧集回卷（在产期豁免，装配轮撤重后转生效）',
         src='练习件/批3值台账.md 登记③；组名总表-v1.md §修⑥③', status='待装配轮生效'),
    dict(id='钉-7', key='练-课时09-7(2)',
         want=None, rollback=None,
         note='复习C·4(2) 二面角符号两制并存挂账（钝制 −2√7/7／取锐 2√7/7）——随 S5 以教材答案栏钉一，'
              '钉后本门转生效（want＝钉定制，rollback＝落选制）',
         src='练习件/批3值台账.md §一题7；清稿执行记录 §五#4', status='待钉'),
    # ---- 修键轮0912 追加（钉-8~钉-13，S7 逻辑闸六键离全量转生效门）----
    # 拓-159/哨兵兼容：新门键式全为 练-课时NN-N，不触拓号集、不触钉-6（拓-057 缺席哨兵）与钉-7；
    # run() 仍只验生效门，--拓159 档断言与钉值门正交。组装S5.py 内嵌值表未随轮同步——若以旧表重跑，
    # 本批生效门即触发中止（设计内防回潮，禁静默再生）。
    dict(id='钉-8', key='练-课时04-2',
         want=r'(-8,8,4)', rollback=r'(-6,8,4)',
         note='修键轮0912 改值钉（(1) AB→=B−A，x 分量 −6−2=−8；旧值 −6 系直抄 B 的 x 分量，灌回必拦）——'
              '(2) 小问 (−6,−9,−2) 双方一致不涉',
         src='逻辑闸/练习-课4-6-glm.md 键离#1；逻辑闸/修键轮执行记录.md §二-1', status='生效'),
    dict(id='钉-9', key='练-课时04-10',
         want=r'2,2,\dfrac{4}{3}', rollback=r'2,2,\dfrac{2}{3}',
         note='修键轮0912 改值钉（EB=2EB₁⇒E 近 B₁，z_E=4/3→选 D；旧键 C(2,2,2/3) 与台账自注 EB=4/3 '
              '自相矛盾，灌回必拦）',
         src='逻辑闸/练习-课4-6-glm.md 键离#2；逻辑闸/修键轮执行记录.md §二-2', status='生效'),
    dict(id='钉-10', key='练-课时04-13',
         want=r'A_{1}(-1,-2,0)', rollback=r'A_{1}(4,1,-1)',
         note='修键轮0912 改值钉（体对角线配对 A↔C₁、B↔D₁、C↔A₁、D↔B₁；钉「A₁↔(−1,−2,0)」一处标签绑定'
              '即锁全配对，旧值 X₁=2M−X 标签错位灌回必拦；坐标集两案相同故须钉标签）——同题旁证＝导-章末-变式5',
         src='逻辑闸/练习-课4-6-glm.md 键离#3；逻辑闸/修键轮执行记录.md §二-3', status='生效'),
    dict(id='钉-11', key='练-课时04-15',
         want=r'4\sqrt{2}', rollback=r'[4,4\sqrt{3}]',
         note='修键轮0912 改值钉（(3) 离散三点集 {4,4√2,4√3}——钉中值 4√2：区间旧值 [4,4√3] 必缺该分量，'
              '灌回必拦；命制件题3 答案节原文与测-19 同为离散集）',
         src='逻辑闸/练习-课4-6-glm.md 键离#4；逻辑闸/修键轮执行记录.md §二-4', status='生效'),
    dict(id='钉-12', key='练-课时05-12',
         want=r'\dfrac{2\sqrt{13}}{3}', rollback=r'(1)2；(2)1',
         note='修键轮0912 维持钉（键离归因＝盲解臂无图误按棱配置，台账值经面对角线配置复算成立**免改**——'
              '题面(2)明言「面对角线」AB/DC；钉 2√13/3 防棱配置误值 (1)2／(2)1 回潮）',
         src='逻辑闸/练习-课4-6-glm.md 键离#5；逻辑闸/修键轮执行记录.md §二-5', status='生效'),
    dict(id='钉-13', key='练-课时06-9',
         want=r'150^{\circ}', rollback=r'120^{\circ}',
         note='修键轮0912 改值钉（cos⟨BA′,D′C′⟩=−3/(2√3)=−√3/2→150°，与 AB/AD 取值无关；旧值 120° 系 '
              'D′C′ 误作 DC′（⟨BA′,DC′⟩=120°），灌回必拦）',
         src='逻辑闸/练习-课4-6-glm.md 键离#6；逻辑闸/修键轮执行记录.md §二-6', status='生效'),
    # ---- 拓上补对分·修键轮0912 追加（钉-14，拓展上册拓-053 改值钉）----
    # 键式为拓号：拓-053 在在产 159 档内（撤号哨兵只盯拓-057），不触钉-6；--拓159 对号档不受影响。
    dict(id='钉-14', key='拓-053',
         want=r'\dfrac{1}{4}', rollback=r'\left(\dfrac{1}{2},1\right)',
         note='拓上修键轮0912 改值钉（折叠保距 ⟹ 2fx=1 ⟹ t=1/(2f)∈(1/4,1/2)；旧值 (1/2,1) 系 t=1/f 漏因子 2，'
              'f=2 端验 |D′F|²=3≠4=|DC|² 不容，灌回必拦）',
         src='逻辑闸/拓展-上-glm.md 键离#3；逻辑闸/拓上-补对分-修键-glm.md 件一', status='生效'),
    # ---- S7 修键·单题0912 追加（钉-15，拓展册拓-009 改值钉）----
    # 键式为拓号：拓-009 在在产 159 档内（撤号哨兵只盯拓-057），不触钉-6；--拓159 对号档不受影响。
    dict(id='钉-15', key='拓-009',
         want=r'0', rollback=r'1',
         note='S7 修键轮0912 改值钉（AB₁→·BC₁→＝(AB→＋BB₁→)·(BC→＋CC₁→)＝AB→·BC→＋1＝2·1·cos120°＋1＝0；'
              '旧值 1 疑 BA·BC 未取负——⟨AB→,BC→⟩＝180°−∠ABC＝120° 非 60°，灌回必拦）',
         src='逻辑闸/修键-拓009-glm.md；逻辑闸双臂＋复算臂三臂一致', status='生效'),
    # ---- S7 修键·双题0912 追加（钉-16~钉-17，导学件课05 预习空1＋课06 评价5 第二解改值钉）----
    # 键式为导学件聚合槽 导-课时NN-预习填空／导-课时NN-评N：不触拓号集、不触钉-6（拓-057 哨兵）与钉-7；
    # --拓159 对号档不受影响。组装S5.py 内嵌值表未随轮同步——以旧表重跑本两门即触发中止（设计内防回潮）。
    dict(id='钉-16', key='导-课时05-预习填空',
         want=r'\overrightarrow{DC}', rollback=r'\overrightarrow{AD}',
         note='S7 修键轮0912 改值钉（四边形ABCD 为平行四边形⇔AB→＝DC→⇔A+C＝B+D，与同条目公式及评3/判5 亲算'
              '自洽；旧值 AD→ 按 AB→＝AD→ 导出 B＝D 不成立——D→C 键位笔误，灌回必拦）',
         src='逻辑闸/导学-课4-6-glm.md 键离2；逻辑闸/修键-课05空-课06评5-qwen.md', status='生效'),
    dict(id='钉-17', key='导-课时06-评5',
         want=r'(-3,3,-3)', rollback=r'(-3,3,-1)',
         note='S7 修键轮0912 改值钉（t=−2 支 N＝M−2v＝(1,1,1)−(4,−2,4)＝(−3,3,−3)，|MN|＝√36＝6 ✓；旧值 '
              '(−3,3,−1) 给 |MN|＝√24≠6 且 MN→ 与 v→ 不共线，双重不容——z 分量笔误，灌回必拦；亲算行 N=M±2v 本无误）',
         src='逻辑闸/导学-课4-6-glm.md 键离3；逻辑闸/修键-课05空-课06评5-qwen.md', status='生效'),
]


class GateTrip(AssertionError):
    """钉值门触发——组装中止（禁静默再生），待人工处置。"""


def run(gates, values):
    """对 {键: 值串} 逐门断言。返回触发列表（空＝全过）；任一生效门不符即 raise。"""
    tripped = []
    for g in gates:
        if g['status'] != '生效' or g['want'] is None:
            continue
        got = values.get(g['key'])
        if got is None:
            tripped.append((g, '缺值（键不在值快照——组装器漏取或键式不符）'))
            continue
        hit = g['want'] in got if not g.get('regex') else __import__('re').search(g['want'], got)
        if not hit:
            tripped.append((g, '值不含钉值串（疑素材回卷旧值 %s）' % (g['rollback'] or '？')))
    if tripped:
        g, why = tripped[0]
        raise GateTrip('钉值门触发：%s（%s）%s——中止组装待人工处置'
                       % (g['key'], g['id'], why))
    return tripped


def selftest():
    """正测零漂移＋负测真拦（排产单 §五A2 口径）。"""
    seed = {g['key']: g['want'] for g in GATES if g['want'] is not None}
    seed['导-课时02-探五变式1'] = r'\( - \dfrac{2\sqrt{7}}{7} \)'   # 钉-1 按册内式形含 \sqrt{7} 即过
    ok = run([g for g in GATES if g['status'] == '生效'], seed) is not None or True
    print('正测：生效门 %d 项全过（零漂移）＝%s' % (sum(1 for g in GATES if g['status'] == '生效'), ok))
    neg = 0
    for g in [g for g in GATES if g['status'] == '生效']:
        bad = dict(seed)
        bad[g['key']] = g['rollback'] or ''   # 灌回卷旧值→必拦
        try:
            run([g], bad)
        except GateTrip as e:
            neg += 1
            print('负测：%-14s 灌旧值 %-14s → 真拦 ✓（%s…）' % (g['key'], (g['rollback'] or '∅')[:14], str(e)[:38]))
        else:
            print('负测：%-14s 未拦 ✗✗ 门失效' % g['key'])
    assert neg == sum(1 for g in GATES if g['status'] == '生效'), '负测存在未拦门'
    print('负测：%d/%d 真拦' % (neg, neg))


if __name__ == '__main__':
    print('==== 钉值门表（%d 项：生效 %d／待钉 %d）===='
          % (len(GATES), sum(1 for g in GATES if g['status'] == '生效'),
             sum(1 for g in GATES if g['status'] != '生效')))
    for g in GATES:
        print(' [%s] %-4s %-16s want=%-10s rollback=%s' % (g['status'], g['id'], g['key'],
              (g['want'] or '—')[:10], (g['rollback'] or '—')[:14]))
    print('\n==== 自检 ====')
    selftest()
    if len(sys.argv) > 1 and sys.argv[1] == '--strict':
        snap = json.load(open(sys.argv[2], encoding='utf-8'))
        run(GATES, snap)
        print('\n--strict：值快照 %d 键逐门断言全过' % len(snap))
