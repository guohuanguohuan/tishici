# -*- coding: utf-8 -*-
r"""check_pairs.py —— 答案册·对号断言（题号集相等零缺漏：答案册题号集 ＝ 四本题号集并集）。

口径（排产单 §一.5/§二.1-2.2④）：
  四本侧＝导学件（课中例/变式＋课堂评价＋预习判断＋衔接-1~29＋章末）∪ 练习件（课时×16）
        ∪ 拓展册（拓-001~160）∪ 卷件（测-1~19＋滚A/B-1~16）；
  答案册侧＝body.tex 内组装器标记 `% pair:键`（一行一键，键式见《取值映射模板.md》§〇）；
  断言＝两侧集合**相等**（零缺漏零多余），报告缺/多清单；exit：报告态恒 0，--strict 不等 exit 1。
四本侧取数源（机器可读，S5 组装时以成品定稿为准复跑）：
  练习件 ← `成卷/题面库/课时NN-*.md`「### 第N题」；衔接 ← `题面库/衔接节.md`「### 衔接-N」；
  拓展册 ← `题面库/拓展册.md`「### 拓-NNN」；卷件 ← `卷件值台账.md` §一表＋`命制/命制-滚X-16题.md`；
  导学件 ← 结构常量（批1~6值台账已核探点数，见 取值映射模板 §一）＋衔接/章末常量。
跑法：python check_pairs.py            # 报告态（骨架期：答案册侧 0 键属正常，恒 exit 0）
      python check_pairs.py --strict   # S5 验收态（集合不等 exit 1）
      python check_pairs.py --拓159    # 装配轮撤重后档（拓-057 撤下，靶 159）
骨架件：排布断言（衔接组内四约束/练习件难度槽序）留 S5 扩展位（§TODO）。
"""
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CJ = os.path.normpath(os.path.join(HERE, '..'))            # 成卷/
M2 = os.path.normpath(os.path.join(CJ, '..'))              # M2 根/
TMUB = os.path.join(CJ, '题面库')

# ---------- 导学件结构常量（批1~6值台账已核：课时 → (例1×n, 变式槽列表)） ----------
# S5 修正（以成品定稿为准复跑——本文件头注口径）：变式槽改显式 (探点, 变式名) 列表。
#   课时04 批2 台账 §1.2 实态＝变式2×2 落探究一/探究三（尾页平衡补位位），
#   原常量 ['变式1']*3+['变式2']*2 按枚举探号错配成探4/探5（件无探4/探5），照实态改正。
DAOXUE = {                      # 课时NN: (例1×n, [(探点, 变式名), ...])
    '01': (4, [(i, '变式1') for i in range(1, 5)]),
    '02': (5, [(i, '变式1') for i in range(1, 6)]),
    '03': (4, [(i, '变式1') for i in range(1, 5)]),
    '04': (3, [(1, '变式1'), (1, '变式2'), (2, '变式1'), (3, '变式1'), (3, '变式2')]),
    '05': (5, [(i, '变式1') for i in range(1, 6)]),
    '06': (5, [(i, '变式1') for i in range(1, 6)]),
    '07': (5, [(i, '变式1') for i in range(1, 6)]),
    '08': (5, [(i, '变式1') for i in range(1, 6)]),
    '09': (5, [(i, '变式1') for i in range(1, 6)]),
    '10': (5, [(i, '变式1') for i in range(1, 6)]),
}
XIANJIE_N, ZHANGMO = 29, (['例%d' % i for i in range(1, 13)]
                          + ['变式%d' % i for i in range(1, 13)] + ['高考%d' % i for i in range(1, 5)])


def _head(text, pat):
    return sorted(set(pat.findall(text)), key=int)


def _contig(nums, lo, hi, what):
    assert [int(n) for n in nums] == list(range(lo, hi + 1)), '%s 题号非 %d~%d 连续：%s' % (what, lo, hi, nums)


def collect_expected(tuo159=False):
    """四本侧题号集（键式＝册前缀全号）。"""
    ks = set()
    # ① 导学件
    for hh, (nl, vspec) in DAOXUE.items():
        # 例1×n／变式N：中文号条目按探究点位区分（「例1」每探点同名——册内按探点分组行文，
        # 键含探点序：导-课时NN-探K-例1／变式N）
        for i in range(1, nl + 1):
            ks.add('导-课时%s-探%d-例1' % (hh, i))
        for tp, sp in vspec:
            ks.add('导-课时%s-探%d-%s' % (hh, tp, sp))
        ks |= {'导-课时%s-评%d' % (hh, i) for i in range(1, 6)}
        ks |= {'导-课时%s-判%d' % (hh, i) for i in range(1, 6)}
        ks.add('导-课时%s-预习填空' % hh)                 # 课时级聚合槽（不逐空设键）
    ks |= {'导-衔接-%d' % i for i in range(1, XIANJIE_N + 1)}
    ks |= {'导-章末-%s' % s for s in ZHANGMO}
    # ② 练习件（题面库逐题头）
    for f in sorted(glob.glob(os.path.join(TMUB, '课时*-*.md'))):
        hh = re.search(r'课时(\d{2})-', os.path.basename(f)).group(1)
        nums = _head(open(f, encoding='utf-8').read(), re.compile(r'^### 第(\d+)题', re.M))
        _contig(nums, 1, 16, '题面库 %s' % os.path.basename(f))
        ks |= {'练-课时%s-%s' % (hh, n) for n in nums}
    # ③ 拓展册（题面库逐题头；装配轮撤重后键集以重编号版为准，--拓159 为撤下档）
    tuo = _head(open(os.path.join(TMUB, '拓展册.md'), encoding='utf-8').read(),
                re.compile(r'^### 拓-(\d{3})', re.M))
    _contig(tuo, 1, 160, '题面库拓展册')
    if tuo159:
        tuo = [n for n in tuo if n != '057']
        assert len(tuo) == 159
    ks |= {'拓-%s' % n for n in tuo}
    # ④ 卷件
    j = open(os.path.join(CJ, '卷件值台账.md'), encoding='utf-8').read()
    sec1 = j.split('## 一')[1].split('## 二')[0]
    nums = _head(sec1, re.compile(r'^\| (\d{1,2}) \| (?:单选|多选|填空|解答)', re.M))
    _contig(nums, 1, 19, '卷件值台账 §一 测评')
    ks |= {'测-%s' % n for n in nums}
    for xa in ('A', 'B'):
        f = os.path.join(M2, '命制', '命制-滚%s-16题.md' % xa)
        nums = _head(open(f, encoding='utf-8').read(), re.compile(r'^## 命制-滚%s-(\d{1,2})（' % xa, re.M))
        _contig(nums, 1, 16, '命制-滚%s' % xa)
        ks |= {'滚%s-%s' % (xa, n) for n in nums}
    return ks


def collect_answer_side():
    """答案册侧＝body.tex `% pair:键` 标记集（组装器契约，body 头注）。"""
    f = os.path.join(HERE, 'body.tex')
    if not os.path.exists(f):
        return set(), '缺 body.tex'
    # S5 修正：答案册侧键＝册前缀全串（导-/练-/拓-/测-/滚A-/滚B-），非纯整数——去 int 排序键
    return set(re.findall(r'^%\s*pair:(\S+)', open(f, encoding='utf-8').read(), re.M)), ''


def main():
    tuo159 = '--拓159' in sys.argv
    strict = '--strict' in sys.argv
    exp = collect_expected(tuo159)
    got, note = collect_answer_side()
    print('四本侧键集：%d（拓%d档）｜答案册侧 pair 标记：%d %s'
          % (len(exp), 159 if tuo159 else 160, len(got), note))
    miss = sorted(exp - got)
    extra = sorted(got - exp)
    print('缺（四本有册无）：%d %s' % (len(miss), miss[:12]))
    print('多（册有四本无）：%d %s' % (len(extra), extra[:12]))
    if not got:
        print('骨架态：body.tex 尚未注入值（S5 组装器产出后复跑）')
    ok = (not miss and not extra)
    print('集合断言：%s（%s）' % ('相等零缺漏 ✓' if ok else '不等 ✗', 'strict' if strict else '报告态'))
    # §TODO（S5 扩展位）：①排布断言——衔接组内四约束（-3 先于 -9/-14 等，汇总 §3.2）＋练习件难度槽序；
    # ②钉值门联动——`钉值门.py --strict 值快照.json` 随本断言同跑（A2 双断言）；
    # ③答案册侧副验——\ansitem/\dansitem 实计数 vs pair 标记数（防标记漏行）。
    if strict and not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
