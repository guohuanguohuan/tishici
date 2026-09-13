# -*- coding: utf-8 -*-
"""课时02 各 ansblock 估高扫描（承重墙 est>8 → 须括线）。只读。"""
import io
import math
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时02-倾斜角与斜率/main.tex'


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


src = open(SRC, encoding='utf-8').read()
vals, notes, ruled, order = {}, {}, set(), []
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
    if pending and ls == '':
        continue
    if not pending and ls.startswith('{') is False:
        pending = False
    ma = re.search(r'\\ansitem\{(\d+)\}\{', ls)
    if ma and cur:
        body, _ = braces(ls, ma.end() - 1)
        vals[cur] = body
    mn = re.search(r'\\ansnote\{详解\}\{', ls)
    if mn and cur:
        body, _ = braces(ls, mn.end() - 1)
        notes[cur] = body

items = []
for k in order:
    est = math.ceil(wlen((vals.get(k) or '') + (notes.get(k) or '')) / 23)
    items.append((k, est, '括线' if k in ruled else '灰底'))
for k, est, m in sorted(items, key=lambda x: -x[1]):
    print(f'{est:>3}  {m}  {k}')
over = [k for k, e, m in items if e > 8 and m == '灰底']
print('超阈未转括线：', over if over else '无')
print('块数', len(items), '括线', len(ruled))
