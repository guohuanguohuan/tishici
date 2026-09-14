# -*- coding: utf-8 -*-
"""_诊断S5.py — 三族红病灶定位（tex/log 层，零编译）。"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, T, pieces_of

out = {'印面号漂移': [], '印面缺印': {}, 'Underfull': {}}

# 1) 课时02 印面号漂移键（台账 vs 件内）
for jianxing in ('导学件', '练习件'):
    for pian, pdir in pieces_of(jianxing):
        rd = load_rd = None
        rp = os.path.join(HERE, '%s-%s' % (jianxing, pian), '抽册读数.json')
        if not os.path.exists(rp):
            continue
        rd = json.load(open(rp, encoding='utf-8'))
        reds = rd.get('红') or []
        if not any('印面号≡值台账' in r for r in reds):
            continue
        led_vals, led_nums, lp = T.load_ledger(pdir)
        piece = T.parse_piece(pdir)
        drift = [(b['key'], b['num'], led_nums.get(b['key']))
                 for b in piece['blocks'] if led_nums.get(b['key']) != b['num']]
        out['印面号漂移'].append({'件': '%s-%s' % (jianxing, pian),
                                 '漂移': drift[:8], '漂移数': len(drift)})

# 2) 逐键值印面缺印键（PDF 门红件）：册值 vs PDF 折形
for d in sorted(glob.glob(os.path.join(HERE, '*-课时*')) +
                glob.glob(os.path.join(HERE, '*-衔接节'))):
    rp = os.path.join(d, '抽册读数.json')
    if not os.path.exists(rp):
        continue
    rd = json.load(open(rp, encoding='utf-8'))
    if not any('逐键值印面' in r for r in (rd.get('红') or [])):
        continue
    import fitz
    import unicodedata
    fold = lambda s: unicodedata.normalize('NFKC', T.norm_ws(s or '')).replace('\u2212', '-')
    def needle(val):
        v = (val or '').replace('$', '').replace('\\iff', '\u27fa') \
                       .replace('\\leqslant', '\u2a7d').replace('\\geqslant', '\u2a7e') \
                       .replace('_', '').replace('^', '')
        return fold(v)
    miss = []
    for k, v in (rd.get('册值快照') or {}).items():
        hit = False
        for tag in ('true', 'false'):
            p = os.path.join(d, 'ansbook-%s.pdf' % tag)
            if not os.path.exists(p):
                continue
            doc = fitz.open(p)
            t = fold('\n'.join(pg.get_text() for pg in doc))
            doc.close()
            if needle(v) in t:
                hit = True
        if not hit:
            miss.append((k, (v or '')[:60]))
    if miss:
        out['印面缺印'][os.path.basename(d)] = miss[:6]

# 3) Underfull 行摘录（册 log）
for d in sorted(glob.glob(os.path.join(HERE, '*-课时*')) +
                glob.glob(os.path.join(HERE, '*-衔接节'))):
    log = os.path.join(d, 'ansbook-true.log')
    if not os.path.exists(log):
        continue
    txt = open(log, encoding='utf-8', errors='replace').read()
    ms = re.findall(r'Underfull[^\n]*\n(?:[^\n]*\n){0,3}', txt)
    if ms:
        out['Underfull'][os.path.basename(d)] = [m.strip().replace('\n', ' ⏎ ')[:220]
                                                 for m in ms[:2]]

json.dump(out, open(os.path.join(HERE, '诊断读数.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('印面号漂移件:', [(x['件'], x['漂移数']) for x in out['印面号漂移']])
print('印面缺印件数:', len(out['印面缺印']))
for k, v in out['印面缺印'].items():
    print('  ', k, v[:2])
print('Underfull 件数:', len(out['Underfull']))
for k, v in list(out['Underfull'].items())[:3]:
    print('  ', k, v[0][:150])
