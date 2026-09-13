# -*- coding: utf-8 -*-
"""est-估高.py — 片件 ansblock 逐键估高速查（括线判模预读数；正式读数以门-值快照键型判模.py 为准）。
用法: python est-估高.py <片main.tex路径>
"""
import io
import math
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = sys.argv[1]


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
    raise ValueError


src = open(path, encoding='utf-8').read()
tex_vals, note_vals, ruled, cur, pend = {}, {}, set(), None, False
for ln in src.split('\n'):
    ls = ln.strip()
    if ls.startswith('%'):
        continue
    if '{\\ansblockgrayfalse' in ls.replace(' ', ''):
        pend = True
        continue
    mb = re.match(r'\\begin\{ansblock\}\[([^\]]+)\]', ls)
    if mb:
        cur = mb.group(1)
        if pend:
            ruled.add(cur)
        pend = False
        continue
    ma = re.search(r'\\ansitem\{(\d+)\}\{', ls)
    if ma and cur:
        tex_vals[cur], _ = braces(ls, ma.end() - 1)
    mn = re.search(r'\\ansnote\{详解\}\{', ls)
    if mn and cur:
        note_vals[cur], _ = braces(ls, mn.end() - 1)


def wlen(s):
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    return sum(0.5 if ord(c) < 128 else 1.0 for c in s)


rank = []
for k, tv in tex_vals.items():
    est = math.ceil(wlen(tv + note_vals.get(k, '')) / 23)
    rank.append((est, k, '括线' if k in ruled else '灰底'))
rank.sort(reverse=True)
for est, k, m in rank:
    print(f'{est:>3} {m} {k}')
print('块数:', len(tex_vals))
print('est>8集:', sorted(k for e, k, m in rank if e > 8))
