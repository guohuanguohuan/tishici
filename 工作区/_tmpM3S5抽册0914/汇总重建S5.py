# -*- coding: utf-8 -*-
"""汇总重建S5.py — 拓展册影子件重跑＋补扫＋旧制台账折形比对＋重建逐件汇总.json"""
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, CJ, T, pieces_of, run_tool, load_readings, source_leakscan, fold

SHADOW = os.path.join(HERE, '影子件')


def shadow_rerun():
    """拓展册两件：影子件（去旧制台账）→ 工具重跑 → 补扫。"""
    out_all = {}
    for pian, pdir in pieces_of('拓展册'):
        sd = os.path.join(SHADOW, '拓展册-' + pian)
        os.makedirs(sd, exist_ok=True)
        for f in ('main.tex', 'qp-m3.sty', 'main-true.pdf', 'main-true.log'):
            shutil.copyfile(os.path.join(pdir, f), os.path.join(sd, f))
        out = os.path.join(HERE, '拓展册-' + pian)
        for stale in ('_stdout红.txt',):
            p = os.path.join(out, stale)
            os.path.exists(p) and os.remove(p)
        r = run_tool(sd, out)
        print('影子重跑 拓展册-%s rc=%d %.1fs' % (pian, r['rc'], r['秒']))
        reds, nr = ([], 0)
        if os.path.exists(os.path.join(out, 'ansbook-true.pdf')):
            reds, nr = source_leakscan(pdir, out)   # 补扫针源＝真源件（非影子）
        print('  补扫：针 %d 红 %d' % (nr, len(reds)))
        out_all[pian] = {'run': r, '补扫红针': len(reds), '补扫针数': nr,
                         '目录': out}
    return out_all


def ledger_compat(pian, pdir, blocks):
    """拓展册旧制台账（key/值 渲染形）折形比对（补充腿，非工具硬门）。"""
    p = os.path.join(pdir, '值台账-%s.json' % pian)
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding='utf-8'))
    led = {it.get('key'): (it.get('值') or '') for it in d.get('items', [])}
    same, drift = 0, []

    def plain(val):
        v = (val or '').replace('$', '').replace('\\iff', '\u27fa') \
                       .replace('\\leqslant', '\u2a7d').replace('\\geqslant', '\u2a7e') \
                       .replace('_', '').replace('^', '')
        return fold(v)
    for b in blocks:
        lv = led.get(b['key'])
        if lv is None:
            drift.append((b['key'], '台账缺键'))
        elif plain(b['val']) == fold(lv):
            same += 1
        else:
            drift.append((b['key'], '折形漂移'))
    return {'台账键数': len(led), '折形全等': same, '漂移': drift[:6],
            '漂移数': len(drift)}


def rebuild():
    rows = []
    for jianxing in ('导学件', '练习件', '拓展册'):
        for pian, pdir in pieces_of(jianxing):
            out = os.path.join(HERE, '%s-%s' % (jianxing, pian))
            redtxt = os.path.join(out, '_stdout红.txt')
            rd = load_readings(out)
            row = {'件型': jianxing, '片': pian, '目录': out.replace('\\', '/'),
                   '源md5': (rd or {}).get('源件md5'),
                   'sty_md5': (rd or {}).get('sty_md5'),
                   '键数': (rd or {}).get('键数'),
                   'canonical来源': (rd or {}).get('canonical来源'),
                   '红': (rd or {}).get('红'), '页数': (rd or {}).get('页数'),
                   '台账': (rd or {}).get('台账'),
                   'rc红': os.path.exists(redtxt),
                   'stdout尾段': None}
            if row['rc红']:
                row['stdout尾段'] = open(redtxt, encoding='utf-8',
                                         errors='replace').read().strip().splitlines()[-6:]
            if jianxing == '拓展册':
                bs = os.path.join(out, '泄漏补扫.json')
                if os.path.exists(bs):
                    b = json.load(open(bs, encoding='utf-8'))
                    row['补扫红针'] = b['红针数']
                    row['补扫针数'] = b['针数']
                row['台账折形比对'] = ledger_compat(pian, pdir, T.parse_piece(pdir)['blocks'])
            rows.append(row)
    json.dump(rows, open(os.path.join(HERE, '逐件汇总.json'), 'w',
                         encoding='utf-8'), ensure_ascii=False, indent=1)
    nrc = sum(1 for r in rows if r['rc红'])
    ngate = sum(1 for r in rows if r['红'])
    print('汇总重建：44 件｜rc红 %d｜门红 %d' % (nrc, ngate))
    for r in rows:
        if r['rc红'] or r['红']:
            print(' 红→', r['件型'], r['片'], '键', r['键数'],
                  'rc红' if r['rc红'] else '', (r['红'] or [])[:3])


if __name__ == '__main__':
    shadow_rerun()
    rebuild()
