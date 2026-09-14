# -*- coding: utf-8 -*-
"""值域宏清单盘点（折形表扩容定表用）。只读。"""
import glob
import io
import json
import re
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
c = Counter()
for p in (glob.glob('拓展册-*/抽册读数.json') + glob.glob('导学件-*/抽册读数.json')
          + glob.glob('练习件-*/抽册读数.json')):
    d = json.load(open(p, encoding='utf-8'))
    for v in (d.get('册值快照') or {}).values():
        c.update(re.findall(r'\\[a-zA-Z]+', v or ''))
for k, n in c.most_common(80):
    print(k, n)
print('----样例值（含宏最多的 3 条）----')
best = []
for p in glob.glob('拓展册-上册/抽册读数.json'):
    d = json.load(open(p, encoding='utf-8'))
    for k, v in d['册值快照'].items():
        best.append((len(re.findall(r'\\[a-zA-Z]+', v or '')), k, (v or '')[:100]))
for n, k, v in sorted(best)[-3:]:
    print(n, k, v)
