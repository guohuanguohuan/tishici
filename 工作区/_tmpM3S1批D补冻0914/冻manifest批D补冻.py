# -*- coding: utf-8 -*-
r"""冻manifest批D补冻.py —— M3 S1 批D 课时14~17 G5 补冻重冻器（工序件，跑于 _tmpM3S1批D补冻0914/）。

口径＝工作区/_tmpM3S1批D0913/冻manifest批D.py＋_tmpM3S1批E补冻0913/冻manifest批E补冻.py 同法
（提取规则与 对号门.py 单一约定），单点变更回冲制（canonical键名总表 §四.1）：
换 manifest 冻时戳与哈希＋新增变更注记。
  键 66→71／31→36／45→50／37→42：`2章-导-课时1N-G1~G5` 五键追加
  （片内键序＝导 G1~G5→练 01~16→拓区，总表 §二枚举序；拓区复合键实幅照批D 初冻不动）；
  源件换版＝定稿件末「导学 G5 补产」小节（补产抽验 6/6 一致）；存量键值/题面不动。
  原 期望值 扩展字段（拓展键数/拓区多选数/拓区多选键/备注/抽核）逐字承继，仅改
  键数/导学键数/多选复核与 对号门期望 句内键数三元组。
跑法：python 冻manifest批D补冻.py [--stamp 2026-09-14T01:06:00+0800]   （跑于 值复核批D补冻.py 之后）
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913'))
TMUB = os.path.join(ROOT, '成卷', '题面库')
MANI = os.path.join(TMUB, 'manifest')
DING = os.path.join(ROOT, '定稿')
sys.path.insert(0, TMUB)
import 对号门  # noqa: E402

SLICES = {
    '课时14': ('课时14-2.6.2双曲线性质', '批D-课时14-2.6.2双曲线性质.md', 71),
    '课时15': ('课时15-2.7.1抛物线方程', '批D-课时15-2.7.1抛物线方程.md', 36),
    '课时16': ('课时16-2.7.2抛物线性质', '批D-课时16-2.7.2抛物线性质.md', 50),
    '课时17': ('课时17-2.8①压轴综合一', '批D-课时17-2.8①压轴综合一.md', 42),
}
GK = [u'2章-导-%s-G%d']
PRE_STAMP = '2026-09-13T23:12:00+0800'
NEW_NOTE_U = (u'课时14 五键系新命·14-命A~E·0914命制入槽，15/16/17 存量取材（源见片头席说明）')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def freeze(slice_name, spec, stamp):
    title, src_rel, n_new = spec
    qp = os.path.join(TMUB, '%s.md' % title)
    ap = os.path.join(TMUB, '%s-答案侧.md' % title)
    sp = os.path.join(DING, src_rel)
    for p in (qp, ap, sp):
        assert os.path.exists(p), '缺件：%s' % p
    old = json.load(open(os.path.join(MANI, '%s.manifest.json' % slice_name), encoding='utf-8'))
    assert old['冻时戳'] == PRE_STAMP, '%s 补冻前冻时戳=%s≠%s（基线错位？）' % (slice_name, old['冻时戳'], PRE_STAMP)
    qs = 对号门.parse_questions(qp)
    ans = 对号门.parse_answers(ap)
    qkeys = [k for k, _, _ in qs]
    akeys = [k for k, _, _ in ans]
    assert qkeys == akeys, '%s 键序不等：题面侧%d vs 答案侧%d' % (slice_name, len(qkeys), len(akeys))
    gkeys = ['2章-导-%s-G%d' % (slice_name, i) for i in range(1, 6)]
    assert qkeys[:5] == gkeys, '%s G5 键序不在列首（canonical §二枚举序）' % slice_name
    assert qkeys[5:] == old['键序'], '%s 存量键序被扰动（应＝初冻键序原样后置）' % slice_name
    assert len(qkeys) == n_new and sum(1 for k in qkeys if '-导-' in k) == 5 \
        and sum(1 for k in qkeys if '-练-' in k) == 16, \
        '%s 期望值不符：键%d/导5/练16' % (slice_name, len(qkeys))
    daov = dict((k, (v, d)) for k, v, d in ans)
    per = {}
    for k, _, qtext in qs:
        v, d = daov[k]
        assert v and d, '%s 空值或缺详解锚点' % k
        per[k] = {'题面': sha(qtext.encode('utf-8')), '答案': sha((v + '\n' + d).encode('utf-8'))}
    for k in old['键序']:  # 存量键哈希必须逐键不动（补冻未误伤）
        assert per[k] == old['逐键哈希'][k], '%s 存量键哈希漂移：%s' % (slice_name, k)
    multi = [k for k, t, _ in qs if t == '多选' and '-拓-' not in k]
    exp = dict(old['期望值'])
    exp_old = old['期望值']
    assert multi == exp_old['多选键'] and len(multi) == exp_old['多选数'], \
        '%s 正文多选漂移：%s vs %s' % (slice_name, multi, exp_old['多选键'])
    exp['键数'] = len(qkeys)
    exp['导学键数'] = 5
    exp['对号门期望'] = exp_old['对号门期望'].replace(
        '（%d=%d=%d' % (exp_old['键数'], exp_old['键数'], exp_old['键数']),
        '（%d=%d=%d' % (n_new, n_new, n_new))
    assert str(n_new) in exp['对号门期望'] and str(exp_old['键数']) not in exp['对号门期望'], \
        '%s 对号门期望句键数未换净' % slice_name
    note = (u'G5 补冻 %s：导学 2章-导-%s-G1~G5 追加冻结（键%d→%d，导0→5，拓区复合键实幅不动）；'
            u'源件换版＝定稿件末「导学 G5 补产」小节（补产抽验 6/6 一致，'
            u'_tmpM3补产抽验0913/抽验报告-批DG5.md；%s）；'
            u'单点变更回冲制＝canonical键名总表 §四.1，下游回冲（值快照/钉值门/装配逐层复跑）；'
            u'初冻 %s（练16＋拓区，彼版源件不含 G5 补产）。'
            % (stamp, slice_name, exp_old['键数'], n_new, NEW_NOTE_U, PRE_STAMP))
    mani = {}
    for kk, vv in old.items():  # 承继原字段序与未列字段（章/批/键式/备注/抽核等）
        mani[kk] = vv
        if kk == '冻时戳':
            mani['变更注记'] = note
    mani['冻时戳'] = stamp
    mani['源件sha256'] = sha(open(sp, 'rb').read())
    mani['题面侧sha256'] = sha(open(qp, 'rb').read())
    mani['答案侧sha256'] = sha(open(ap, 'rb').read())
    mani['键序'] = qkeys
    mani['逐键哈希'] = per
    mani['期望值'] = exp
    out = os.path.join(MANI, '%s.manifest.json' % slice_name)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(mani, f, ensure_ascii=False, indent=1)
    print('%s 补冻重冻 ✓｜键%d→%d（导5＋练16＋拓%d）｜正文多选%d｜冻时戳=%s｜manifest→%s'
          % (slice_name, exp_old['键数'], n_new, n_new - 21, len(multi), stamp,
             os.path.relpath(out, ROOT)))
    re.compile('')  # noqa: 保留 re 引用一致性（无实义）


def main():
    args = sys.argv[1:]
    stamp = None
    if '--stamp' in args:
        i = args.index('--stamp')
        stamp = args[i + 1]
        args = args[:i] + args[i + 2:]
    stamp = stamp or '2026-09-14T01:06:00+0800'
    for n in args or list(SLICES):
        freeze(n, SLICES[n], stamp)


if __name__ == '__main__':
    main()
