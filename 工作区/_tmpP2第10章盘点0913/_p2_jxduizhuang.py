# -*- coding: utf-8 -*-
"""_p2_jxduizhuang.py — 教材39 × 微专题141 同文/改编机械比对（承 _p2_jiaocai.py 口径）＋ P1成卷零回收终验辅助"""
import os, json, re
from difflib import SequenceMatcher

WS = os.path.dirname(os.path.abspath(__file__))
PUNCT = '，。；：、！？“”‘’\'",.!?—－-…·・_/／|｜*^$@+=~`’'


def canon(t):
    t = re.sub(r'⟦|⟧', '', t)
    t = re.sub(r'_\(([^()]*)\)', r'_\1', t)
    t = re.sub(r'\^\(([^()]*)\)', r'^\1', t)
    t = re.sub(r'\\[A-Za-z]+', '', t)
    t = t.replace('【图】', '').replace('⏎', ' ')
    t = re.sub(r'\d+(?:\.\d+)?%?', '#', t)
    t = re.sub(r'[零一二两三四五六七八九十百千万]+', '#', t)
    t = re.sub(r'\s+', '', t)
    t = ''.join(c for c in t if c not in PUNCT)
    return t.lower()


def cjk_only(t):
    return ''.join(c for c in t if '一' <= c <= '鿿' or c in '#')


def ratio(a, b):
    if not a or not b or len(a) > len(b) * 2 or len(b) > len(a) * 2:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def conf(a, b):
    if not a or not b:
        return 0.0
    sm = SequenceMatcher(None, a, b)
    return sum(bl.size for bl in sm.get_matching_blocks()) / min(len(a), len(b))


def main():
    Q = json.load(open(os.path.join(WS, '_p2教材35.json'), encoding='utf-8'))
    W = json.load(open(os.path.join(WS, '_p2微专题.json'), encoding='utf-8'))
    hits = []
    for jid, stem in Q.items():
        n, c = canon(stem), cjk_only(canon(stem))
        for w in W:
            r = max(ratio(n, w['norm']), ratio(c, w['cjk']))
            cf = max(conf(n, w['norm']), conf(c, w['cjk']))
            if r >= 0.40 or cf >= 0.85:
                hits.append((round(r, 3), round(cf, 2), jid, w['id'], stem[:26], w['stem'][:26]))
    hits.sort(key=lambda x: (-x[0], -x[1]))
    with open(os.path.join(WS, '_p2教材×微专题.md'), 'w', encoding='utf-8') as f:
        f.write('# 教材39 × 微专题141 命中清单（≥0.40 或 conf≥0.85，未判定）\n\n| # | 判 | conf | 教材 | ↔ | 微专题 |\n|---|---|---|---|---|---|\n')
        for k, (r, cf, a, b, s1, s2) in enumerate(hits, 1):
            f.write('| %d | %.2f | %.2f | %s | ↔ | %s |\n' % (k, r, cf, a, b))
        f.write('\n合计：%d 对\n\n## 对·题面摘要\n' % len(hits))
        for r, cf, a, b, s1, s2 in hits:
            f.write('\n- **%.2f/%.2f %s ↔ %s**\n  - 教材：%s…\n  - 微专题：%s…\n' % (r, cf, a, b, s1, s2))
    print('教材39×微专题141：命中=%d（其中≥0.55=%d）' % (len(hits), len([h for h in hits if h[0] >= 0.55])))


if __name__ == '__main__':
    main()
