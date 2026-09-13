# -*- coding: utf-8 -*-
r"""门-值快照键型判模.py（波1臂3 参数化版）— 值快照逐字零漂＋键型两档＋括线判模断言。
用法: python 门-值快照键型判模.py <片目录> <答案侧md> <冻结manifest路径> <底稿out.json> \
        <括线键,逗号分隔> <键型表>（如 G1:值,T15:值 或 E8:过程,T1:过程-T:末锚文本）
断言面：①值快照（字节级）：\ansitem 第二参 ≡ 答案侧「值：」行（值/过程型逐字全等；
        过程-T 锚制：首锚「(1)见详解；」＋末锚＋长度比 0.8–2.0）。
        ②键型两档：值＋过程 计数对齐键序。
        ③括线判模（双证）：静态估高 top-5 ≡ tex括线集 且 第5/6名间隔≥1行；
        渲染面＝PDF 绘图对象硬计数（灰底大矩形、ansrule 长线、尾框线末页恰2）。
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

PIECE = sys.argv[1]
SIDE = sys.argv[2]
MANIFEST = sys.argv[3]
OUT = sys.argv[4]
RULED = set(x for x in sys.argv[5].split(',') if x)
KT_SPEC = sys.argv[6]  # 键尾短名:型[:末锚]
COLW = 23

reds = []
def check(name, ok, detail=''):
    tag = '绿' if ok else '红'
    print(f'  [{tag}] {name}' + (f'｜{detail}' if detail else ''))
    if not ok:
        reds.append(name)

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

manifest = json.load(open(MANIFEST, encoding='utf-8'))
keyseq = manifest['键序']

kt_map, proc_set, proct_map = {}, set(), {}
for seg in KT_SPEC.split(','):
    if not seg:
        continue
    parts = seg.split(':')
    tail, kt = parts[0], parts[1]
    full = [k for k in keyseq if k.endswith('-' + tail)]
    assert len(full) == 1, f'键型表键尾歧义: {tail}'
    kt_map[full[0]] = kt
    if kt == '过程':
        proc_set.add(full[0])
    if kt == '过程-T':
        proct_map[full[0]] = parts[2]
ANCHOR_HEAD = '(1)见详解；'

print('== ①② 值快照＋键型 ==')
items = []
for k in keyseq:
    tv, sv = tex_vals.get(k), side.get(k)
    kt = kt_map.get(k, '值')
    if kt == '过程':
        ok = (tv == sv)
        d = '全等' if ok else f'tex={tv!r} 侧={sv!r}'
    elif kt == '过程-T':
        ok = (tv is not None and tv.startswith(ANCHOR_HEAD)
              and proct_map[k] in tv and sv is not None and 0.8 <= len(tv) / len(sv) <= 2.0)
        d = f'len比={len(tv)/len(sv):.2f}' if ok else f'tex={tv!r}'
    else:
        ok = (tv == sv)
        d = '逐字全等' if ok else f'tex={tv!r} 侧={sv!r}'
    check(f'{order.index(k)+1:>2} {k} [{kt}]', ok, d)
    est = math.ceil(wlen((tv or '') + (note_vals.get(k) or '')) / COLW) if (tv or note_vals.get(k)) else 0
    items.append({'键': k, '印面号': order.index(k) + 1, '键型': kt, '值tex': tv, '值源': sv,
                  '估高行数': est, '值源字符': len(sv) if sv else 0,
                  '详解字符': len(re.sub(r'\\[a-zA-Z]+', '', note_vals.get(k) or ''))})

print('== ③ 括线判模（静态估高＋PDF 渲染面） ==')
check('tex括线键集', ruled_set == RULED, ','.join(sorted(ruled_set)))
rank = sorted(items, key=lambda x: -x['估高行数'])
top5 = {it['键'] for it in rank[:5]}
check('估高 top-5 ≡ tex括线集', top5 == RULED,
      'top5=' + ','.join(it['键'].rsplit('-', 1)[-1] for it in rank[:5]))
check('判模间隔：第5名>第6名(≥1行)', rank[4]['估高行数'] > rank[5]['估高行数'],
      f"5th={rank[4]['键'].rsplit('-',1)[-1]}:{rank[4]['估高行数']} 6th={rank[5]['键'].rsplit('-',1)[-1]}:{rank[5]['估高行数']}")

nruled = len(RULED)
gray_expect = len(keyseq) - nruled
rule_expect = nruled * 2 + 2
doc = fitz.open(os.path.join(PIECE, 'main-true.pdf'))
gray_n, rule_lines = 0, 0
tail_rules = 0
straddle_info = []
last_pno = len(doc)
page_rules = {}
for pno, page in enumerate(doc, 1):
    rules_here = []
    for dr in page.get_drawings():
        r = dr['rect']
        if dr['fill'] is not None and all(abs(c - 0.941) < 0.01 for c in dr['fill']) \
                and r.width > 100 and r.height > 20:
            gray_n += 1
        elif dr['fill'] is None and dr['color'] is not None \
                and all(abs(c - 0.478) < 0.01 for c in dr['color']) and r.width > 100:
            rule_lines += 1
            rules_here.append(r)
            if pno == last_pno:
                page_rules.setdefault('last', []).append(r)
    if rules_here:
        page_rules[pno] = rules_here
# 尾块框线（tailfill 无参书写区可弹性吃栏余量，框高不设上限）＝
#   顶线：与尾块文字同左缘(±3pt)且紧贴文字上方(|y1−ty0|<12pt)恰 1 条；
#   底线：同左缘线中 y 最大者，须在文字底下方(y0>ty1−2pt)；其余同缘/异缘长线＝括线跨页断线等（计 info）
lastpage = doc[last_pno - 1]
hits = lastpage.search_for('笔记与错题整理')
tail_ok = False
if hits:
    ty0, ty1 = hits[0].y0, hits[0].y1
    tx0 = hits[0].x0
    sameside = [r for r in page_rules.get('last', []) if abs(r.x0 - tx0) < 3]
    tops = [r for r in sameside if abs(r.y1 - ty0) < 12]
    bottoms = [r for r in sameside if r.y0 > ty1 - 2]
    r_bottom = max(bottoms, key=lambda r: r.y0) if bottoms else None
    tail_ok = (len(tops) == 1) and (r_bottom is not None)
    tail_rules = 2 if tail_ok else 0
    for r in page_rules.get('last', []):
        if not (abs(r.y1 - ty0) < 12 or (tail_ok and r is r_bottom)):
            straddle_info.append(round(r.y0, 1))
doc.close()
check(f'渲染面：灰底大矩形＝{gray_expect}', gray_n == gray_expect, f'{gray_n}')
check(f'渲染面：ansrule 长线＝{nruled}块×2＋尾框2＝{rule_expect}', rule_lines == rule_expect, f'{rule_lines}')
check('渲染面：尾块框线在末页恰2（顶线贴文字上方＋底线为同缘最低线）', tail_ok,
      f'尾邻{tail_rules}｜末页长线{len(page_rules.get("last", []))}（跨页断尾线{len(straddle_info)}：{straddle_info}）')
check(f'详解覆盖 {len(keyseq)}/{len(keyseq)}', all(k in note_vals for k in keyseq), f'{len(note_vals)}')
for it in items:
    it['判模'] = '括线' if it['键'] in ruled_set else '灰底'

json.dump({'keys': keyseq, 'vals': side, 'items': items}, open(OUT, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账底稿 →', OUT)
print()
print('值快照键型判模门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
