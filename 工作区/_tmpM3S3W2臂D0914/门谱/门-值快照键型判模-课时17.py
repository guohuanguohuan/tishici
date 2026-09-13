# -*- coding: utf-8 -*-
r"""门-值快照键型判模-课时17.py — M3 S3 W2臂D 课时17 练习件·值快照逐字零漂＋键型两档＋全线括线判模断言。
（照抄 W2臂B 门谱 门-值快照键型判模-课时08.py，PIECE/SIDE/MANIFEST/OUT/PROC 常量换片：
本片 16 键答案侧值全为具体值，PROC（「证明见详解．」过程型）＝空集。
片内唯一断言面适配＝值行 TeX 转义对归一（\{ \} ↔ { }，17-11 集合括号一处；印面须显示花括号
故用 \{，导学件17 ansitem 同变换在案，值语义零漂）。）
用法: python 门-值快照键型判模-课时17.py   退出码: 0＝全过；1＝有红。
红线：件树/题面库只读；唯一写件＝底稿-课时17.json（本过程件目录）。
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

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时17-2.8①压轴综合一'
SIDE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/课时17-2.8①压轴综合一-答案侧.md'
MANIFEST = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/课时17.manifest.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '底稿-课时17.json')

PROC = set()  # 本片无「证明见详解．」过程键；16 键全值型

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

# ---- main.tex：ansblock 键 → ansitem 值（花括号平衡取参）＋全线括线断言 ----
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
    """有效墨宽当量：全角 1、ASCII 0.5；\\命令 记号不计墨。"""
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    return sum(0.5 if ord(c) < 128 else 1.0 for c in s)

manifest = json.load(open(MANIFEST, encoding='utf-8'))
keyseq = [k for k in manifest['键序'] if k.startswith('2章-练-')]

print('== ①② 值快照＋键型 ==')
items = []
def norm_texesc(s):
    # 印面 TeX 转义对 \\{ \\} ↔ 源明文 { }：纯渲染对归一，值语义零漂
    # （17-11 集合括号一处；导学件17 ansitem 同变换在案，印面须显示花括号故用 \{）
    return s.replace('\\{', '{').replace('\\}', '}')
for i, k in enumerate(keyseq, 1):
    tv, sv = tex_vals.get(k), side.get(k)
    if k in PROC:
        kt = '过程'
        ok = (tv == sv == '证明见详解．')
        d = '全等' if ok else f'tex={tv!r} 侧={sv!r}'
    else:
        kt = '值'
        ok = (norm_texesc(tv or '') == (sv or ''))
        d = '逐字全等' if ok else f'tex={tv!r} 侧={sv!r}'
    check(f'{i:>2} {k} [{kt}]', ok, d)
    est = math.ceil(wlen((tv or '') + (note_vals.get(k) or '')) / 23) if (tv or note_vals.get(k)) else 0
    items.append({'键': k, '印面号': i, '键型': kt, '值tex': tv, '值源': sv,
                  '值快照': '逐字全等' if ok else '漂移',
                  '估高行数': est, '值源字符': len(sv) if sv else 0,
                  '详解字符': len(re.sub(r'\\[a-zA-Z]+', '', note_vals.get(k) or ''))})

print('== ③ 全线括线判模（导言置定＋零逐块包装＋PDF 渲染面） ==')
pre, _doc = src.split('\\begin{document}', 1)
n_pre = len(re.findall(r'^\\ansblockgrayfalse\s*$', pre, re.M))
check('导言 \\ansblockgrayfalse 恰1（一次置定）', n_pre == 1, f'{n_pre}')
check('件内零逐块 {\\ansblockgrayfalse 包装（导言置定后不切换）', len(ruled_set) == 0,
      f'{sorted(ruled_set)}')
# PDF 渲染面：练习件全线括线 → ansbg(0.941) 灰底大矩形＝0；ansrule(0.478) 长线
# ＝16 块×上下 2 线＋尾块框 2 线＝34；尾框对＝末页绘图序最后两根（同列纵列）。
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
check('渲染面：ansbg 灰底大矩形＝0（练习件禁灰底）', gray_n == 0, f'{gray_n}')
check('渲染面：ansrule 长线＝16块×2＋尾框2＝34', rule_lines == 34, f'{rule_lines}')
tail_pair = False
doc = fitz.open(os.path.join(PIECE, 'main-true.pdf'))
page = doc[len(doc) - 1]
seq = [d['rect'] for d in page.get_drawings()
       if d['fill'] is None and d['color'] is not None
       and all(abs(c - 0.478) < 0.01 for c in d['color']) and d['rect'].width > 100]
doc.close()
if len(seq) >= 2:
    a, b = seq[-2], seq[-1]
    tail_pair = abs(a.x0 - b.x0) < 1 and b.y0 > a.y0
check('渲染面：尾块框线对＝末页绘图序最后两根（同列纵列）', tail_pair,
      f'末页{len(seq)}根，末两根y=({seq[-2].y0:.1f},{seq[-1].y0:.1f})' if len(seq) >= 2 else '不足2根')
check('详解覆盖 16/16', all(k in note_vals for k in keyseq), f'{len(note_vals)}')
for it in items:
    it['判模'] = '括线'

json.dump({'keys': keyseq, 'vals': side, 'items': items}, open(OUT, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账底稿 →', OUT)
print()
print('值快照键型判模门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
