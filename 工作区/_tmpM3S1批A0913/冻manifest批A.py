# -*- coding: utf-8 -*-
r"""冻manifest批A.py —— M3 S1 批A 片（课时01~05）冻结器（工序件，跑于 _tmpM3S1批A0913/）。

口径：与 工作区/_tmpM3S1首批0913/冻manifest.py 同一提取规则（改片格式须与 对号门.py 同改）；
批A 增量＝①canonical 期望键表硬断言（含 04 前移6＝E11~E16、05 回填6＝E17~E22 与空号席跳号、T1 占位不计）；
②导学5＋练习16＋拓展键数逐片断言；③多选期望照 定稿汇总§十一（01:2／02:1／03:0／04:0／05:0）。
跑法：python 冻manifest批A.py [--stamp 2026-09-13T22:30:00+0800]
"""
import hashlib
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913'))
TMUB = os.path.join(ROOT, '成卷', '题面库')
MANI = os.path.join(TMUB, 'manifest')
DING = os.path.join(ROOT, '定稿')


def gkeys(prefix, g=5):
    return ['2章-导-%s-G%d' % (prefix, i) for i in range(1, g + 1)]


def ekeys(prefix, nums):
    return ['2章-练-%s-E%d' % (prefix, n) for n in nums]


def tkeys(prefix, nums):
    return ['2章-拓-%s-T%d' % (prefix, n) for n in nums]


SLICES = {
    '课时01': ('坐标法', '批A-课时01-坐标法.md',
               gkeys('课时01') + ekeys('课时01', range(1, 17)) + tkeys('课时01', [1, 2]), 2),
    '课时02': ('倾斜角与斜率', '批A-课时02-倾斜角与斜率.md',
               gkeys('课时02') + ekeys('课时02', range(1, 17)) + tkeys('课时02', [1, 2, 3, 4]), 1),
    '课时03': ('方向向量与法向量', '批A-课时03-方向向量与法向量.md',
               gkeys('课时03') + ekeys('课时03', range(1, 17)), 0),
    '课时04': ('点斜式与斜截式', '批A-课时04-点斜式与斜截式.md',
               gkeys('课时04') + ekeys('课时04', range(1, 17)) + tkeys('课时04', [1]), 0),
    '课时05': ('两点式与一般式', '批A-课时05-两点式与一般式.md',
               gkeys('课时05') + ekeys('课时05', [2, 3, 5, 6, 7, 9, 10, 11, 15, 16, 17, 18, 19, 20, 21, 22])
               + tkeys('课时05', [6, 7, 8]), 0),
}
EXP_TUO = {'课时01': 2, '课时02': 4, '课时03': 0, '课时04': 1, '课时05': 3}


def sha(t):
    if isinstance(t, bytes):
        return hashlib.sha256(t).hexdigest()
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


def parse_questions(path):
    text = open(path, encoding='utf-8', newline='').read()
    out, cur = [], None
    for ln in text.splitlines():
        if ln.startswith('### '):
            if cur:
                out.append(cur)
            head = ln[4:]
            key = head.split('｜')[0].strip()
            kinds = [s for s in head.split('｜')[1:] if s in ('单选', '多选', '填空', '解答')]
            cur = [key, kinds[0] if kinds else '', []]
        elif cur is not None:
            if ln.strip() == '---':
                out.append(cur)
                cur = None
            elif ln.startswith('【注】') or not ln.strip():
                continue
            else:
                cur[2].append(ln)
    if cur:
        out.append(cur)
    return [(k, t, '\n'.join(body)) for k, t, body in out]


def parse_answers(path):
    text = open(path, encoding='utf-8', newline='').read()
    out, cur = [], None
    for ln in text.splitlines():
        m = re.match(r'^% ans:(\S+)\s*$', ln)
        if m:
            if cur:
                out.append(cur)
            cur = [m.group(1), '', '']
        elif cur is not None:
            if ln.startswith('值：'):
                cur[1] = ln[2:].strip()
            elif ln.startswith('详解：'):
                cur[2] = ln[3:].strip()
    if cur:
        out.append(cur)
    return out


def freeze(slice_name, title, src_name, exp_keys, multi_exp, stamp=None):
    qp = os.path.join(TMUB, '%s-%s.md' % (slice_name, title))
    ap = os.path.join(TMUB, '%s-%s-答案侧.md' % (slice_name, title))
    sp = os.path.join(DING, src_name)
    for p in (qp, ap, sp):
        assert os.path.exists(p), '缺件：%s' % p
    qs, ans = parse_questions(qp), parse_answers(ap)
    qkeys = [k for k, _, _ in qs]
    akeys = [k for k, _, _ in ans]
    assert qkeys == akeys, '%s 键序不等：题面侧%d vs 答案侧%d\n缺%s\n多%s' % (
        slice_name, len(qkeys), len(akes), sorted(set(qkeys) - set(akes))[:6], sorted(set(akes) - set(qkeys))[:6])
    assert qkeys == exp_keys, '%s 键序 ≠ canonical 期望键表：\n缺%s\n多%s' % (
        slice_name, [k for k in exp_keys if k not in qkeys], [k for k in qkeys if k not in exp_keys])
    daov = dict((k, (v, d)) for k, v, d in ans)
    per = {}
    for k, _, qtext in qs:
        v, d = daov[k]
        assert v, '%s 空值' % k
        assert d, '%s 缺详解锚点' % k
        per[k] = {'题面': sha(qtext), '答案': sha(v + '\n' + d)}
    multi = [k for k, t, _ in qs if t == '多选']
    n_g = sum(1 for k in qkeys if '-导-' in k)
    n_l = sum(1 for k in qkeys if '-练-' in k)
    n_t = sum(1 for k in qkeys if '-拓-' in k)
    exp = {
        '键数': len(qkeys),
        '导学键数': n_g,
        '练习键数': n_l,
        '拓展键数': n_t,
        '多选数': len(multi),
        '多选键': multi,
        '批A基线注': '0913命制入槽（01-E15/E16、03-E12~E16）＋0913收口§六前移6/回填6（04-E11~E16、05-E17~E22）落盘后实态；'
                  '批A合计115题次＝G25＋E80＋T10（05-T1占位行不计题）；任务串旧读数108口径（21/25/16/16/30-占位1）'
                  '系命制入槽与前移6施工前快照，已按实态升账，见 canonical更新指令单。',
        '对号门期望': '题面侧键集＝答案侧锚点集＝manifest键清单（%d=%d=%d，序一致零缺漏）；'
                  '多选门≤4（本片%d，%s）；题面全文/答案块哈希逐一相符；片冻后不可变，变更→重冻→下游回冲'
                  % (len(qkeys), len(akeys), len(qkeys), len(multi), '合规' if len(multi) <= 4 else '破门'),
    }
    assert n_g == 5 and n_l == 16, '%s 导学/练习键数异常：%d/%d' % (slice_name, n_g, n_l)
    assert n_t == EXP_TUO[slice_name], '%s 拓展键数 %d ≠ 期望 %d' % (slice_name, n_t, EXP_TUO[slice_name])
    assert len(multi) == multi_exp, '%s 多选数 %d ≠ §十一期望 %d' % (slice_name, len(multi), multi_exp)
    stamp = stamp or '2026-09-13T22:30:00+0800'
    mani = {
        '片': slice_name,
        '章': 'M3选必1第2章',
        '批': '批A',
        '键式': '2章-<册>-课时<NN>-<槽>',
        '冻时戳': stamp,
        '源件': src_name,
        '源件sha256': sha(open(sp, 'rb').read()),
        '题面侧': os.path.basename(qp),
        '题面侧sha256': sha(open(qp, 'rb').read()),
        '答案侧': os.path.basename(ap),
        '答案侧sha256': sha(open(ap, 'rb').read()),
        '键序': qkeys,
        '逐键哈希': per,
        '期望值': exp,
    }
    out = os.path.join(MANI, '%s.manifest.json' % slice_name)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(mani, f, ensure_ascii=False, indent=1)
    print('%s 冻结 ✓｜键%d（导%d＋练%d＋拓%d）｜多选%d｜manifest→%s'
          % (slice_name, exp['键数'], n_g, n_l, n_t, exp['多选数'], os.path.relpath(out, ROOT)))


def main():
    args = sys.argv[1:]
    stamp = None
    if '--stamp' in args:
        i = args.index('--stamp')
        stamp = args[i + 1]
        args = args[:i] + args[i + 2:]
    names = args or list(SLICES)
    for n in names:
        title, src, exp_keys, multi_exp = SLICES[n]
        freeze(n, title, src, exp_keys, multi_exp, stamp)


if __name__ == '__main__':
    main()
