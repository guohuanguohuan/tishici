# -*- coding: utf-8 -*-
r"""冻manifest.py —— M3 S1 首批片冻结器（工序件，跑于 _tmpM3S1首批0913/）。

口径（军师账审-收口轮0913 §七合成终裁）：
  对每片：解析 题面侧/答案侧 → 键序（canonical 位）＋逐键哈希（题面全文 sha256／答案块 sha256）
  ＋文件级哈希＋源件（定稿）哈希 → 写 `成卷/题面库/manifest/<片>.manifest.json`。
  提取规则（与 对号门.py 一致，改片格式须两件同改）：
    题面侧：`### <键>｜…` 起块；题面全文＝块内除【注】行、空行、`---` 分隔行外全部行（前置提示行属印面，保留）。
    答案侧：`% ans:<键>` 锚点行；紧随 `值：` 行取规范化值；`详解：` 行取件内亲算格指针；答案块哈希＝值＋"\n"＋详解行。
  冻结纪律：片冻后不可变；单点变更→重冻该片→下游回冲。
跑法：python 冻manifest.py [片名 ...]   # 缺省＝SLICES 全表
"""
import hashlib
import io
import json
import os
import re
import sys
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913'))
TMUB = os.path.join(ROOT, '成卷', '题面库')
MANI = os.path.join(TMUB, 'manifest')
DING = os.path.join(ROOT, '定稿')

SLICES = {
    '课时06':  '定稿/批B-课时06-两条直线的位置关系.md',
    '课时06B': '定稿/批B补-课时06B-2.2.4 点到直线距离.md',
    '课时07':  '定稿/批B-课时07-圆的方程（2.3.1加2.3.2合）.md',
    '课时08':  '定稿/批B-课时08-直线与圆的位置关系.md',
    '课时09':  '定稿/批B-课时09-圆与圆的位置关系.md',
}
MULTI_EXP = {'课时06': 2, '课时06B': 1, '课时07': 2, '课时08': 0, '课时09': 4}


def sha(t):
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


def freeze(slice_name, src_rel):
    qp = os.path.join(TMUB, '%s.md' % slice_name)
    ap = os.path.join(TMUB, '%s-答案侧.md' % slice_name)
    sp = os.path.join(DING, os.path.basename(src_rel))
    for p in (qp, ap, sp):
        assert os.path.exists(p), '缺件：%s' % p
    qs, ans = parse_questions(qp), parse_answers(ap)
    qkeys = [k for k, _, _ in qs]
    akeys = [k for k, _, _ in ans]
    assert qkeys == akeys, '%s 键序不等：题面侧%d vs 答案侧%d\n缺%s\n多%s' % (
        slice_name, len(qkeys), len(akes), sorted(set(qkeys) - set(akes))[:6], sorted(set(akes) - set(qkeys))[:6])
    daov = dict((k, (v, d)) for k, v, d in ans)
    per = {}
    for k, _, qtext in qs:
        v, d = daov[k]
        assert v, '%s 空值' % k
        assert d, '%s 缺详解锚点' % k
        per[k] = {'题面': sha(qtext), '答案': sha(v + '\n' + d)}
    multi = [k for k, t, _ in qs if t == '多选']
    exp = {
        '键数': len(qkeys),
        '导学键数': sum(1 for k in qkeys if '-导-' in k),
        '练习键数': sum(1 for k in qkeys if '-练-' in k),
        '多选数': len(multi),
        '多选键': multi,
        '对号门期望': '题面侧键集＝答案侧锚点集＝manifest键清单（%d=%d=%d，序一致零缺漏）；'
                  '多选门≤4（本片%d，%s）；题面全文/答案块哈希逐一相符；片冻后不可变，变更→重冻→下游回冲'
                  % (len(qkeys), len(akes), len(qkeys), len(multi),
                     '触顶合规' if MULTI_EXP[slice_name] == 4 and len(multi) == 4 else '合规'),
    }
    assert exp['导学键数'] == 5 and exp['练习键数'] == 16, '%s 导学/练习键数异常：%d/%d' % (
        slice_name, exp['导学键数'], exp['练习键数'])
    assert exp['多选数'] == MULTI_EXP[slice_name], '%s 多选数 %d ≠ 期望 %d' % (
        slice_name, exp['多选数'], MULTI_EXP[slice_name])
    stamp = datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
    mani = {
        '片': slice_name,
        '章': 'M3选必1第2章',
        '键式': '2章-<册>-课时<NN>-<槽>',
        '冻时戳': stamp,
        '源件': src_rel.replace('定稿/', ''),
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
    print('%s 冻结 ✓｜键%d（导%d＋练%d）｜多选%d｜manifest→%s'
          % (slice_name, exp['键数'], exp['导学键数'], exp['练习键数'], exp['多选数'], os.path.relpath(out, ROOT)))


def main():
    names = sys.argv[1:] or list(SLICES)
    for n in names:
        freeze(n, SLICES[n])


if __name__ == '__main__':
    main()
