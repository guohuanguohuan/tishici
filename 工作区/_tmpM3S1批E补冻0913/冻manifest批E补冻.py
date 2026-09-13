# -*- coding: utf-8 -*-
r"""冻manifest批E补冻.py —— M3 S1 批E 课时18/19 G5 补冻重冻器（工序件，跑于 _tmpM3S1批E补冻0913/）。

口径＝工作区/_tmpM3S1批E0913/冻manifest批E.py 同法（提取规则与 对号门.py 单一约定），
单点变更回冲制（canonical键名总表 §四.1）：换 manifest 冻时戳与哈希＋变更注记。
  键 16→21：`2章-导-课时1N-G1~G5` 五键追加（片内键序＝导 G1~G5→练 01~16，总表 §二枚举序）；
  源件换版＝定稿件末「导学 G5 补产」小节（补产抽验 4/4 一致）；存量 16 键值/题面不动。
跑法：python 冻manifest批E补冻.py [--stamp 2026-09-13T23:37:00+0800]   （跑于 值复核批E补冻.py 之后）
"""
import hashlib
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913'))
TMUB = os.path.join(ROOT, '成卷', '题面库')
MANI = os.path.join(TMUB, 'manifest')
DING = os.path.join(ROOT, '定稿')
sys.path.insert(0, TMUB)
import 对号门  # noqa: E402

SLICES = {
    '课时18': ('课时18-2.8②压轴综合二', '批E-课时18-2.8②压轴综合二.md'),
    '课时19': ('课时19-章末总结与复习', '批E-课时19-章末总结与复习.md'),
}
EXP = {  # 键数, 导学(2章-导-), 练习(2章-练-), 多选期望
    '课时18': (21, 5, 16, 1),
    '课时19': (21, 5, 16, 2),
}
PRE_STAMP = '2026-09-13T23:05:00+0800'


def sha(t):
    return hashlib.sha256(t).hexdigest() if isinstance(t, bytes) else hashlib.sha256(t.encode('utf-8')).hexdigest()


def freeze(slice_name, spec, stamp):
    title, src_rel = spec
    qp = os.path.join(TMUB, '%s.md' % title)
    ap = os.path.join(TMUB, '%s-答案侧.md' % title)
    sp = os.path.join(DING, src_rel)
    for p in (qp, ap, sp):
        assert os.path.exists(p), '缺件：%s' % p
    qs = 对号门.parse_questions(qp)
    ans = 对号门.parse_answers(ap)
    qkeys = [k for k, _, _ in qs]
    akeys = [k for k, _, _ in ans]
    assert qkeys == akeys, '%s 键序不等：题面侧%d vs 答案侧%d' % (slice_name, len(qkeys), len(akes))
    daov = dict((k, (v, d)) for k, v, d in ans)
    per = {}
    for k, _, qtext in qs:
        v, d = daov[k]
        assert v and d, '%s 空值或缺详解锚点' % k
        per[k] = {'题面': sha(qtext), '答案': sha(v + '\n' + d)}
    n, ng, nl, nm = EXP[slice_name]
    multi = [k for k, t, _ in qs if t == '多选']
    assert len(qkeys) == n and sum(1 for k in qkeys if '-导-' in k) == ng \
        and sum(1 for k in qkeys if '-练-' in k) == nl and len(multi) == nm, \
        '%s 期望值不符：键%d/导%d/练%d/多选%d' % (slice_name, len(qkeys), ng, nl, len(multi))
    assert qkeys[:5] == ['2章-导-%s-G%d' % (slice_name, i) for i in range(1, 6)], \
        '%s G5 键序不在列首（canonical §二枚举序）' % slice_name
    assert len(multi) <= 4, '%s 多选门破门' % slice_name
    mani = {
        '片': slice_name,
        '章': 'M3选必1第2章',
        '键式': '2章-<册>-<位>-<槽>（位＝课时18/课时19/衔接）',
        '冻时戳': stamp,
        '变更注记': 'G5 补冻 %s：导学 2章-导-%s-G1~G5 追加冻结（键16→21，导0→5）；源件换版＝定稿件末'
                  '「导学 G5 补产」小节（补产抽验 4/4 一致，_tmpM3补产抽验0913/抽验报告-批EG5.md）；'
                  '单点变更回冲制＝canonical键名总表 §四.1，下游回冲（值快照/钉值门/装配逐层复跑）；'
                  '初冻 %s（练16，此版源件不含 G5 补产）。' % (stamp, slice_name, PRE_STAMP),
        '源件': src_rel,
        '源件sha256': sha(open(sp, 'rb').read()),
        '题面侧': os.path.basename(qp),
        '题面侧sha256': sha(open(qp, 'rb').read()),
        '答案侧': os.path.basename(ap),
        '答案侧sha256': sha(open(ap, 'rb').read()),
        '键序': qkeys,
        '逐键哈希': per,
        '期望值': {
            '键数': n,
            '导学键数': ng,
            '练习键数': nl,
            '多选数': len(multi),
            '多选键': multi,
            '对号门期望': '题面侧键集＝答案侧锚点集＝manifest键清单（%d=%d=%d，序一致零缺漏）；'
                      '多选门≤4（本片%d，%s）；题面全文/答案块哈希逐一相符；片冻后不可变，变更→重冻→下游回冲'
                      % (n, n, n, len(multi), '合规' if len(multi) < 4 else '触顶合规'),
        },
    }
    out = os.path.join(MANI, '%s.manifest.json' % slice_name)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(mani, f, ensure_ascii=False, indent=1)
    print('%s 补冻重冻 ✓｜键%d（导%d＋练%d）｜多选%d｜冻时戳=%s｜manifest→%s'
          % (slice_name, n, ng, nl, len(multi), stamp, os.path.relpath(out, ROOT)))


def main():
    args = sys.argv[1:]
    stamp = None
    if '--stamp' in args:
        i = args.index('--stamp')
        stamp = args[i + 1]
        args = args[:i] + args[i + 2:]
    stamp = stamp or datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:00+0800')
    for n in args or list(SLICES):
        freeze(n, SLICES[n], stamp)


if __name__ == '__main__':
    main()
