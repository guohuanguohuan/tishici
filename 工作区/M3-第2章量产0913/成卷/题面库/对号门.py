# -*- coding: utf-8 -*-
r"""对号门.py —— M3 题面库·对号断言（v2 新锚点 `% ans:` 版，M2 check_pairs 为底改造）。

口径（规格书-v1 v2 变更节6＋军师账审 §七）：
  对号 gate 改「题面库键 ↔ 件内答案键」：每片断言三集合相等——
    ①题面侧 `### <键>｜…` 头键集（canonical 序）
    ②答案侧 `% ans:<键>` 锚点集
    ③freeze manifest 键清单（含逐键哈希＋文件哈希＋期望值复核）
  另锚点安全：锚点行必须整行仅键（防答案值串进锚点行）；多选门每课时正文 ≤4。
跑法：python 对号门.py             # 全部已冻片（报告态恒 exit 0）
      python 对号门.py --strict   # 验收态（任一断言不等 exit 1）
      python 对号门.py --片 课时06 [--strict]
未冻片（批A/批C/批D/批E/命制15）不在本门射程：S2 前总闸全量一次跑齐（canonical键名总表 §四.3）。
"""
import hashlib
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
TMUB = os.path.join(ROOT, '成卷', '题面库')
MANI = os.path.join(TMUB, 'manifest')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from 冻manifest import parse_questions, parse_answers, sha  # 提取规则单一源
except ImportError:
    sys.path.insert(0, os.path.join(ROOT, '..'))  # 兜底：工作区级不成立时由调用方并入工序目录
    raise


def check_slice(name, strict=False):
    qp = os.path.join(TMUB, '%s.md' % name)
    ap = os.path.join(TMUB, '%s-答案侧.md' % name)
    mp = os.path.join(MANI, '%s.manifest.json' % name)
    bad = []
    if not (os.path.exists(qp) and os.path.exists(ap) and os.path.exists(mp)):
        return False, ['缺件：题面/答案/manifest 任一缺失（%s）' % name]
    mani = json.load(open(mp, encoding='utf-8'))
    qs = parse_questions(qp)
    ans = parse_answers(ap)
    # 锚点安全：答案侧原文逐行扫锚点，锚点行不得携带值内容
    raw = open(ap, encoding='utf-8').read().splitlines()
    anchor_lines = [ln for ln in raw if ln.startswith('% ans:')]
    unsafe = [ln for ln in anchor_lines if not re.match(r'^% ans:\S+\s*$', ln)]
    if unsafe:
        bad.append('锚点行带值污染：%d 行' % len(unsafe))
    qkeys = [k for k, _, _ in qs]
    akeys = [k for k, _, _ in ans]
    mkeys = mani['键序']
    if qkeys != akeys:
        bad.append('题面侧↔答案侧键序不等：缺%s 多%s' % (sorted(set(qkeys) - set(akes))[:8],
                                                  sorted(set(akes) - set(qkeys))[:8]))
    if qkeys != mkeys:
        bad.append('题面侧↔manifest 键序不等：缺%s 多%s' % (sorted(set(qkeys) - set(mkeys))[:8],
                                                    sorted(set(mkeys) - set(qkeys))[:8]))
    # 逐键哈希
    daov = dict((k, (v, d)) for k, v, d in ans)
    for k, _, qtext in qs:
        h = mani['逐键哈希'].get(k)
        if not h:
            bad.append('manifest 缺键哈希：%s' % k)
            continue
        v, d = daov.get(k, ('', ''))
        if sha(qtext) != h['题面']:
            bad.append('题面哈希漂移：%s' % k)
        if sha(v + '\n' + d) != h['答案']:
            bad.append('答案块哈希漂移：%s' % k)
    # 文件级哈希（片不可变协议）
    for tag, path in (('题面侧', qp), ('答案侧', ap)):
        if sha(open(path, 'rb').read()) != mani['%ssa256' % tag]:
            bad.append('%s 文件漂移（片冻后被动过→须重冻该片）' % tag)
    # 期望值复核
    exp = mani['期望值']
    multi = [k for k, t, _ in qs if t == '多选']
    if len(qkeys) != exp['键数'] or len(multi) != exp['多选数']:
        bad.append('期望值漂移：键%d/多选%d vs 期望%d/%d' % (len(qkeys), len(multi), exp['键数'], exp['多选数']))
    if len(multi) > 4:
        bad.append('多选门破门（>4）：%s' % multi)
    ok = not bad
    print('【%s】键%d（导%d＋练%d）｜多选%d｜断言：%s'
          % (name, len(qkeys), exp['导学键数'], exp['练习键数'], len(multi),
             '相等零缺漏 ✓' if ok else '✗'))
    for b in bad:
        print('  - %s' % b)
    if strict and not ok:
        sys.exit(1)
    return ok, bad


def main():
    args = sys.argv[1:]
    strict = '--strict' in args
    names = []
    if '--片' in args:
        names = [args[args.index('--片') + 1]]
    else:
        names = sorted(f[:-len('.manifest.json')] for f in os.listdir(MANI) if f.endswith('.manifest.json'))
    if not names:
        print('骨架态：manifest 目录空（冻manifest.py 跑后复跑本门）')
        return
    allok = all(check_slice(n, strict)[0] for n in names)
    total = sum(json.load(open(os.path.join(MANI, '%s.manifest.json' % n), encoding='utf-8'))['期望值']['键数']
                for n in names)
    print('合计：%d 片｜%d 键｜全集断言：%s（%s）'
          % (len(names), total, '相等零缺漏 ✓' if allok else '不等 ✗', 'strict' if strict else '报告态'))
    if strict and not allok:
        sys.exit(1)


if __name__ == '__main__':
    main()
