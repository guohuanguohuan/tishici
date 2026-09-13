# -*- coding: utf-8 -*-
r"""冻manifest批D.py —— M3 S1 批D 片冻结器（工序件，跑于 _tmpM3S1批D0913/；以 _tmpM3S1首批0913/冻manifest.py 为底改）。

口径（S1 批D 轮·沿军师账审-收口轮0913 §七冻结纪律）：
  对每片：解析 题面侧/答案侧 → 键序（canonical 位）＋逐键哈希（题面全文 sha256／答案块 sha256）
  ＋文件级哈希＋源件（定稿）哈希 → 写 `成卷/题面库/manifest/<片>.manifest.json`。
  提取规则（与 对号门.py 一致，改片格式须两件同改）：
    题面侧：`### <键>｜…` 起块；题面全文＝块内除【注】行、空行、`---` 分隔行外全部行（前置提示行属印面，保留）。
    答案侧：`% ans:<键>` 锚点行；紧随 `值：` 行取规范化值；`详解：` 行取件内亲算格指针；答案块哈希＝值＋"\n"＋详解行。
  批D 特有：导学 0＋练习 16＋拓区（键数按片 50/15/29/21，让位/撤块不占键）；多选门只计正文（拓区多选另记不入 ≤4 门，
  对号门 v3 同口径改）。
  冻结纪律：片冻后不可变；单点变更→重冻该片→下游回冲。
跑法：python 冻manifest批D.py --stamp '2026-09-13T23:12:00+0800' [片名 ...]   # 缺省＝SLICES 全表
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
    '课时14':  ('2.6.2双曲线性质',   '定稿/批D-课时14-2.6.2双曲线性质.md'),
    '课时15':  ('2.7.1抛物线方程',   '定稿/批D-课时15-2.7.1抛物线方程.md'),
    '课时16':  ('2.7.2抛物线性质',   '定稿/批D-课时16-2.7.2抛物线性质.md'),
    '课时17':  ('2.8①压轴综合一',    '定稿/批D-课时17-2.8①压轴综合一.md'),
}
# 拓展键数／正文多选数／拓区多选数（门验三读数；键数＝16＋拓展键数）
TUO_EXP = {'课时14': 50, '课时15': 15, '课时16': 29, '课时17': 21}
ZHENG_MULTI_EXP = {'课时14': 0, '课时15': 0, '课时16': 1, '课时17': 0}
TUO_MULTI_EXP = {'课时14': 1, '课时15': 3, '课时16': 4, '课时17': 0}
REMARKS = {
    '课时14': '拓14-13 让位不设键＋拓14-31 双收4撤不设块（拓键复合：01~12,14~30,32-1/2,33-1~13,34-1~6，合50键）；'
              '值规范化仅14-08、14-10 多行【答案】并一行（仅去换行零增删字）',
    '课时15': '无让位；闸附条件落盘（15行28 组合特批、15-16 行「总高5、拱高3、宽6…0913 勘误」）',
    '课时16': '拓16-18 让位席无键留块（拓键实幅01~30 减18，29键）；16行11 16-01 依据格还原',
    '课时17': '卷④§2.8.12.1-25 让位无块无键，注记随 17-03 块内【注】；拓17-01 选项 A/B/C 图嵌占位照源保留'
              '（瑕疵⑤在案）；17行18/19 改④/收窄',
}
CHOUHE = {
    '课时14': '工作区/_tmpM3前置闸0913/互撞与抽核-批D1415.md（抽验报告-批D1415 6/6、拓14真盲 4/4、内容级14/14、勘误5/5闭合）',
    '课时15': '工作区/_tmpM3前置闸0913/互撞与抽核-批D1415.md（内容级14/14、勘误5/5闭合）',
    '课时16': '工作区/_tmpM3前置闸0913/互撞与抽核-批D1617.md（抽验-批D1617 6/6 错键0、内容级14/14、复算14/14全对）',
    '课时17': '工作区/_tmpM3前置闸0913/互撞与抽核-批D1617.md（内容级14/14、复算14/14全对）',
}
CHOUHE_TAIL = '；闸判§六④：本件即§八案3要求之样本与结果记录，入S1 freeze manifest'


def sha(t):
    if isinstance(t, bytes):
        return hashlib.sha256(t).hexdigest()
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


def freeze(slice_name, spec, stamp=None):
    title, src_rel = spec
    qp = os.path.join(TMUB, '%s-%s.md' % (slice_name, title))
    ap = os.path.join(TMUB, '%s-%s-答案侧.md' % (slice_name, title))
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
    zheng_multi = [k for k, t, _ in qs if t == '多选' and '-拓-' not in k]
    tuo_multi = [k for k, t, _ in qs if t == '多选' and '-拓-' in k]
    n_zhao = sum(1 for k in qkeys if '-导-' in k)
    n_lian = sum(1 for k in qkeys if '-练-' in k)
    n_tuo = sum(1 for k in qkeys if '-拓-' in k)
    exp = {
        '键数': len(qkeys),
        '导学键数': n_zhao,
        '练习键数': n_lian,
        '拓展键数': n_tuo,
        '多选数': len(zheng_multi),
        '多选键': zheng_multi,
        '拓区多选数': len(tuo_multi),
        '拓区多选键': tuo_multi,
        '备注': REMARKS[slice_name],
        '抽核': CHOUHE[slice_name] + CHOUHE_TAIL,
        '对号门期望': '题面侧键集＝答案侧锚点集＝manifest键清单（%d=%d=%d，序一致零缺漏）；'
                  '多选门≤4（只计正文：本片正文%d＋拓区%d，拓区多选不入门，对号门 v3 增注同口径）；'
                  '题面全文/答案块哈希逐一相符；片冻后不可变，变更→重冻→下游回冲'
                  % (len(qkeys), len(akeys), len(qkeys), len(zheng_multi), len(tuo_multi)),
    }
    assert n_zhao == 0 and n_lian == 16 and n_tuo == TUO_EXP[slice_name], (
        '%s 导学/练习/拓键数异常：%d/%d/%d（期望 0/16/%d）'
        % (slice_name, n_zhao, n_lian, n_tuo, TUO_EXP[slice_name]))
    assert exp['键数'] == 16 + TUO_EXP[slice_name], '%s 总键数异常：%d' % (slice_name, exp['键数'])
    assert exp['多选数'] == ZHENG_MULTI_EXP[slice_name], '%s 正文多选数 %d ≠ 期望 %d' % (
        slice_name, exp['多选数'], ZHENG_MULTI_EXP[slice_name])
    assert exp['拓区多选数'] == TUO_MULTI_EXP[slice_name], '%s 拓区多选数 %d ≠ 期望 %d' % (
        slice_name, exp['拓区多选数'], TUO_MULTI_EXP[slice_name])
    stamp = stamp or datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
    mani = {
        '片': slice_name,
        '章': 'M3选必1第2章',
        '批': '批D',
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
    print('%s 冻结 ✓｜键%d（导%d＋练%d＋拓%d）｜正文多选%d｜拓区多选%d｜manifest→%s'
          % (slice_name, exp['键数'], n_zhao, n_lian, n_tuo, exp['多选数'], exp['拓区多选数'],
             os.path.relpath(out, ROOT)))


def main():
    args = sys.argv[1:]
    stamp = None
    if '--stamp' in args:
        i = args.index('--stamp')
        stamp = args[i + 1]
        args = args[:i] + args[i + 2:]
    names = args or list(SLICES)
    for n in names:
        freeze(n, SLICES[n], stamp)


if __name__ == '__main__':
    main()
