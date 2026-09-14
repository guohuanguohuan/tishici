# -*- coding: utf-8 -*-
r"""值差诊断.py — 逐键比对 main.tex \ansitem 值 vs 答案侧「值：」行（过程件，只读）。"""
import io
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = r'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/衔接节'
SIDE = r'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/衔接节-答案侧.md'


def braces(s, i):
    d, j = 0, i
    while j < len(s):
        if s[j] == '\\' and j + 1 < len(s):
            j += 2
            continue
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[i + 1:j], j
        j += 1
    raise ValueError('unbalanced')


src = io.open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
side = {}
for m in re.finditer(r'^%[ \t]*ans:(\S+)\s*\n值：(.*)$', io.open(SIDE, encoding='utf-8').read(), re.M):
    side[m.group(1)] = m.group(2).rstrip()

tex_vals, cur, order = {}, None, []
for ln in src.split('\n'):
    ls = ln.strip()
    if ls.startswith('%'):
        continue
    mb = re.match(r'\\begin\{ansblock\}\[([^\]]+)\]', ls)
    if mb:
        cur = mb.group(1)
        order.append(cur)
        continue
    ma = re.search(r'\\ansitem\{(\d+)\}\{', ls)
    if ma and cur:
        tex_vals[cur], _ = braces(ls, ma.end() - 1)

keys = json.load(io.open(os.path.join(r'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest',
                                      '衔接节.manifest.json'), encoding='utf-8'))['键序']
nd = 0
for k in keys:
    tv, sv = tex_vals.get(k), side.get(k)
    if tv == sv:
        continue
    nd += 1
    stripped = re.sub(r'\\allowbreak', '', tv or '')
    print('DIFF', k)
    print('  tex:', repr(tv))
    print('  侧 :', repr(sv))
    print('  剔allowbreak后等值:', stripped == sv)
print('差异键数 =', nd, '/', len(keys))
