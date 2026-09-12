# -*- coding: utf-8 -*-
r"""钉值门.py —— 答案册·钉值门配置＋引擎（自数学 M2 成卷/答案册/钉值门.py 参数化移植，防回卷）。

门表 GATES＝数据（定位键·断言·回卷串·出处·状态）；引擎 run(gates, values)＝对 {键: 值串} 逐门
断言，任一不符 raise 钉值门触发（中止组装待人工处置）；自检 selftest()＝正测（种子值零漂移）
＋负测（回卷串必拦＋段哨兵缺键必拦）。P1 轮 0 改值——钉值系各批「钉值门抽验·必抽席」亲算值的
回归锁（防详解干扰项/串位值/数量级错渗入答案位）。
收尾轮（2026-09-12）：钉-8/钉-9 段哨兵随批5b 回填**转生效**（|拓|＝46／|测|＝19 键段核）；
批5b §三 六项亲算（A/B/C↔拓36/34/32、D/E/F↔测10/13/19）落为**生效值门 钉-10～钉-15**。
跑法：python 钉值门.py            # 门表读数＋内置自检（正测/负测）
      python 钉值门.py --strict 值快照.json   # S5 实装：对值快照逐门断言，触发则 exit 2
零 git；PL1 样张原目录不动。
"""
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 门表（状态：生效＝S5 注入即断言；收尾轮回填后全表生效、0 待回填）
# 键式承《取值映射模板.md》§〇；断言式＝in 子串（R 仅当 regex=True）；
# 回卷串＝防渗入的旧读/干扰值（负测用：把它当期望必拦）；
# 段哨兵＝want/rollback 皆 None＋sentinel=(前缀, 题数, 键式)——断言值快照该段键集恰为号段全集。
# ============================================================
GATES = [
    dict(id='钉-1', key='练-课时91-9',
         want=r'1.76\times10^{11}', rollback=r'5.69\times10^{-12}',
         note='比荷 e/mₑ＝1.76×10¹¹ C/kg（批1 钉值门抽验：C 项干扰数值 5.69×10⁻¹² kg/C 来源坐实'
              '——防干扰项渗入答案位）',
         src='练习件/批1值台账.md §三', status='生效'),
    dict(id='钉-2', key='练-课时91-14',
         want=r'+5.0\times10^{-9}', rollback=r'2.5\times10^{-9}',
         note='q₁＝2×2.5×10⁻⁹＝+5.0×10⁻⁹ C（守恒互证；防未乘 2 错算回卷）',
         src='练习件/批1值台账.md §三', status='生效'),
    dict(id='钉-3', key='练-课时91-16',
         want=r'\+4\.0.*\+2\.0.*0.*-2\.0.*-4\.0', rollback=r'+6.0', regex=True,
         sample=r'+4.0／+2.0／0／-2.0／-4.0（×$10^{-9}\,\unit{C}$）',
         note='C 可能值＝+4.0／+2.0／0／−2.0／−4.0（×10⁻⁹ C，六序枚举 Fraction 精确核定；'
              '防枚举缺支/越界值回卷）',
         src='练习件/批1值台账.md §三', status='生效'),
    dict(id='钉-4', key='练-课时92-16',
         want=r'5\sqrt{3}', rollback=r'\dfrac{\sqrt{3}}{6}',
         note='f_地＝5√3 N（47题11 四级链全复算；rollback＝链中 μ 值 √3/6——防串位）',
         src='批2值台账.md §四', status='生效'),
    dict(id='钉-5', key='练-课时93-16',
         want=r'\dfrac{3kq}{8R^{2}}-2E', rollback=r'\dfrac{3kq}{8R^{2}}+2E',
         note='|3kq/8R²−2E|（冲4 双层割补数值闭合 1.46923687；防符号错型）',
         src='批3值台账.md §四', status='生效'),
    dict(id='钉-6', key='练-课时94-16',
         want=r'300\,\unit{N/C}', rollback=r'30\,\unit{N/C}',
         note='E_A＝kq₁/r²＝300 N/C（Python 复算 27/0.09＝300.0；防 10 倍数量级错）',
         src='批4值台账.md §三', status='生效'),
    dict(id='钉-7', key='导-课时92-探2-例1',
         want=r'\dfrac{4F}{3}', rollback=r'\dfrac{F}{3}',
         note='中4 照用件答案 C（4F/3）（批2 §二；rollback＝选项 A 干扰 F/3——防选项值渗入答案位）',
         src='批2值台账.md §二/§五-1', status='生效'),
    dict(id='钉-8', key='拓-001～拓-046（段哨兵）',
         want=None, rollback=None, sentinel=('拓-', 46, '拓-%03d'),
         note='集合哨兵：拓展册 46 题账——值快照 |拓|＝46 且键段恰＝拓-001~046（防在产值/号段'
              '回潮与缺漏；收尾轮 2026-09-12 批5b 回填转生效）',
         src='批5b值台账.md §一/§八-1', status='生效'),
    dict(id='钉-9', key='测-1～测-19（段哨兵）',
         want=None, rollback=None, sentinel=('测-', 19, '测-%d'),
         note='集合哨兵：测评卷 19 题式——值快照 |测|＝19 且键段恰＝测-1~19（防题数/号段回潮；'
              '收尾轮 2026-09-12 批5b 回填转生效）',
         src='批5b值台账.md §四；成卷/就绪报告.md §六', status='生效'),
    dict(id='钉-10', key='拓-036',
         want=r'\dfrac{45kq}{16h^{2}}', rollback=r'\dfrac{9kq}{4h^{2}}',
         note='48题1 镜像法合场强 45kq/16h²（批5b §三-A 亲算：9kq/16h²＋9kq/4h²＝45kq/16h²；'
              'rollback＝q 单独贡献分项值——防分项值渗入答案位）',
         src='批5b值台账.md §三-A', status='生效'),
    dict(id='钉-11', key='拓-034',
         want=r'\dfrac{3kQ}{l_{0}^{2}}', rollback=r'\dfrac{3kQ}{2l_{0}^{2}}',
         note='48题9 双正四面体 E_max＝3kQ/l₀²（批5b §三-B 亲算；印面B＝原C；'
              'rollback＝选项 D 干扰值 3kQ/(2l₀²)）',
         src='批5b值台账.md §三-B', status='生效'),
    dict(id='钉-12', key='拓-032',
         want=r'合场强为 $0$', rollback=r'\dfrac{kQ}{4R^{2}}',
         note='48题11 半球壳＋轴上点荷 P 点合场强 0（批5b §三-C 亲算；'
              'rollback＝半球壳分量 kQ/4R²——防分量值代合值）',
         src='批5b值台账.md §三-C', status='生效'),
    dict(id='钉-13', key='测-10',
         want=r'CD', rollback=r'AC',
         note='Q28 双绳靠墙接触后＝CD（批5b §三-D 亲算：距离增大/库仑力增大/拉力无关三判闭合；'
              'rollback＝同卷测9/测11 值 AC——防多选字母串位）',
         src='批5b值台账.md §三-D', status='生效'),
    dict(id='钉-14', key='测-13',
         want=r's^{-4}\cdot A^{-2}', rollback=r's^{-4}\cdot A^{2}',
         note='47题1 k 单位＝kg·m³·s⁻⁴·A⁻²（批5b §三-E 亲算；rollback＝缺负号 A²——'
              '批5b §四 转录脱符系台账侧笔误，卷末速查印面本就正确，收尾轮 §八-2 勘正）',
         src='批5b值台账.md §三-E/§八-2', status='生效'),
    dict(id='钉-15', key='测-19',
         want=r'8R^{2}}-2E', rollback=r'8R^{2}}+2E',
         note='冲4 割补 |3kq/8R²−2E|（批5b §三-F 亲算，端到端 1.46923687 闭合；'
              'rollback＝符号错型 +2E；与钉-5 双席同值互锁）',
         src='批5b值台账.md §三-F', status='生效'),
]


class GateTrip(AssertionError):
    """钉值门触发——组装中止（禁静默再生），待人工处置。"""


def run(gates, values):
    """对 {键: 值串} 逐门断言（段哨兵对键集断言）。返回触发列表（空＝全过）；任一生效门不符即 raise。"""
    tripped = []
    for g in gates:
        if g['status'] != '生效':
            continue
        if g['want'] is None:
            sent = g.get('sentinel')
            if not sent:
                continue
            pre, n, fmt = sent
            want_keys = {fmt % i for i in range(1, n + 1)}
            got_keys = {k for k in values if k.startswith(pre)}
            if got_keys != want_keys:
                miss = sorted(want_keys - got_keys)[:4]
                extra = sorted(got_keys - want_keys)[:4]
                tripped.append((g, '段哨兵不符：|段|＝%d（应 %d）缺 %s 多 %s'
                                % (len(got_keys), n, miss, extra)))
            continue
        got = values.get(g['key'])
        if got is None:
            tripped.append((g, '缺值（键不在值快照——组装器漏取或键式不符）'))
            continue
        hit = g['want'] in got if not g.get('regex') else re.search(g['want'], got)
        if not hit:
            tripped.append((g, '值不含钉值串（疑素材回卷旧值 %s）' % (g['rollback'] or '？')))
    if tripped:
        g, why = tripped[0]
        raise GateTrip('钉值门触发：%s（%s）%s——中止组装待人工处置'
                       % (g['key'], g['id'], why))
    return tripped


def _seed():
    """正测种子：值门用 want（regex 门用 sample）；段哨兵用号段全集占位值。"""
    seed = {g['key']: g.get('sample', g['want']) for g in GATES if g['want'] is not None}
    for g in GATES:
        if g['want'] is None and g.get('sentinel'):
            pre, n, fmt = g['sentinel']
            for i in range(1, n + 1):
                seed.setdefault(fmt % i, 'seed')   # 不覆盖值门种子（钉-10~15 落同段）
    return seed


def selftest():
    """正测零漂移＋负测真拦（照数学排产单 §五A2 口径，随册复跑）。"""
    seed = _seed()
    live = [g for g in GATES if g['status'] == '生效']
    n_ok = len(live)
    run(live, seed)
    print('正测：生效门 %d 项全过（零漂移）＝True' % n_ok)
    neg = 0
    for g in live:
        bad = dict(seed)
        if g['want'] is None and g.get('sentinel'):      # 段哨兵负测＝抽掉一键
            del bad[g['sentinel'][2] % g['sentinel'][1]]
        else:                                             # 值门负测＝灌回卷串
            bad[g['key']] = g['rollback'] or ''
        try:
            run([g], bad)
        except GateTrip as e:
            neg += 1
            print('负测：%-22s 灌旧值/抽键 %-16s → 真拦 ✓（%s…）'
                  % (g['key'], (g['rollback'] or '∅')[:16], str(e)[:38]))
        else:
            print('负测：%-22s 未拦 ✗✗ 门失效' % g['key'])
    assert neg == n_ok, '负测存在未拦门'
    print('负测：%d/%d 真拦' % (neg, n_ok))


if __name__ == '__main__':
    print('==== 钉值门表（%d 项：生效 %d／待回填 %d）===='
          % (len(GATES), sum(1 for g in GATES if g['status'] == '生效'),
             sum(1 for g in GATES if g['status'] != '生效')))
    for g in GATES:
        print(' [%s] %-4s %-22s want=%-24s rollback=%s' % (
            g['status'], g['id'], g['key'],
            (g['want'] or '哨兵' if g.get('sentinel') else g['want'] or '—')[:24],
            (g['rollback'] or '—')[:16]))
    print('\n==== 自检 ====')
    selftest()
    if len(sys.argv) > 1 and sys.argv[1] == '--strict':
        snap = json.load(open(sys.argv[2], encoding='utf-8'))
        run(GATES, snap)
        print('\n--strict：值快照 %d 键逐门断言全过' % len(snap))
