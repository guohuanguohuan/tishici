# -*- coding: utf-8 -*-
r"""门-值快照键型判模.py — M3 S2 波1 臂4·课时09·值快照逐字零漂＋键型两档＋括线判模断言。
适配自母版门谱：PIECE/SIDE→课时09；PROC＝∅（本片 21 键全值型，T15 值「猜想正确，理由见解析」亦值型）；
括线判据 est>8 行 → top-3（T9/T14/T15），间隔断言第3/4名；渲染面计数 21−3＝18 灰底、3×2＋2＝8 长线。
唯一写件＝值台账底稿.json（本目录）。
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

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时14-2.6.2双曲线性质'
SIDE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/课时14-2.6.2双曲线性质-答案侧.md'
MANI = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/课时14.manifest.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '值台账底稿-课时14.json')

PROC = set()
RULED = set(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        '括线键-课时14.json'), encoding='utf-8')))
NRULE = len(RULED)
NKEY = 71
NUM = ('2章-练-课时14-01:1,2章-练-课时14-02:2,2章-练-课时14-07:3,2章-练-课时14-08:4,'
       '2章-拓-课时14-14:5,2章-拓-课时14-15:6,2章-拓-课时14-16:7,2章-拓-课时14-17:8,'
       '2章-练-课时14-03:9,2章-练-课时14-04:10,2章-练-课时14-11:11,2章-拓-课时14-07:12,'
       '2章-拓-课时14-19:13,2章-拓-课时14-20:14,2章-拓-课时14-21:15,2章-练-课时14-05:16,'
       '2章-练-课时14-06:17,2章-练-课时14-09:18,2章-练-课时14-10:19,2章-拓-课时14-18:20,'
       '2章-拓-课时14-23:21,2章-拓-课时14-24:22,2章-拓-课时14-27:23,2章-练-课时14-12:24,'
       '2章-练-课时14-13:25,2章-练-课时14-14:26,2章-拓-课时14-22:27,2章-拓-课时14-25:28,'
       '2章-拓-课时14-26:29,2章-拓-课时14-08:30,2章-拓-课时14-01:31,2章-拓-课时14-02:32,'
       '2章-拓-课时14-03:33,2章-拓-课时14-04:34,2章-拓-课时14-05:35,2章-拓-课时14-06:36,'
       '2章-拓-课时14-09:37,2章-拓-课时14-10:38,2章-拓-课时14-11:39,2章-拓-课时14-12:40,'
       '2章-拓-课时14-32-1:41,2章-拓-课时14-32-2:42,2章-拓-课时14-33-1:43,2章-拓-课时14-33-2:44,'
       '2章-拓-课时14-33-3:45,2章-拓-课时14-33-12:46,2章-拓-课时14-33-13:47,2章-拓-课时14-34-1:48,'
       '2章-拓-课时14-34-2:49,2章-拓-课时14-34-3:50,2章-拓-课时14-34-4:51,2章-拓-课时14-34-5:52,'
       '2章-拓-课时14-34-6:53,2章-练-课时14-15:54,2章-练-课时14-16:55,2章-拓-课时14-28:56,'
       '2章-拓-课时14-29:57,2章-拓-课时14-30:58,2章-拓-课时14-33-4:59,2章-拓-课时14-33-5:60,'
       '2章-拓-课时14-33-6:61,2章-拓-课时14-33-7:62,2章-拓-课时14-33-8:63,2章-拓-课时14-33-9:64,'
       '2章-拓-课时14-33-10:65,2章-拓-课时14-33-11:66,'
       '2章-导-课时14-G1:67,2章-导-课时14-G2:68,2章-导-课时14-G3:69,2章-导-课时14-G4:70,2章-导-课时14-G5:71')

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
        base = '2章-导-课时09-' if k.startswith('G') else '2章-练-课时09-'
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
check('tex括线键集≡{est>8}判定集', ruled_set == RULED, ','.join(sorted(ruled_set)))
check('全片估高>8 键集≡tex括线集（承重墙判据逐键）',
      {it['键'] for it in items if it['估高行数'] > 8} == RULED,
      ' '.join(f"{it['键'].rsplit('-',1)[-1]}:{it['估高行数']}" for it in items if it['估高行数'] > 8))
rank = sorted(items, key=lambda x: -x['估高行数'])
topn = {it['键'] for it in rank[:NRULE]}
check(f'估高 top-{NRULE} ≡ tex括线集', topn == ruled_set,
      'top=' + ','.join(it['键'].rsplit('-', 1)[-1] + f"({it['估高行数']})" for it in rank[:NRULE + 1]))
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
print()
print('值快照键型判模门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
