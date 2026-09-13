# -*- coding: utf-8 -*-
r"""_p2_screen.py — P2 第10章 轮1 双通道近重复筛查（机械初筛，非判定；口径承 P1 _p1_screen.py）

段：A 池59内部｜B 落选11×池59｜C 落选11内部｜D 微专题真题119×讲练70｜E 微专题全块141内部｜F 微专题真题119×落选11并入B/D逻辑
阈值：ratio≥0.55（全文norm／中文cjk取大）或 conf≥0.95 出命中；另列 0.40~0.55 召回带供人工补判。
"""
import os, json
from difflib import SequenceMatcher

WS = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(WS, '_p2池.json'), encoding='utf-8'))
POOL = D['pool59']
SRC = {q['no']: q for q in D['src70']}
LOST = D['lost']
BACK = [SRC[n] for n in LOST]
WZT = json.load(open(os.path.join(WS, '_p2微专题.json'), encoding='utf-8'))
WZT_TI = [b for b in WZT if b['is_ti']]


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


def score(a, b):
    return (max(ratio(a['norm'], b['norm']), ratio(a['cjk'], b['cjk'])),
            max(conf(a['norm'], b['norm']), conf(a['cjk'], b['cjk'])))


def screen(listA, listB, same_set, lo=0.55):
    pairs = []
    n = len(listA)
    for i in range(n):
        rng = range(i + 1, len(listB)) if same_set else range(len(listB))
        for j in rng:
            a, b = listA[i], listB[j]
            r, c = score(a, b)
            if r >= lo or c >= 0.95:
                pairs.append((r, c, a, b))
    pairs.sort(key=lambda x: (-x[0], -x[1]))
    return pairs


def recall(listA, listB, same_set):
    """0.40≤判<0.55 召回带（含高包含度低ratio），供人工补判。"""
    out = []
    n = len(listA)
    for i in range(n):
        rng = range(i + 1, len(listB)) if same_set else range(len(listB))
        for j in rng:
            a, b = listA[i], listB[j]
            r, c = score(a, b)
            if 0.40 <= r < 0.55 or (0.80 <= c < 0.95 and r >= 0.30):
                out.append((r, c, a, b))
    out.sort(key=lambda x: (-x[0], -x[1]))
    return out


def write_hits(f, title, ps, recall_ps=()):
    f.write('## %s：命中 %d 对（≥0.55/conf0.95）＋召回带 %d 对\n\n' % (title, len(ps), len(recall_ps)))
    f.write('| # | 判 | conf | X | ↔ | Y | X首句 | Y首句 |\n|---|---|---|---|---|---|---|---|\n')
    for k, (r, c, a, b) in enumerate(ps, 1):
        f.write('| %d | %.2f | %.2f | %s | ↔ | %s | %s | %s |\n' % (
            k, r, c, a['id'], b['id'], a['head'][:26], b['head'][:26]))
    if recall_ps:
        f.write('\n召回带（0.40≤判<0.55 或 conf0.80~0.95，人工补判队列）：\n\n')
        f.write('| # | 判 | conf | X | ↔ | Y | X首句 | Y首句 |\n|---|---|---|---|---|---|---|---|\n')
        for k, (r, c, a, b) in enumerate(recall_ps, 1):
            f.write('| %d | %.2f | %.2f | %s | ↔ | %s | %s | %s |\n' % (
                k, r, c, a['id'], b['id'], a['head'][:26], b['head'][:26]))
    f.write('\n')


def main():
    secs = [
        ('A 池59内部', screen(POOL, POOL, True), recall(POOL, POOL, True)),
        ('B 落选11×池59', screen(BACK, POOL, False), recall(BACK, POOL, False)),
        ('C 落选11内部', screen(BACK, BACK, True), recall(BACK, BACK, True)),
        ('D 微专题真题119×讲练70', screen(WZT_TI, POOL + BACK, False), recall(WZT_TI, POOL + BACK, False)),
        ('E 微专题全块141内部', screen(WZT, WZT, True), recall(WZT, WZT, True)),
    ]
    with open(os.path.join(WS, '_p2候选.md'), 'w', encoding='utf-8') as f:
        f.write('# P2 第10章 轮1 近重复候选（机械初筛，未判定）\n\n')
        f.write('> 阈值：双通道 ratio≥0.55（全文norm／中文cjk取大）或包含度 conf≥0.95；'
                '召回带＝0.40≤判<0.55 或 conf0.80~0.95。判定以人工读双方题面为准（公共规则§5）。\n\n')
        for title, ps, rp in secs:
            write_hits(f, title, ps, rp)
    with open(os.path.join(WS, '_p2配对.md'), 'w', encoding='utf-8') as f:
        f.write('# P2 轮1 命中对·双方题面全文对照（供逐对人工判定）\n')
        idx = 0
        for title, ps, rp in secs:
            f.write('\n\n# ===== %s =====\n' % title)
            for r, c, a, b in list(ps) + list(rp):
                idx += 1
                f.write('\n## 对%d｜%.2f/conf%.2f｜%s ↔ %s\n\n**%s**：%s\n\n**%s**：%s\n' % (
                    idx, r, c, a['id'], b['id'], a['id'], a['stem'], b['id'], b['stem']))
    print('候选对：%s' % '；'.join('%s 命中%d+召回%d' % (t.split()[0], len(p), len(rp))
                                  for (t, p, rp) in secs))


if __name__ == '__main__':
    main()
