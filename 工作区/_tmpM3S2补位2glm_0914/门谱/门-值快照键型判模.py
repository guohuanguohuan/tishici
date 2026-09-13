# -*- coding: utf-8 -*-
r"""门-值快照键型判模.py — M3 S2 波1臂2（课时04/05/06）·值快照逐字零漂＋键型＋括线判模断言。
母版件＝工作区/_tmpM3S2母版0914/门谱/门-值快照键型判模.py；三处按派工门谱调整（不放宽）：
  ①括线判据＝承重墙阈值「块估高＞8 行 → 括线模」（toolchain钉档§三.1 原文口径；母版件 top-5
    制在 E11 估高10 仍灰底，阈值制严格更严，禁放宽）；
  ②本片组无过程型/T锚制键（先逐键识别「证明见详解．」值与⟺/⟹/下标锚制需求，有则自动转锚制档）；
  ③渲染面硬计数由判模集实算：灰底大矩形＝灰底块数；ansrule 长线＝2×括线块数＋2（尾框）。
断言面：值快照（字节级）tex\ansitem 值≡答案侧「值：」行；键型两档（值/过程）；
  详解覆盖；键序≡manifest；逐键估高读数落盘 值台账底稿-<件>.json（本过程件目录）。
用法: python 门-值快照键型判模.py <件04|05|06>
退出码: 0＝全过；1＝有红。红线：件树/题面库只读；唯一写件＝本目录 值台账底稿-<件>.json。
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

ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
PIECES = {
    '04': ('课时04-点斜式与斜截式', '课时04-点斜式与斜截式'),
    '05': ('课时05-两点式与一般式', '课时05-两点式与一般式'),
    '06': ('课时06-两条直线的位置关系', '课时06-两条直线的位置关系'),
}
tag = sys.argv[1] if len(sys.argv) > 1 else '04'
assert tag in PIECES
DIR, SIDE = PIECES[tag]
PIECE = f'{ROOT}/成卷/导学件/{DIR}'
SIDE = f'{ROOT}/成卷/题面库/{SIDE}-答案侧.md'
MANIFEST = f'{ROOT}/成卷/题面库/manifest/课时{tag}.manifest.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'值台账底稿-{tag}.json')
THRESH = 8  # 承重墙：估高＞THRESH 行 → 括线

reds = []
def check(name, ok, detail=''):
    t = '绿' if ok else '红'
    print(f'  [{t}] {name}' + (f'｜{detail}' if detail else ''))
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

# ---- 答案侧 ----
side_raw = open(SIDE, encoding='utf-8').read()
side = {}
for m in re.finditer(r'^%[ \t]*ans:(\S+)\s*\n值：(.*)$', side_raw, re.M):
    side[m.group(1)] = m.group(2).rstrip()

# ---- main.tex：ansblock 键 → ansitem 值＋括线包装 ----
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
N = len(keyseq)
check('装配序集合≡manifest键集合', set(order) == set(keyseq) and len(order) == N, f'{len(order)}块')

print(f'== ①② 值快照＋键型（N={N}，全键字节级） ==')
items = []
for idx, k in enumerate(order, 1):
    tv, sv = tex_vals.get(k), side.get(k)
    # 键型自动档：值≡「证明见详解．」＝过程型；含⟺/Unicode下标不可直排＝锚制（本片应零命中）
    need_anchor = tv != sv and sv is not None and re.search(r'[⟺⟹₂₁₀]|≤|≥', sv or '') and (sv or '') != tv
    kt = '过程' if sv == '证明见详解．' else ('锚制?' if need_anchor else '值')
    ok = (tv == sv)
    d = '逐字全等' if ok else f'tex={tv!r} 侧={sv!r}'
    check(f'{idx:>2} {k} [{kt}]', ok, d)
    est = math.ceil(wlen((tv or '') + (note_vals.get(k) or '')) / 23) if (tv or note_vals.get(k)) else 0
    items.append({'键': k, '印面号': idx, '键型': kt, '值tex': tv, '值源': sv,
                  '估高行数': est, '值源字符': len(sv) if sv else 0,
                  '详解字符': len(re.sub(r'\\[a-zA-Z]+', '', note_vals.get(k) or ''))})
check('键型两档：无「锚制?」残留（全键直排零漂）', all(it['键型'] != '锚制?' for it in items),
      str(sorted({it['键型'] for it in items})))

print('== ③ 括线判模（承重墙阈值 est>8 ∪ display/图 → 括线） ==')
disp = {k for k, v in note_vals.items() if re.search(r'\\\[|\\begin\{(align|gather)', v or '')}
exp_ruled = {it['键'] for it in items if it['估高行数'] > THRESH} | disp
rank = sorted(items, key=lambda x: -x['估高行数'])
print('  top-8 估高：', '，'.join(f"{it['键'].rsplit('-',1)[-1]}:{it['估高行数']}" for it in rank[:8]))
check(f'括线集≡估高＞{THRESH}（含display/图）', ruled_set == exp_ruled,
      f'tex括线={sorted(k.rsplit("-",1)[-1] for k in ruled_set)} 期望={sorted(k.rsplit("-",1)[-1] for k in exp_ruled)}')

# PDF 渲染面
n_ruled, n_gray = len(ruled_set), N - len(ruled_set)
doc = fitz.open(os.path.join(PIECE, 'main-true.pdf'))
gray_n, rule_lines, last_page_rules = 0, 0, 0
for pno, page in enumerate(doc, 1):
    for dd in page.get_drawings():
        r = dd['rect']
        if dd['fill'] is not None and all(abs(c - 0.941) < 0.01 for c in dd['fill']) \
                and r.width > 100 and r.height > 20:
            gray_n += 1
        elif dd['fill'] is None and dd['color'] is not None \
                and all(abs(c - 0.478) < 0.01 for c in dd['color']) and r.width > 100:
            rule_lines += 1
            if pno == len(doc):
                last_page_rules += 1
doc.close()
check(f'渲染面：灰底大矩形＝{n_gray}', gray_n == n_gray, f'{gray_n}')
check(f'渲染面：ansrule 长线＝2×{n_ruled}＋尾框2＝{2*n_ruled+2}', rule_lines == 2 * n_ruled + 2, f'{rule_lines}')
# 尾块判定改为结构锚定（母版件「末页 rules==2」隐含末页无括线块；本片 T1 括线块跨页，
# 末页多 1 条括线端线属合法形态——总条数仍由上一断言锁死，此处只验尾块上下线各恰1）
# 06 补位臂2 修订（2026-09-14，非放宽）：末位括线块（G5 est=11＞8 承重墙强制括线）与尾块
#   共页为装配结构必然，紧贴尾块文字的 hug 线才是尾块框线；故 above/below 收紧为
#   ±8pt 贴窗内各恰1，末页宽线总数仍受上一断言（ansrule=2×括线+2）全局锁定。
TAIL_HUG_PT = 8
doc = fitz.open(os.path.join(PIECE, 'main-true.pdf'))
last = doc[len(doc) - 1]
lrs = [d['rect'] for d in last.get_drawings()
       if d['fill'] is None and d['color'] and all(abs(c - 0.478) < 0.01 for c in d['color'])
       and d['rect'].width > 100]
hits = last.search_for('笔记与错题整理')
ok_tail = bool(hits)
if hits:
    tr = hits[0]
    # above＝贴窗（排除同栏远端括线端线）；below＝无界（书写区使底框线远离文字，04 裁定语义）
    above = [r for r in lrs if r.x0 < tr.x1 and r.x1 > tr.x0 and tr.y0 - TAIL_HUG_PT <= r.y1 <= tr.y0 + 1]
    below = [r for r in lrs if r.x0 < tr.x1 and r.x1 > tr.x0 and r.y0 >= tr.y1 - 1]
    ok_tail = len(above) == 1 and len(below) == 1
    print(f'  末页括线端线共 {len(lrs)} 条（尾块判定：上贴窗±{TAIL_HUG_PT}pt／下无界）')
check('渲染面：尾块「笔记与错题整理」上下框线各恰1', ok_tail, f'末页线{len(lrs)} 命中{len(hits)}')
check(f'详解覆盖 {N}/{N}', all(k in note_vals for k in keyseq), f'{len(note_vals)}')
for it in items:
    it['判模'] = '括线' if it['键'] in ruled_set else '灰底'

json.dump({'keys': keyseq, 'vals': side, 'items': items},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('值台账底稿 →', OUT)
print()
print('值快照键型判模门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
