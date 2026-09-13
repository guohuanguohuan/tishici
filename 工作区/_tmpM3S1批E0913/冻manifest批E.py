# -*- coding: utf-8 -*-
r"""冻manifest批E.py —— M3 S1 批E 三片冻结器（工序件，跑于 _tmpM3S1批E0913/）。

口径＝工作区/_tmpM3S1首批0913/冻manifest.py 同法（提取规则与 对号门.py 单一约定）：
  题面侧 `### <键>｜…` 起块（题面全文排除【注】行/空行/---）；答案侧 `% ans:<键>`＋值＋详解行。
批E 差异：三片非「导5＋练16」构形——课时18/19 仅练习16（导学 G1~G5 无定稿载体），
衔接节＝导11（G5 5＋探6）＋练16，故期望值按片给定，不套 5+16 断言。
跑法：python 冻manifest批E.py [--stamp 2026-09-13T23:05:00+0800]
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
    '衔接节': ('衔接节', '批E-衔接节.md'),
}
EXP = {  # 键数, 导学(2章-导-), 练习(2章-练-), 多选期望, 多选键前缀核对
    '课时18': (16, 0, 16, 1),
    '课时19': (16, 0, 16, 2),
    '衔接节': (27, 11, 16, 0),
}


def sha(t):
    return hashlib.sha256(t).hexdigest() if isinstance(t, bytes) else hashlib.sha256(t.encode('utf-8')).hexdigest()


def freeze(slice_name, spec, stamp):
    title, src_rel = spec
    qp = os.path.join(TMUB, '%s.md' % title)
    ap = os.path.join(TMUB, '%s-答案侧.md' % title)
    sp = os.path.join(DING, src_rel)
    for p in (qp, ap, sp):
        assert os.path.exists(p), '缺件：%s' % p
    qs, ans = 对号门.parse_questions(qp), 对号门.parse_answers(ap)
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
    assert len(multi) <= 4, '%s 多选门破门' % slice_name
    mani = {
        '片': slice_name,
        '章': 'M3选必1第2章',
        '键式': '2章-<册>-<位>-<槽>（位＝课时18/课时19/衔接）',
        '冻时戳': stamp,
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
    print('%s 冻结 ✓｜键%d（导%d＋练%d）｜多选%d｜manifest→%s'
          % (slice_name, n, ng, nl, len(multi), os.path.relpath(out, ROOT)))


def main():
    args = sys.argv[1:]
    stamp = None
    if '--stamp' in args:
        i = args.index('--stamp')
        stamp = args[i + 1]
        args = args[:i] + args[i + 2:]
    stamp = stamp or datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
    for n in args or list(SLICES):
        freeze(n, SLICES[n], stamp)


if __name__ == '__main__':
    main()
