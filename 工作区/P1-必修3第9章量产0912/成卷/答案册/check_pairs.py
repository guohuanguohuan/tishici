# -*- coding: utf-8 -*-
r"""check_pairs.py —— 答案册·对号断言（题号集相等零缺漏：答案册题号集 ＝ 四本题号集并集）。

P1 移植自数学 M2 轮4 成卷/答案册/check_pairs.py（同构同号口径照排产单 §一.5/§二.1）。
  四本侧＝【甲】导学件 4 节（课时91~94：预习填空聚合槽＋诊断判断 6＋探究点例1/变式1×3
        ＋拓展延伸＋课堂评价 5；章末·本章易错过关 5 题）∪【乙】练习件 4 节
        （卷面 \tihao{N} 实扫——9.2/9.3 第 2 题位＝略位留空，与件面同构）
        ∪【丙】拓展册（卷面 \tihao{N} 实扫 46 题——收尾轮回填轮起入现有件键集）
        ∪【丁】测评卷（卷面 \ti{N}{ 实扫 19 题——同上）；
  答案册侧＝body.tex 内组装器标记 `% pair:键`（一行一键，键式见《取值映射模板.md》§〇）；
  断言＝现有件键集**相等**零缺漏零多余；
  exit：报告态恒 0，--strict 不等 exit 1。
PENDING 白名单（收尾轮 2026-09-12 已全部撤项——拓 46／测 19 值随批5b 台账回填转实值入实扫集；
  导-课时92/93-预习填空两槽随批2/批3 台账 §二-A1 补登回填、缺账注记撤）：
  PENDING＝空集（机制保留供后续在产件豁免）。
跑法：python check_pairs.py            # 报告态
      python check_pairs.py --strict   # S5 验收态（集合不等 exit 1）
零 git；PL1 样张原目录不动。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CJ = os.path.normpath(os.path.join(HERE, '..'))              # 成卷/

# ============================================================
# PENDING 白名单（收尾轮 2026-09-12 全部撤项——原拓-001～046＋测-1～19 转 collect_expected ④⑤ 实扫）
# ============================================================
PENDING = []

# ---------- 导学件结构常量（批1~4 值台账＋就绪报告附录A 已核；课时 → 槽规格） ----------
# (预习填空, 判断数, 探究点数, 拓展延伸, 评价数)——四件同构：探K＝例1＋变式1。
DAOXUE = {
    '91': dict(pre=True,  pan=6, tan=3, tuo=True,  ping=5),   # 9.1 电荷（值源＝就绪报告 附录A）
    '92': dict(pre=True,  pan=6, tan=3, tuo=True,  ping=5),   # 9.2 库仑定律（批2 §二；预习填空值＝§二-A1 收尾轮补登）
    '93': dict(pre=True,  pan=6, tan=3, tuo=True,  ping=5),   # 9.3 电场 电场强度（批3 §二；预习填空值＝§二-A1 收尾轮补登）
    '94': dict(pre=True,  pan=6, tan=3, tuo=True,  ping=5),   # 9.4 静电的防止与利用（批4 §四）
}
ZHANGMO_N = 5            # 章末·本章易错过关 5 题（批5a §一；件型词承导学件）
LIANJIE_DIRS = {         # 练习件四件目录（\tihao{N} 实扫——与件面同构同号，含略位实态）
    '91': '9.1电荷',
    '92': '9.2库仑定律',
    '93': '9.3电场电场强度',
    '94': '9.4静电的防止与利用',
}
TUO_N = 46               # 拓展册 46 题账（批5b §一；收尾轮回填转实扫）
CE_N = 19                # 测评卷 19 题式（批5b §四；同上）


def _head(text, pat):
    return sorted(set(pat.findall(text)), key=int)


def collect_expected():
    """四本侧·现有件题号集（键式＝册前缀全号；PENDING 白名单键不入本集）。"""
    ks = set()
    # ① 导学件 4 节（课时91~94）
    for hh, sp in DAOXUE.items():
        b = '导-课时%s-' % hh
        if sp['pre']:
            ks.add(b + '预习填空')                       # 课时级聚合槽（不逐空设键）
        ks |= {'%s判%d' % (b, i) for i in range(1, sp['pan'] + 1)}
        for t in range(1, sp['tan'] + 1):
            ks.add('%s探%d-例1' % (b, t))
            ks.add('%s探%d-变式1' % (b, t))
        if sp['tuo']:
            ks.add(b + '拓展')
        ks |= {'%s评%d' % (b, i) for i in range(1, sp['ping'] + 1)}
    # ② 章末·本章易错过关（5 题，键归导学件侧——件型词承导学件，照 M2 批6 章末位先例）
    ks |= {'导-章末-%d' % i for i in range(1, ZHANGMO_N + 1)}
    # ③ 练习件 4 节（件面 \tihao{N} 实扫；9.2/9.3 第 2 题位＝略位，件面无题即册内无键）
    for hh, d in LIANJIE_DIRS.items():
        f = os.path.join(CJ, '练习件', d, 'main.tex')
        nums = _head(open(f, encoding='utf-8').read(), re.compile(r'\\tihao\{(\d+)\}'))
        want = ([1] + list(range(3, 17))) if hh in ('92', '93') else list(range(1, 17))
        assert [int(n) for n in nums] == want, \
            '练习件 %s 题号实态 %s ≠ 预期 %s（略位口径变动须改本断言）' % (d, nums, want)
        ks |= {'练-课时%s-%s' % (hh, n) for n in nums}
    # ④ 拓展册（件面 \tihao{N} 实扫 1~46 连续；键式 拓-NNN 三位号）
    f = os.path.join(CJ, '拓展册', 'main.tex')
    nums = _head(open(f, encoding='utf-8').read(), re.compile(r'\\tihao\{(\d+)\}'))
    assert [int(n) for n in nums] == list(range(1, TUO_N + 1)), \
        '拓展册题号实态 %s ≠ 预期 1~%d 连续（题数/号段变动须改本断言）' % (nums, TUO_N)
    ks |= {'拓-%03d' % int(n) for n in nums}
    # ⑤ 测评卷（卷面 \ti{N}{ 实扫 1~19 连续）
    f = os.path.join(CJ, '测评卷', 'main.tex')
    nums = _head(open(f, encoding='utf-8').read(), re.compile(r'\\ti\{(\d+)\}\{'))
    assert [int(n) for n in nums] == list(range(1, CE_N + 1)), \
        '测评卷题号实态 %s ≠ 预期 1~%d 连续（题数/号段变动须改本断言）' % (nums, CE_N)
    ks |= {'测-%s' % n for n in nums}
    return ks


def collect_answer_side():
    """答案册侧＝body.tex `% pair:键` 标记集（组装器契约，body 头注）。"""
    f = os.path.join(HERE, 'body.tex')
    if not os.path.exists(f):
        return set(), '缺 body.tex'
    return set(re.findall(r'^%\s*pair:(\S+)', open(f, encoding='utf-8').read(), re.M)), ''


def main():
    strict = '--strict' in sys.argv
    exp = collect_expected()
    pend = set(PENDING)
    got, note = collect_answer_side()
    print('四本侧·现有件键集：%d｜PENDING 白名单：%d｜答案册侧 pair 标记：%d %s'
          % (len(exp), len(pend), len(got), note))
    miss = sorted(exp - got)                    # 四本有册无（缺）
    extra = sorted(got - exp - pend)            # 册有四本无、且非白名单（多）
    pendmiss = sorted(pend - got)               # PENDING 占位键缺席（白名单在位性）
    print('缺（四本有册无）：%d %s' % (len(miss), miss[:12]))
    print('多（册有四本无·非白名单）：%d %s' % (len(extra), extra[:12]))
    print('PENDING 缺席：%d %s' % (len(pendmiss), pendmiss[:12]))
    if not got:
        print('骨架态：body.tex 尚未注入值（组装器产出后复跑）')
    ok = (not miss and not extra and not pendmiss)
    print('集合断言：%s（现有件相等零缺漏%s；PENDING 全在位%s）[%s]'
          % ('✓ 通过' if ok else '✗ 不通过',
             '✓' if not miss and not extra else '✗',
             '✓' if not pendmiss else '✗',
             'strict' if strict else '报告态'))
    if strict and not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
