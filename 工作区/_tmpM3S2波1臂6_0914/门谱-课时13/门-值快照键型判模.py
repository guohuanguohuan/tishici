# -*- coding: utf-8 -*-
r"""门-值快照键型判模.py — M3 S2 波1 臂6 课时13·值快照逐字零漂＋全值型＋括线判模断言。
参数化自 母版 门谱，常量换片：PIECE/SIDE/NUM/21；课时13 无过程型键（21 键全值型）。
断言面：
  ①值快照（字节级）：main.tex 各键 \ansitem 第二参 ≡ 答案侧「值：」行原文（21 键逐字全等）。
  ②印面号：ansitem 首参 ≡ 装配序连号 1..21（探究1—16＋课堂评价17—21），键↔号入台账。
  ③括线判模（承重墙判据，双证）：
    静态＝块内容估高（wlen：全角 1、ASCII 0.5，剔 \命令；栏宽 23 字口径）＞8 行 → 括线模；
    tex 括线集 ≡ {估高>8}；灰/括最小间隔：末名括线估高 ＞ 首名灰底估高（≥1 行）。
    渲染面＝main-true.pdf 绘图对象硬计数：ansbg 灰底大矩形＝21−括线数；
    ansrule 长线＝括线块×2＋尾框 2；尾框线在末页恰 2。
    逐键估高读数落盘 值台账底稿-课时13.json（本过程件目录）。
用法: python 门-值快照键型判模.py
退出码: 0＝全过；1＝有红。红线：件树/题面库只读；唯一写件＝值台账底稿-课时13.json。
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

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时13-2.6.1双曲线的标准方程'
SIDE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/课时13-2.6.1双曲线的标准方程-答案侧.md'
MANIFEST = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/课时13.manifest.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '值台账底稿-课时13.json')
NKEYS = 21
# 印面号映射（装配序连号 1–21＝探究1—16＋评价17—21，见 main.tex 头注；键尾段→号）
NUM = {'简1': 1, '简9': 2, '简3': 3, '简4': 4, '简10': 5, '简2': 6,
       '简5': 7, '简6': 8, '简7': 9, '简8': 10, '中1': 11, '中2': 12, '中3': 13,
       '中4': 14, '难1': 15, '难2': 16,
       'G1': 17, 'G2': 18, 'G3': 19, 'G4': 20, 'G5': 21}

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

# ---- 答案侧 ----
side_raw = open(SIDE, encoding='utf-8').read()
side = {}
for m in re.finditer(r'^%[ \t]*ans:(\S+)\s*\n值：(.*)$', side_raw, re.M):
    side[m.group(1)] = m.group(2).rstrip()

# ---- main.tex：ansblock 键 → ansitem 值（花括号平衡取参）＋括线包装 ----
src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
tex_vals, note_vals, ruled_set, order = {}, {}, set(), []
pending_gray = False
for ln in src.split('\n'):
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
    ma = re.search(r'\\ansitem\{(\d+)\}\{', ls)
    if ma and cur:
        body, _ = braces(ls, ma.end() - 1)
        tex_vals[cur] = body
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
num_map = {k: NUM[k.rsplit('-', 1)[-1]] for k in keyseq}

print('== ①② 值快照（全值型·逐字全等）＋印面号 ==')
items = []
for k in keyseq:
    tv, sv = tex_vals.get(k), side.get(k)
    ok = (tv == sv)
    check(f'{num_map[k]:>2} {k} [值]', ok, '逐字全等' if ok else f'tex={tv!r} 侧={sv!r}')
    est = math.ceil(wlen((tv or '') + (note_vals.get(k) or '')) / 23) if (tv or note_vals.get(k)) else 0
    items.append({'键': k, '印面号': num_map[k], '键型': '值', '值tex': tv, '值源': sv,
                  '估高行数': est, '值源字符': len(sv) if sv else 0,
                  '详解字符': len(re.sub(r'\\[a-zA-Z]+', '', note_vals.get(k) or ''))})
check('印面号≡1..21 连号', sorted(num_map.values()) == list(range(1, NKEYS + 1)), '')
check('ansitem 首参序≡1..21', [int(n) for n in re.findall(r'\\ansitem\{(\d+)\}\{', src)]
      == list(range(1, NKEYS + 1)), '')

print('== ③ 括线判模（承重墙：est>8→括线；间隔≥1 行；渲染面硬计数） ==')
est_over = {it['键'] for it in items if it['估高行数'] > 8}
check('tex括线集≡{估高>8}（承重墙判据）', ruled_set == est_over,
      f'tex={",".join(sorted(ruled_set))} est={",".join(sorted(est_over))}')
rank = sorted(items, key=lambda x: -x['估高行数'])
nruled = len(ruled_set)
if 0 < nruled < NKEYS:
    check('灰/括最小间隔：末名括线＞首名灰底（≥1行）',
          rank[nruled - 1]['估高行数'] > rank[nruled]['估高行数'],
          f"括末={rank[nruled - 1]['键'].rsplit('-', 1)[-1]}:{rank[nruled - 1]['估高行数']} "
          f"灰首={rank[nruled]['键'].rsplit('-', 1)[-1]}:{rank[nruled]['估高行数']}")

doc = fitz.open(os.path.join(PIECE, 'main-true.pdf'))
gray_n, rules_pages = 0, []
for pno, page in enumerate(doc, 1):
    for d in page.get_drawings():
        r = d['rect']
        if d['fill'] is not None and all(abs(c - 0.941) < 0.01 for c in d['fill']) \
                and r.width > 100 and r.height > 20:
            gray_n += 1
        elif d['fill'] is None and d['color'] is not None \
                and all(abs(c - 0.478) < 0.01 for c in d['color']) and r.width > 100:
            rules_pages.append(pno)
doc.close()
check(f'渲染面：灰底大矩形＝{NKEYS}−括线{nruled}＝{NKEYS - nruled}', gray_n == NKEYS - nruled, f'{gray_n}')
check(f'渲染面：ansrule 长线＝{nruled}块×2＋尾框2＝{2 * nruled + 2}',
      len(rules_pages) == 2 * nruled + 2, f'{len(rules_pages)}')
check('渲染面：尾块框线（文档序末2条）在末页',
      len(rules_pages) >= 2 and rules_pages[-1] == rules_pages[-2] == max(rules_pages),
      f'末2条所在页={rules_pages[-2:]} 末页={max(rules_pages) if rules_pages else "-"}')
check(f'详解覆盖 {NKEYS}/{NKEYS}', all(k in note_vals for k in keyseq), f'{len(note_vals)}')
for it in items:
    it['判模'] = '括线' if it['键'] in ruled_set else '灰底'

json.dump({'keys': keyseq, 'vals': side, 'items': items},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('值台账底稿 →', OUT)
print()
print('值快照键型判模门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
