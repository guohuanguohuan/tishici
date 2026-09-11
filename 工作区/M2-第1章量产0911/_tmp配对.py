# -*- coding: utf-8 -*-
"""_tmp配对.py — 逐题最优候选导出（亲算用）：按相似度降序，打印外源题面 vs 我方题面全文。
用法: python _tmp配对.py <起> <数> > _tmp配对-N.md"""
import json, os, sys, re
from difflib import SequenceMatcher
WS = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(WS, '_tmp查重-池.json'), encoding='utf-8'))
ext, mine = d['ext'], d['old'] + d['slice']


def ratio(a, b):
    if not a or not b or len(a) > len(b) * 2 or len(b) > len(a) * 2:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def clean(s):
    s = re.split(r'【答案】', s)[0]
    s = re.sub(r'【图】', '[图]', s)
    s = re.sub(r'\n+', '\n', s)
    return s.strip()


rows = []
for e in ext:
    scored = []
    for m in mine:
        b = max(ratio(e['norm'], m['norm']), ratio(e['cjk'], m['cjk']))
        if b >= 0.55:
            scored.append((b, m))
    scored.sort(key=lambda x: -x[0])
    rows.append((scored[0][0] if scored else 0.0, e, scored[:3]))
rows.sort(key=lambda x: -x[0])

a, n = int(sys.argv[1]), int(sys.argv[2])
for i, (b, e, top) in enumerate(rows[a - 1:a - 1 + n], start=a):
    print('=== 排名%d｜%s｜判=%.2f｜难度标=%s｜知识点=%s ===' % (i, e['id'], b, e['diff'], e['kp']))
    print('【外源题面】' + clean(e['stem'])[:900])
    for s, m in top:
        print('  --- 我方 %s（%.3f｜知识点=%s｜难度=%s）---' % (m['id'], s, m['kp'][:30], m['diff']))
        print('  ' + clean(m['stem'])[:900].replace('\n', '\n  '))
    print()
