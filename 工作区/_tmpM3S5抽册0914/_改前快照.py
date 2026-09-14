# -*- coding: utf-8 -*-
"""改前快照：42 件既有 抽册读数.json 的 册值快照＋门红 留照（钉值恒 0 漂比对基线）。只读。"""
import glob
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
snap = {}
for p in sorted(glob.glob(os.path.join(HERE, '*', '抽册读数.json'))):
    tag = os.path.basename(os.path.dirname(p))
    d = json.load(open(p, encoding='utf-8'))
    vals = d.get('册值快照') or {}
    blob = json.dumps(vals, ensure_ascii=False, sort_keys=True)
    snap[tag] = {'键数': d.get('键数'), '快照sha256': hashlib.sha256(blob.encode('utf-8')).hexdigest(),
                 '红': d.get('红'), '门读数行数': len(d.get('门读数') or [])}
out = os.path.join(HERE, '改前快照-册值.json')
json.dump(snap, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print('快照件数', len(snap), '→', out)
for k, v in snap.items():
    print(' ', k, v['键数'], v['快照sha256'][:12], '红', len(v['红'] or []))
