# -*- coding: utf-8 -*-
"""折形比对S5.py — 拓展册旧制台账（渲染形值）强折形 containment 重比，就地更新逐件汇总。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, CJ, T, pieces_of
from _强折形复验 import strong_needle


def fold_chk(lv, val):
    a = T.norm_ws(strong_needle(val))
    b = T.norm_ws(lv).replace('\u2212', '-')
    return b in a


out = {}
for pian, pdir in pieces_of('拓展册'):
    d = json.load(open(os.path.join(pdir, '值台账-%s.json' % pian), encoding='utf-8'))
    led = {it.get('key'): (it.get('值') or '') for it in d.get('items', [])}
    from 汇编答案册S5 import parse_raw
    blocks = parse_raw(pdir)
    same, drift = 0, []
    for b in blocks:
        lv = led.get(b['key'])
        if lv is None:
            drift.append((b['key'], '台账缺键'))
        elif fold_chk(lv, b['val']):
            same += 1
        else:
            drift.append((b['key'], 'containment不中'))
    out[pian] = {'台账键数': len(led), 'containment中': same,
                 '残漂移': drift[:6], '漂移数': len(drift)}
    print(pian, '中', same, '/', len(blocks), '残', len(drift), drift[:3])


if __name__ == '__main__':
    rows = json.load(open(os.path.join(HERE, '逐件汇总.json'), encoding='utf-8'))
    for r in rows:
        if r['件型'] == '拓展册':
            r['台账折形比对'] = out.get(r['片'])
    json.dump(rows, open(os.path.join(HERE, '逐件汇总.json'), 'w',
                         encoding='utf-8'), ensure_ascii=False, indent=1)
    print('逐件汇总.json 已就地更新')
