# -*- coding: utf-8 -*-
r"""_p1_screen.py — P1 轮1 双通道近重复筛查（机械初筛，非判定；口径仿 M2 _tmp查重.py）

通道：①全文骨架 norm ratio≥0.55 ②纯中文骨架 cjk ratio≥0.55 ③包含度 conf（短侧被公共子块覆盖率）≥0.95。
三段：A＝池41内部；B＝回捞25×池41；C＝回捞25内部。
命中对全文题面对照落 _p1配对.md，供逐对人工判定（判重不唯分数）。
"""
import os, json
from difflib import SequenceMatcher

WS = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(WS, '_p1池.json'), encoding='utf-8'))
POOL = D['pool41']
SRC = {q['no']: q for q in D['src66']}
LOST = [1, 4, 5, 6, 7, 8, 13, 15, 21, 28, 31, 33, 38, 40, 41, 42, 45, 52, 55, 58, 59, 61, 63, 65, 66]
BACK = [SRC[n] for n in LOST]


def ratio(a, b):
    if not a or not b:
        return 0.0
    if len(a) > len(b) * 2 or len(b) > len(a) * 2:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def conf(a, b):
    if not a or not b:
        return 0.0
    sm = SequenceMatcher(None, a, b)
    m = sum(bl.size for bl in sm.get_matching_blocks())
    return m / min(len(a), len(b))


def screen(listA, listB, same_set):
    pairs = []
    n = len(listA)
    for i in range(n):
        rng = range(i + 1, len(listB)) if same_set else range(len(listB))
        for j in rng:
            a, b = listA[i], listB[j]
            r = max(ratio(a['norm'], b['norm']), ratio(a['cjk'], b['cjk']))
            c = max(conf(a['norm'], b['norm']), conf(a['cjk'], b['cjk']))
            if r >= 0.55 or c >= 0.95:
                pairs.append((r, c, a, b))
    pairs.sort(key=lambda x: (-x[0], -x[1]))
    return pairs


def main():
    secs = [('A 池41内部', screen(POOL, POOL, True)),
            ('B 回捞25×池41', screen(BACK, POOL, False)),
            ('C 回捞25内部', screen(BACK, BACK, True))]
    with open(os.path.join(WS, '_p1候选.md'), 'w', encoding='utf-8') as f:
        f.write('# P1 轮1 近重复候选（机械初筛，未判定）\n\n')
        f.write('> 阈值：双通道 ratio≥0.55（全文norm／中文cjk取大）或包含度 conf≥0.95。')
        f.write('命中对题面全文见 _p1配对.md；判定以人工为准（公共规则§5）。\n\n')
        for title, ps in secs:
            f.write('## %s：命中 %d 对\n\n' % (title, len(ps)))
            f.write('| # | 判 | conf | X | X知识点 | ↔ | Y | Y知识点 | X首句 | Y首句 |\n|---|---|---|---|---|---|---|---|---|---|\n')
            for k, (r, c, a, b) in enumerate(ps, 1):
                f.write('| %d | %.2f | %.2f | %s | %s | ↔ | %s | %s | %s | %s |\n' % (
                    k, r, c, a['id'], a['kp'][:20].replace('|', '／'), b['id'],
                    b['kp'][:20].replace('|', '／'), a['head'][:28], b['head'][:28]))
            f.write('\n')
    with open(os.path.join(WS, '_p1配对.md'), 'w', encoding='utf-8') as f:
        f.write('# P1 轮1 命中对·双方题面全文对照（供逐对人工判定）\n')
        idx = 0
        for title, ps in secs:
            f.write('\n\n# ===== %s =====\n' % title)
            for r, c, a, b in ps:
                idx += 1
                f.write('\n## 对%d｜%.2f/conf%.2f｜%s ↔ %s\n\n' % (idx, r, c, a['id'], b['id']))
                f.write('**%s**：%s\n\n**%s**：%s\n' % (a['id'], a['stem'], b['id'], b['stem']))
    tot = sum(len(p) for _, p in secs)
    print('候选对合计=%d（A=%d B=%d C=%d）-> _p1候选.md/_p1配对.md' % (
        tot, len(secs[0][1]), len(secs[1][1]), len(secs[2][1])))


if __name__ == '__main__':
    main()
