# -*- coding: utf-8 -*-
r"""门-值快照键型判模15.py — M3 S2 波1 臂4·课时15·值快照逐字零漂＋键型两档＋括线判模断言。
适配自臂4 门谱（课时09/14 版）：PIECE/SIDE/MANI/OUT→课时15；NKEY=36（全值型，无过程键）；
NUM＝印面装配序全键映射（探究 1—31＋课堂评价 32—36）；RULED 载 括线键-课时15.json（首轮 [] 跑读数）。
唯一写件＝值台账底稿-课时15.json（本目录）。
"""
import fitz  # pymupdf
import io
import json
import math
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时15-2.7.1抛物线方程'
SIDE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/课时15-2.7.1抛物线方程-答案侧.md'
MANI = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/课时15.manifest.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '值台账底稿-课时15.json')

PROC = set()
RULED = set(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        '括线键-课时15.json'), encoding='utf-8')))
NRULE = len(RULED)
NKEY = 36
NUM = ('2章-练-课时15-01:1,2章-练-课时15-03:2,2章-练-课时15-05:3,2章-练-课时15-14:4,'
       '2章-拓-课时15-15:5,2章-练-课时15-02:6,2章-练-课时15-07:7,2章-拓-课时15-07:8,'
       '2章-拓-课时15-08:9,2章-拓-课时15-10:10,2章-拓-课时15-11:11,2章-练-课时15-08:12,'
       '2章-练-课时15-04:13,2章-练-课时15-09:14,2章-练-课时15-11:15,2章-拓-课时15-12:16,'
       '2章-拓-课时15-13:17,2章-练-课时15-06:18,2章-练-课时15-10:19,2章-练-课时15-12:20,'
       '2章-拓-课时15-14:21,2章-练-课时15-13:22,2章-练-课时15-16:23,2章-拓-课时15-01:24,'
       '2章-拓-课时15-09:25,2章-拓-课时15-03:26,2章-拓-课时15-04:27,2章-拓-课时15-05:28,'
       '2章-拓-课时15-06:29,2章-拓-课时15-02:30,2章-练-课时15-15:31,'
       '2章-导-课时15-G1:32,2章-导-课时15-G2:33,2章-导-课时15-G3:34,'
       '2章-导-课时15-G4:35,2章-导-课时15-G5:36')

reds = []
def check(name, ok, detail=''):
    tag = '绿' if ok else '红'
    print(f'  [{tag}] {name}' + (f'｜{detail}' if detail else ''))
    if not ok:
        reds.append(name)

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

side_raw = open(SIDE, encoding='utf-8').read()
side = {}
for m in re.finditer(r'^%[ \t]*ans:(\S+)\s*\n值：(.*)$', side_raw, re.M):
    side[m.group(1)] = m.group(2).rstrip()

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

def wlen(s):
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    return sum(0.5 if ord(c) < 128 else 1.0 for c in s)

manifest = json.load(open(MANI, encoding='utf-8'))
keyseq = manifest['键序']
num_map = {}
for seg in NUM.split(','):
    k, n = seg.rsplit(':', 1)
    if k.startswith('2章'):
        num_map[k] = int(n)
    else:
        base = '2章-导-课时15-' if k.startswith('G') else '2章-练-课时15-'
        num_map[base + k] = int(n)

print('== ①② 值快照＋键型 ==')
items = []
for k in keyseq:
    tv, sv = tex_vals.get(k), side.get(k)
    kt = '过程' if k in PROC else '值'
    ok = (tv == sv) and tv is not None
    d = '逐字全等' if ok else f'tex={tv!r} 侧={sv!r}'
    check(f'{num_map[k]:>2} {k} [{kt}]', ok, d)
    est = math.ceil(wlen((tv or '') + (note_vals.get(k) or '')) / 23) if (tv or note_vals.get(k)) else 0
    items.append({'键': k, '印面号': num_map[k], '键型': kt, '值tex': tv, '值源': sv,
                  '估高行数': est, '值源字符': len(sv) if sv else 0,
                  '详解字符': len(re.sub(r'\\[a-zA-Z]+', '', note_vals.get(k) or ''))})

print('== ③ 括线判模（静态估高＋PDF 渲染面） ==')
check('tex括线键集≡RULED判定集', ruled_set == RULED, ','.join(sorted(ruled_set)))
check('全片估高>8 键集≡tex括线集（承重墙判据逐键）',
      {it['键'] for it in items if it['估高行数'] > 8} == RULED,
      ' '.join(f"{it['键'].rsplit('-',1)[-1]}:{it['估高行数']}" for it in items if it['估高行数'] > 8))
rank = sorted(items, key=lambda x: -x['估高行数'])
topn = {it['键'] for it in rank[:NRULE]}
check(f'估高 top-{NRULE} ≡ tex括线集', topn == ruled_set,
      'top=' + ','.join(it['键'].rsplit('-', 1)[-1] + f"({it['估高行数']})" for it in rank[:NRULE + 1]))
if NRULE > 0:
    check(f'判模间隔：第{NRULE}名>第{NRULE+1}名(≥1行)', rank[NRULE - 1]['估高行数'] > rank[NRULE]['估高行数'],
          f"{NRULE}th={rank[NRULE-1]['键'].rsplit('-',1)[-1]}:{rank[NRULE-1]['估高行数']}"
          f" {NRULE+1}th={rank[NRULE]['键'].rsplit('-',1)[-1]}:{rank[NRULE]['估高行数']}")

doc = fitz.open(os.path.join(PIECE, 'main-true.pdf'))
gray_n, rule_lines, last_page_rules = 0, 0, 0
for pno, page in enumerate(doc, 1):
    for d in page.get_drawings():
        r = d['rect']
        if d['fill'] is not None and all(abs(c - 0.941) < 0.01 for c in d['fill']) \
                and r.width > 100 and r.height > 20:
            gray_n += 1
        elif d['fill'] is None and d['color'] is not None \
                and all(abs(c - 0.478) < 0.01 for c in d['color']) and r.width > 100:
            rule_lines += 1
            if pno == len(doc):
                last_page_rules += 1
doc.close()
check(f'渲染面：灰底大矩形＝{NKEY - NRULE}', gray_n == NKEY - NRULE, f'{gray_n}')
check(f'渲染面：ansrule 长线＝{NRULE}块×2＋尾框2＝{2*NRULE+2}', rule_lines == 2 * NRULE + 2, f'{rule_lines}')
check('渲染面：尾块框线在末页恰2', last_page_rules == 2, f'{last_page_rules}')
check(f'详解覆盖 {NKEY}/{NKEY}', all(k in note_vals for k in keyseq), f'{len(note_vals)}')
for it in items:
    it['判模'] = '括线' if it['键'] in ruled_set else '灰底'

json.dump({'keys': keyseq, 'vals': side, 'items': items}, open(OUT, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账底稿 →', OUT)
print('印面装配序（登记用）:', ' '.join(k.rsplit('-', 1)[-1] for k in order))
print()
print('值快照键型判模门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
