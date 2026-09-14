# -*- coding: utf-8 -*-
"""_片段在册证明.py — 残缺印键片段级在册核（长针拆片逐查，定性假红）。"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, T, fold
from _强折形复验 import strong_needle
import fitz

res = json.load(open(os.path.join(HERE, '强折形复验.json'), encoding='utf-8'))
out = {}
for name, v in res.items():
    if not v['缺印数']:
        continue
    d = os.path.join(HERE, name)
    rd = json.load(open(os.path.join(d, '抽册读数.json'), encoding='utf-8'))
    hay = {}
    for tag in ('true', 'false'):
        doc = fitz.open(os.path.join(d, 'ansbook-%s.pdf' % tag))
        hay[tag] = fold('\n'.join(pg.get_text() for pg in doc))
        doc.close()
    for k, nv in v['缺印键']:
        # 用原值再强折（json 里只存了截断串）
        full = rd['册值快照'][k]
        n = strong_needle(full)
        frags = [f for f in re.split(r'[;；,，]', n) if len(f) >= 4]
        hits = {f: all(f in hay[t] for t in hay) for f in frags}
        out['%s｜%s' % (name, k)] = {'片段数': len(frags),
                                     '全中片段数': sum(hits.values()),
                                     '缺片': [f for f, h in hits.items() if not h][:4]}
json.dump(out, open(os.path.join(HERE, '片段在册证明.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
for k, v in out.items():
    print(k, '→ 片段', v['片段数'], '中', v['全中片段数'],
          ('缺:' + str(v['缺片'])[:100]) if v['缺片'] else '')
