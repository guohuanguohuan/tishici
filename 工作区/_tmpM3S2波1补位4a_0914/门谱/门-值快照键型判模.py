# -*- coding: utf-8 -*-
r"""门-值快照键型判模.py — M3 S2 课时17·值快照逐字零漂＋全值型＋括线判模断言（波1补位臂4a）。

断言面（母版同构改造）：
  ①值快照（字节级）：main.tex 各键 \ansitem 第二参 ≡ 答案侧「值：」行原文——课时17
    全 42 键均值型逐字全等零换算。门归一化两处（注册，均在装配侧零字形纯记号）：
      a) 转义花括号：练17-11 值含字面 {}，tex 以 \{ \} 印制，门比对前 \{→{、\}→}；
      b) 弹性胶记号：拓17-04 值行断行校准加 \hspace{0pt plus 1.5em}（零字形纯弹性胶），
         门比对前整体剔除（其前原空格保留，剔除后与侧文逐字全等）。
  ②键型：42 键全「值」，与键序逐位对齐。
  ③括线判模（双证）：静态＝块内容估高（wlen：全角 1、ASCII 0.5，剔 \命令；栏宽 23 字
    口径）est＝ceil，est＞8 → 括线模；断言 tex 括线集 ≡ {est＞8} 集（39 键，边界干净：
    灰底 max est=8／括线 min est=9）；渲染面＝PDF 绘图对象硬计数：
    ansbg 灰底大矩形 3（＝42−39）、ansrule 长线 80（括线 39 块×2＋尾框 2）、
    尾框线以「笔记与错题整理」文本锚定上下各一线。
    逐键估高读数落盘 值台账底稿.json。
用法: python 门-值快照键型判模.py
退出码: 0＝全过；1＝有红。红线：件树/题面库只读；唯一写件＝值台账底稿.json（本过程件目录）。
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

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时17-2.8①压轴综合一'
SIDE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/课时17-2.8①压轴综合一-答案侧.md'
MANIFEST = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/课时17.manifest.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '值台账底稿.json')

NK_RULED = 39   # 括线块数（est＞8 集）
NK_GRAY = 3     # 灰底块数（42−39）
RULE_LINES = NK_RULED * 2 + 2  # 括线块×上下线＋尾框 2 线＝80

reds = []
def check(name, ok, detail=''):
    tag = '绿' if ok else '红'
    print(f'  [{tag}] {name}' + (f'｜{detail}' if detail else ''))
    if not ok:
        reds.append(name)

def braces(s, i):
    """s[i]=='{' → 平衡花括号体与闭位。"""
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

def normalize(tv):
    """门归一化（注册项，见头注）：转义花括号还原＋弹性胶记号剔除。"""
    tv = tv.replace(r'\{', '{').replace(r'\}', '}')
    tv = tv.replace(r'\hspace{0pt plus 1.5em}', '')
    return tv

# ---- 答案侧 ----
side_raw = open(SIDE, encoding='utf-8').read()
side = {}
for m in re.finditer(r'^%[ \t]*ans:(\S+)\s*\n值：(.*)$', side_raw, re.M):
    side[m.group(1)] = m.group(2).rstrip()

# ---- main.tex：ansblock 键 → ansitem 值（花括号平衡取参）＋括线包装＋印面号 ----
src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
tex_vals, note_vals, ruled_set, order, num_of = {}, {}, set(), [], {}
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
    ma = re.search(r'\\ansitem\{(\d+)\}\{', ls)
    if ma and cur:
        body, _ = braces(ls, ma.end() - 1)
        tex_vals[cur] = body
        num_of[cur] = int(ma.group(1))
    mn = re.search(r'\\ansnote\{详解\}\{', ls)
    if mn and cur:
        body, _ = braces(ls, mn.end() - 1)
        note_vals[cur] = body

def wlen(s):
    """有效墨宽当量：全角 1、ASCII 0.5；\\命令 记号不计墨。"""
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    return sum(0.5 if ord(c) < 128 else 1.0 for c in s)

manifest = json.load(open(MANIFEST, encoding='utf-8'))
keyseq = manifest['键序']

print('== ①② 值快照＋键型 ==')
items = []
for k in keyseq:
    tv, sv = tex_vals.get(k), side.get(k)
    ok = (tv is not None and normalize(tv) == sv)
    d = '逐字全等（归一化后）' if ok else f'tex={tv!r} 侧={sv!r}'
    check(f'{num_of.get(k, "?"):>2} {k} [值]', ok, d)
    est = math.ceil(wlen((tv or '') + (note_vals.get(k) or '')) / 23) if (tv or note_vals.get(k)) else 0
    items.append({'键': k, '印面号': num_of.get(k), '键型': '值', '值tex': tv, '值源': sv,
                  '估高行数': est, '值源字符': len(sv) if sv else 0,
                  '详解字符': len(re.sub(r'\\[a-zA-Z]+', '', note_vals.get(k) or ''))})

print('== ③ 括线判模（静态估高＋PDF 渲染面） ==')
est_ruled = {it['键'] for it in items if it['估高行数'] > 8}
check('tex括线集 ≡ {est＞8}集', ruled_set == est_ruled,
      f'tex={len(ruled_set)}键 est集={len(est_ruled)}键 '
      f'差={sorted(ruled_set ^ est_ruled)}')
grays = [it['估高行数'] for it in items if it['键'] not in ruled_set]
ruleds = [it['估高行数'] for it in items if it['键'] in ruled_set]
check('判模边界干净：灰底max≤8 且 括线min≥9',
      max(grays) <= 8 and min(ruleds) >= 9,
      f'灰底max={max(grays)} 括线min={min(ruleds)}')
check(f'括线块数={NK_RULED} 且 灰底块数={NK_GRAY}', len(ruled_set) == NK_RULED and len(items) - len(ruled_set) == NK_GRAY,
      f'括线{len(ruled_set)} 灰底{len(items) - len(ruled_set)}')

# PDF 渲染面：灰底大矩形（ansbg F0F0F0≈0.941）＝3；ansrule 长线（7A7A7A≈0.478）
# ＝括线 39 块×上下 2 线＋尾块框 2 线＝80。尾框判定以「笔记与错题整理」文本锚定
# 其所在栏中紧邻其上/下的两条 ansrule 长线为尾框对。
doc = fitz.open(os.path.join(PIECE, 'main-true.pdf'))
gray_n, rule_lines = 0, 0
tail_ok, tail_detail = False, ''
last_page = doc[len(doc) - 1]
hits = last_page.search_for('笔记与错题整理')
tail_top = tail_bot = None
for pno, page in enumerate(doc, 1):
    for d in page.get_drawings():
        r = d['rect']
        if d['fill'] is not None and all(abs(c - 0.941) < 0.01 for c in d['fill']) \
                and r.width > 100 and r.height > 20:
            gray_n += 1
        elif d['fill'] is None and d['color'] is not None \
                and all(abs(c - 0.478) < 0.01 for c in d['color']) and r.width > 100:
            rule_lines += 1
if len(hits) == 1:
    t = hits[0]
    col_x = 150 if t.x0 < 300 else 450
    col_rules = []
    for d in last_page.get_drawings():
        r = d['rect']
        if d['fill'] is None and d['color'] is not None \
                and all(abs(c - 0.478) < 0.01 for c in d['color']) and r.width > 100 \
                and abs(r.x0 - col_x) < 150:
            col_rules.append(r.y0)
    above = [y for y in col_rules if y <= t.y0 + 1]
    below = [y for y in col_rules if y >= t.y1 - 1]
    if above and below:
        tail_top, tail_bot = max(above), min(below)
        tail_ok = True
        tail_detail = f'尾框线 y={tail_top:.1f}/{tail_bot:.1f}（栏x≈{col_x}，隔 {tail_bot - tail_top:.0f}pt）'
    else:
        tail_detail = f'文本上方线{len(above)}条 下方线{len(below)}条'
else:
    tail_detail = f'「笔记与错题整理」命中{len(hits)}处'
doc.close()
check(f'渲染面：灰底大矩形＝{NK_GRAY}', gray_n == NK_GRAY, f'{gray_n}')
check(f'渲染面：ansrule 长线＝{NK_RULED}块×2＋尾框2＝{RULE_LINES}', rule_lines == RULE_LINES, f'{rule_lines}')
check('渲染面：尾块框线（文本锚定上下各一线）', tail_ok, tail_detail)
check(f'详解覆盖 {len(keyseq)}/{len(keyseq)}', all(k in note_vals for k in keyseq), f'{len(note_vals)}')
for it in items:
    it['判模'] = '括线' if it['键'] in ruled_set else '灰底'

json.dump({'keys': keyseq, 'vals': side, 'items': items}, open(OUT, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账底稿 →', OUT)
print()
print('值快照键型判模门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
