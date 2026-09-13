# -*- coding: utf-8 -*-
r"""对号门.py —— M3 题面库·对号断言（v2 新锚点 `% ans:` 版，M2 check_pairs 为底改造）。

口径（规格书-v1 v2 变更节6＋军师账审-收口轮0913 §七）：
  对号 gate 改「题面库键 ↔ 件内答案键」：每片断言三集合相等——
    ①题面侧 `### <键>｜…` 头键集（canonical 序）
    ②答案侧 `% ans:<键>` 锚点集
    ③freeze manifest 键清单（含逐键哈希＋文件哈希＋期望值复核）
  提取规则（与 工作区/_tmpM3S1首批0913/冻manifest.py 单一约定，改片格式须两件同改）：
    题面侧：`### <键>｜…` 起块；题面全文＝块内除【注】行、空行、`---` 分隔行外全部行（前置提示行属印面，保留）。
    答案侧：`% ans:<键>` 锚点行（整行仅键）；紧随 `值：` 行取规范化值；`详解：` 行取件内亲算格指针；
            答案块哈希＝值＋"\\n"＋详解行。
  另锚点安全＋多选门（每课时正文 ≤4）。未冻片（批C/D/E/命制8 席）不在本门射程：
  S2 前总闸全量一次跑齐（canonical键名总表 §四.3）；片冻后不可变，文件漂移＝须重冻该片。
  批A 五片（课时01~05）自 2026-09-13T22:30:00+0800 冻结起入本门射程（S1 批A 轮增注）。
跑法：python 对号门.py             # 全部已冻片（报告态恒 exit 0）
      python 对号门.py --strict   # 验收态（任一断言不等 exit 1）
      python 对号门.py --片 课时06 [--strict]
"""
import hashlib
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
TMUB = HERE
MANI = os.path.join(HERE, 'manifest')

# 片名 → 题面库文件名标题段（canonical 键序见 canonical键名总表.md）
TITLES = {
    '课时01':  '坐标法',
    '课时02':  '倾斜角与斜率',
    '课时03':  '方向向量与法向量',
    '课时04':  '点斜式与斜截式',
    '课时05':  '两点式与一般式',
    '课时06':  '两条直线的位置关系',
    '课时06B': '2.2.4点到直线距离',
    '课时07':  '圆的方程',
    '课时08':  '直线与圆的位置关系',
    '课时09':  '圆与圆的位置关系',
}


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_text(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


def parse_questions(path):
    """题面侧 → [(键, 槽型, 题面全文)]，保持文件序。"""
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
    """答案侧 → [(键, 值, 详解指针)]，保持文件序。"""
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


def check_slice(name, strict=False):
    title = TITLES.get(name, '')
    qp = os.path.join(TMUB, '%s%s.md' % (name, ('-' + title) if title else ''))
    ap = os.path.join(TMUB, '%s%s-答案侧.md' % (name, ('-' + title) if title else ''))
    mp = os.path.join(MANI, '%s.manifest.json' % name)
    bad = []
    if not (os.path.exists(qp) and os.path.exists(ap) and os.path.exists(mp)):
        print('【%s】缺件：题面/答案/manifest 任一缺失 ✗' % name)
        if strict:
            sys.exit(1)
        return False
    mani = json.load(open(mp, encoding='utf-8'))
    qs = parse_questions(qp)
    ans = parse_answers(ap)
    qkeys = [k for k, _, _ in qs]
    akeys = [k for k, _, _ in ans]
    mkeys = mani['键序']
    if qkeys != akeys:
        bad.append('题面侧↔答案侧键序不等：缺%s 多%s' % (sorted(set(qkeys) - set(akeys))[:8],
                                                  sorted(set(akeys) - set(qkeys))[:8]))
    if qkeys != mkeys:
        bad.append('题面侧↔manifest 键序不等：缺%s 多%s' % (sorted(set(qkeys) - set(mkeys))[:8],
                                                    sorted(set(mkeys) - set(qkeys))[:8]))
    daov = dict((k, (v, d)) for k, v, d in ans)
    for k, _, qtext in qs:
        h = mani['逐键哈希'].get(k)
        if not h:
            bad.append('manifest 缺键哈希：%s' % k)
            continue
        v, d = daov.get(k, ('', ''))
        if not v:
            bad.append('答案侧空值：%s' % k)
        if not d:
            bad.append('答案侧缺详解锚点：%s' % k)
        if sha_text(qtext) != h['题面']:
            bad.append('题面哈希漂移：%s' % k)
        if sha_text(v + '\n' + d) != h['答案']:
            bad.append('答案块哈希漂移：%s' % k)
    for tag, path in (('题面侧', qp), ('答案侧', ap)):
        if sha_bytes(open(path, 'rb').read()) != mani[tag + 'sha256']:
            bad.append('%s 文件漂移（片冻后被动过→须重冻该片）' % tag)
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
    return ok


def main():
    args = sys.argv[1:]
    strict = '--strict' in args
    if '--片' in args:
        names = [args[args.index('--片') + 1]]
    else:
        names = sorted(f[:-len('.manifest.json')] for f in os.listdir(MANI) if f.endswith('.manifest.json'))
    if not names:
        print('骨架态：manifest 目录空（冻manifest.py 跑后复跑本门）')
        return
    results = [check_slice(n, strict) for n in names]
    allok = all(results)
    total = sum(json.load(open(os.path.join(MANI, '%s.manifest.json' % n), encoding='utf-8'))['期望值']['键数']
                for n in names)
    print('合计：%d 片｜%d 键｜全集断言：%s（%s）'
          % (len(names), total, '相等零缺漏 ✓' if allok else '不等 ✗', 'strict' if strict else '报告态'))
    if strict and not allok:
        sys.exit(1)


if __name__ == '__main__':
    main()
