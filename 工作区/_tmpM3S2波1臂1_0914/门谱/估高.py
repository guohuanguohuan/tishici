# -*- coding: utf-8 -*-
r"""估高.py — 片件括线判模静态估高（wlen/23 栏宽口径，母版同式）。用法: python 估高.py <片目录>"""
import io
import math
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = sys.argv[1]


def braces(s, i):
    assert s[i] == '{'
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


src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
cur = None
tv, nv = {}, {}
for ln in src.split('\n'):
    ls = ln.strip()
    if ls.startswith('%'):
        continue
    mb = re.match(r'\\begin\{ansblock\}\[([^\]]+)\]', ls)
    if mb:
        cur = mb.group(1)
        continue
    ma = re.search(r'\\ansitem\{(\d+)\}\{', ls)
    if ma and cur and cur not in tv:
        body, _ = braces(ls, ma.end() - 1)
        tv[cur] = (ma.group(1), body)
    mn = re.search(r'\\ansnote\{详解\}\{', ls)
    if mn and cur and cur not in nv:
        body, _ = braces(ls, mn.end() - 1)
        nv[cur] = body

rows = []
for k in tv:
    est = math.ceil(wlen(tv[k][1] + (nv.get(k) or '')) / 23)
    rows.append((est, k, tv[k][0]))
for est, k, n in sorted(rows, reverse=True):
    print(f'{est:3d}  号{n:>2}  {k}')
