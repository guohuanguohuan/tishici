# -*- coding: utf-8 -*-
"""估高试算.py — 波1臂3 片件括线判模底稿计算（wlen 口径同母版门谱）。
只读 main.tex，落盘 值台账底稿.json（本过程件目录）。
"""
import io, json, math, os, re, sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = sys.argv[1]
OUT = sys.argv[2]
COLW = 23  # 栏宽字口径


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


src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
tex_vals, note_vals, ruled_set, order = {}, {}, set(), []
lines = src.split('\n')
pending_gray = False
cur = None
for ln in lines:
    ls = ln.strip()
    if ls.startswith('%'):
        continue
    if '{\\ansblockgrayfalse' in ls.replace(' ', ''):
        pending_gray = True
        continue
    mb = re.match(r'\\begin\{ansblock\}\[([^\]]+)\]', ls)
    if mb:
        cur = mb.group(1)
        order.append(cur)
        if pending_gray:
            ruled_set.add(cur)
        pending_gray = False
        continue
    if pending_gray and ls == '':
        continue
    if not pending_gray and ls.startswith('{') is False:
        pending_gray = False
    ma = re.search(r'\\ansitem\{(\d+)\}\{', ls)
    if ma and cur:
        body, _ = braces(ls, ma.end() - 1)
        tex_vals[cur] = body
    mn = re.search(r'\\ansnote\{详解\}\{', ls)
    if mn and cur:
        body, _ = braces(ls, mn.end() - 1)
        note_vals[cur] = body

items = []
for k in order:
    est = math.ceil(wlen((tex_vals.get(k) or '') + (note_vals.get(k) or '')) / COLW) \
        if (tex_vals.get(k) or note_vals.get(k)) else 0
    items.append({'键': k, '印面号': order.index(k) + 1, '值tex': tex_vals.get(k),
                  '估高行数': est, '判模': '括线' if k in ruled_set else '灰底'})

rank = sorted(items, key=lambda x: -x['估高行数'])
print('装配序键数:', len(order), ' 括线键:', sorted(ruled_set))
print('估高排名:')
for it in rank:
    print(f"  {it['估高行数']:>3}  {it['键']}  判模={it['判模']}")
json.dump({'keys': order, 'items': items}, open(OUT, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('底稿 →', OUT)
