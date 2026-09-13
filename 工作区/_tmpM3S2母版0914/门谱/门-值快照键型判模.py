# -*- coding: utf-8 -*-
r"""门-值快照键型判模.py — M3 S2 课时01 母版·值快照逐字零漂＋键型两档＋括线判模断言。

断言面：
  ①值快照（字节级）：main.tex 各键 \ansitem 第二参 ≡ 答案侧「值：」行原文——
      值型 17 键逐字全等；过程型 E8/E11/E13/E14（答案侧值＝「证明见详解．」）亦全等；
      T1/T2（tex 侧 ⟺→$\iff$、x₁→x_1 数学下标换算）＝锚制断言：
        首锚「(1)见详解；」＋末锚（T1「等号不成立」／T2「在该矩形外．」）
        ＋长度比 len(tex)/len(答案侧) ∈ [0.8, 2.0]。
  ②键型两档：值型17＋过程型6（E8/E11/E13/E14/T1/T2）＝23，与键序逐位对齐。
  ③括线判模（双证）：静态＝块内容估高（wlen：全角 1、ASCII 0.5，剔 \命令；栏宽 23 字
    口径）top-5 键 → 括线模，且第 5/6 名估高间隔 ≥1 行；渲染面＝PDF 绘图对象硬计数：
    ansbg 灰底大矩形 18、ansrule 长线 12（括线 5 块×2＋尾框 2）、尾框线在末页恰 2。
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

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时01-坐标法'
SIDE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/课时01-坐标法-答案侧.md'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '值台账底稿.json')

PROC = {f'2章-练-课时01-E{k}' for k in (8, 11, 13, 14)}
PROC_T = {'2章-拓-课时01-T1': '等号不成立', '2章-拓-课时01-T2': '在该矩形外．'}
ANCHOR_HEAD = '(1)见详解；'
NUM = '2章-练-课时01-E4:1,E1:2,E5:3,E6:4,E9:5,E8:6,E7:7,E2:8,E3:9,E11:10,E14:11,E13:12,E10:13,E12:14,E15:15,E16:16,2章-拓-课时01-T1:17,T2:18,2章-导-课时01-G1:19,G2:20,G3:21,G4:22,G5:23'

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
        num_of = cur
    mn = re.search(r'\\ansnote\{详解\}\{', ls)
    if mn and cur:
        body, _ = braces(ls, mn.end() - 1)
        note_vals[cur] = body

def wlen(s):
    """有效墨宽当量：全角 1、ASCII 0.5；\\命令 记号不计墨。"""
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    return sum(0.5 if ord(c) < 128 else 1.0 for c in s)

manifest = json.load(open('C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/课时01.manifest.json', encoding='utf-8'))
keyseq = manifest['键序']
# 印面号映射（连号 1–23＝探究1—18＋评价19—23，见 main.tex 头注）
num_map = {}
for seg in NUM.split(','):
    k, n = seg.rsplit(':', 1)
    if k.startswith('2章'):
        num_map[k] = int(n)
    else:
        base = '2章-练-课时01-' if k.startswith('E') else '2章-导-课时01-'
        if k.startswith('T'):
            base = '2章-拓-课时01-'
        num_map[base + k] = int(n)

print('== ①② 值快照＋键型 ==')
items = []
for k in keyseq:
    tv, sv = tex_vals.get(k), side.get(k)
    if k in PROC:
        kt = '过程'
        ok = (tv == sv == '证明见详解．')
        d = '全等' if ok else f'tex={tv!r} 侧={sv!r}'
    elif k in PROC_T:
        kt = '过程-T'
        ok = (tv is not None and tv.startswith(ANCHOR_HEAD)
              and PROC_T[k] in tv and sv is not None and 0.8 <= len(tv) / len(sv) <= 2.0)
        d = f'len比={len(tv)/len(sv):.2f}' if ok else f'tex={tv!r}'
    else:
        kt = '值'
        ok = (tv == sv)
        d = '逐字全等' if ok else f'tex={tv!r} 侧={sv!r}'
    check(f'{num_map[k]:>2} {k} [{kt}]', ok, d)
    est = math.ceil(wlen((tv or '') + (note_vals.get(k) or '')) / 23) if (tv or note_vals.get(k)) else 0
    items.append({'键': k, '印面号': num_map[k], '键型': kt, '值tex': tv, '值源': sv,
                  '估高行数': est, '值源字符': len(sv) if sv else 0,
                  '详解字符': len(re.sub(r'\\[a-zA-Z]+', '', note_vals.get(k) or ''))})

print('== ③ 括线判模（静态估高＋PDF 渲染面） ==')
check('tex括线键集', ruled_set == {'2章-练-课时01-E2', '2章-练-课时01-E3',
                                   '2章-练-课时01-E14', '2章-拓-课时01-T1',
                                   '2章-拓-课时01-T2'},
      ','.join(sorted(ruled_set)))
rank = sorted(items, key=lambda x: -x['估高行数'])
top5 = {it['键'] for it in rank[:5]}
check('估高 top-5 ≡ tex括线集', top5 == ruled_set,
      'top5=' + ','.join(it['键'].rsplit('-', 1)[-1] for it in rank[:5]))
check('判模间隔：第5名>第6名(≥1行)', rank[4]['估高行数'] > rank[5]['估高行数'],
      f"5th={rank[4]['键'].rsplit('-',1)[-1]}:{rank[4]['估高行数']} 6th={rank[5]['键'].rsplit('-',1)[-1]}:{rank[5]['估高行数']}")

# PDF 渲染面：灰底大矩形（ansbg F0F0F0≈0.941）＝18；ansrule 长线（7A7A7A≈0.478）
# ＝括线 5 块×上下 2 线＋尾块框 2 线＝12；尾块框线恒在末页。
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
check('渲染面：灰底大矩形＝18', gray_n == 18, f'{gray_n}')
check('渲染面：ansrule 长线＝5块×2＋尾框2＝12', rule_lines == 12, f'{rule_lines}')
check('渲染面：尾块框线在末页恰2', last_page_rules == 2, f'{last_page_rules}')
check('详解覆盖 23/23', all(k in note_vals for k in keyseq), f'{len(note_vals)}')
for it in items:
    it['判模'] = '括线' if it['键'] in ruled_set else '灰底'

json.dump({'keys': keyseq, 'vals': side, 'items': items}, open(OUT, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账底稿 →', OUT)
print()
print('值快照键型判模门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
