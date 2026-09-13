# -*- coding: utf-8 -*-
"""预检估高 — 补位臂2(glm) 06 片：与门-值快照键型判模.py 同判据的括线预判（只读 main.tex，零写入）。"""
import io, math, re, sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BS = chr(92)
PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时06-两条直线的位置关系'
src = open(PIECE + '/main.tex', encoding='utf-8').read()

def braces(s, i):
    assert s[i] == '{', '位置非花括号'
    d, j = 0, i
    while j < len(s):
        if s[j] == BS and j + 1 < len(s):
            j += 2; continue
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[i+1:j], j
        j += 1
    raise ValueError('花括号不配平')

vals, notes, order, ruled = {}, {}, [], set()
pending = False
cur = None
for ln in src.split(chr(10)):
    ls = ln.strip()
    if ls.startswith('%'):
        continue
    if '{' + BS + 'ansblockgrayfalse' in ls.replace(' ', ''):
        pending = True
        continue
    mb = re.match(re.escape(BS + 'begin{ansblock}') + r'\[([^\]]+)\]', ls)
    if mb:
        cur = mb.group(1)
        order.append(cur)
        if pending:
            ruled.add(cur)
        pending = False
        continue
    ma = re.search(re.escape(BS + 'ansitem') + r'{(\d+)}{', ls)
    if ma and cur:
        body, _ = braces(ls, ma.end() - 1)
        vals[cur] = body
    mn = re.search(re.escape(BS + 'ansnote{详解}{'), ls)
    if mn and cur:
        body, _ = braces(ls, mn.end() - 1)
        notes[cur] = body

def wlen(s):
    s = re.sub(BS[0] + r'' + BS + r'[a-zA-Z]+', '', s)
    return sum(0.5 if ord(c) < 128 else 1.0 for c in s)

THRESH = 8
need = []
for idx, k in enumerate(order, 1):
    est = math.ceil(wlen((vals.get(k) or '') + (notes.get(k) or '')) / 23) if (vals.get(k) or notes.get(k)) else 0
    tag = k.rsplit('-', 1)[-1]
    mark = '←需括线' if est > THRESH else ''
    ruledmark = '已括线' if k in ruled else '灰底'
    print(f'{idx:>2} {tag:<4} est={est:>3} {ruledmark} {mark}')
    if est > THRESH:
        need.append(k)
print('需括线键：', sorted(x.rsplit('-', 1)[-1] for x in need))
print('已括线键：', sorted(x.rsplit('-', 1)[-1] for x in ruled))
