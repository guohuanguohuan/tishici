# -*- coding: utf-8 -*-
r"""估高探针.py — 片面 ansblock 逐键估高（wlen/23 栏宽口径）＋括线现状（只读）。
用法: python 估高探针.py <片目录>
"""
import io
import json
import math
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = sys.argv[1]


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
    raise ValueError('花括号不配平')


def wlen(s):
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    return sum(0.5 if ord(c) < 128 else 1.0 for c in s)


src = io.open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
tex_vals, note_vals, ruled, order = {}, {}, set(), []
pending = False
cur = None
for ln in src.split('\n'):
    ls = ln.strip()
    if ls.startswith('%'):
        continue
    if '{\\ansblockgrayfalse' in ls.replace(' ', ''):
        pending = True
        continue
    mb = re.match(r'\\begin\{ansblock\}\[([^\]]+)\]', ls)
    if mb:
        cur = mb.group(1)
        order.append(cur)
        if pending:
            ruled.add(cur)
        pending = False
        continue
    ma = re.search(r'\\ansitem\{(\d+)\}\{', ls)
    if ma and cur:
        tex_vals[cur], _ = braces(ls, ma.end() - 1)
    mn = re.search(r'\\ansnote\{详解\}\{', ls)
    if mn and cur:
        note_vals[cur], _ = braces(ls, mn.end() - 1)

rows = []
for k in order:
    est = math.ceil(wlen((tex_vals.get(k) or '') + (note_vals.get(k) or '')) / 23)
    rows.append((est, k, k in ruled))
rows.sort(reverse=True)
print('括线现状：%d 块' % len(ruled))
for est, k, r in rows:
    print(f'  {est:>3}行 {"括线" if r else "灰底"} {k}')
print('>8行键：', [k for e, k, r in rows if e > 8])
