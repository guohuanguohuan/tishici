# -*- coding: utf-8 -*-
r"""门-值快照键型判模.py — M3 S2 波1 臂1 衔接节·值快照零漂＋键型＋括线判模断言。
参数化自 母版 门谱（_tmpM3S2母版0914/门谱/），常量换片：PIECE/SIDE/键序/括线集/号映射。
断言面：
  ①值快照（字节级）：main.tex 各键 \ansitem 第二参 ≡ 答案侧「值：」行原文——
      26 键逐字全等；1 键（2章-练-衔接-10）＝清洗制：tex 侧含 2 枚 \\allowbreak 断行提示
      （TeX 吞随空、墨面零变化），剔 `\\allowbreak\\s*` 后逐字全等。
  ②键型两档：本件 27 键值面全部可逐字核（无「证明见详解．」纯过程键）；
      过程性内容一律落 \\ansnote{详解}，27/27 键均有详解行。
  ③括线判模（承重墙口径，禁放宽）：块内容估高（wlen：全角1·ASCII0.5，剔\\命令；
      栏宽 23 字口径）行数 **>8** 者转括线，断言 括线集 ≡ {估高>8}；
      顶格 8 行（探5/探2/G2）按严格 >8 口径留灰底，登记不转。
      渲染面＝PDF 绘图对象硬计数：灰底大矩形＝27−4＝23、ansrule 长线＝括线4块×2＋尾框2＝10、
      尾框线在末页恰 2。
  ④双档三零读数（^! 错／Overfull／Underfull／Missing character＝0；ANSKEY＝27）＋false≤true 页数。
用法: python 门-值快照键型判模.py
退出码: 0＝全过；1＝有红。红线：件树/题面库只读；唯一写件＝值台账底稿-衔接节.json（本过程件目录）。
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

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/衔接节'
SIDE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/衔接节-答案侧.md'
MANIFEST = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/衔接节.manifest.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '值台账底稿-衔接节.json')
NKEYS = 27
THRESH = 8  # 承重墙：估高行数 >THRESH 才转括线
RULED = {'2章-练-衔接-1', '2章-练-衔接-6', '2章-练-衔接-7', '2章-练-衔接-8'}
# 清洗制：tex 侧为版面加的零墨记号 → 剔除后须与答案侧逐字全等
NORM = {'2章-练-衔接-10': r'\\allowbreak\s*'}
# 印面装配序：探1—探6→1—6；G1—G5→7—11；练-1—练-16→12—27
NUM = ('2章-导-衔接-探1:1,探2:2,探3:3,探4:4,探5:5,探6:6,'
       '2章-导-衔接-G1:7,G2:8,G3:9,G4:10,G5:11,'
       '2章-练-衔接-1:12,2:13,3:14,4:15,5:16,6:17,7:18,8:19,9:20,10:21,'
       '11:22,12:23,13:24,14:25,15:26,16:27')

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
cur = None
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


keyseq = json.load(open(MANIFEST, encoding='utf-8'))['键序']
num_map = {}
for seg in NUM.split(','):
    k, n = seg.rsplit(':', 1)
    if k.startswith('2章'):
        base = None
        num_map[k] = int(n)
    elif k.startswith('探'):
        num_map['2章-导-衔接-' + k] = int(n)
    elif k.startswith('G'):
        num_map['2章-导-衔接-' + k] = int(n)
    else:
        num_map['2章-练-衔接-' + k] = int(n)
assert len(num_map) == NKEYS and set(num_map) == set(keyseq), '号映射≡manifest键集 失败'

print('== ①② 值快照＋键型 ==')
items = []
for k in keyseq:
    tv, sv = tex_vals.get(k), side.get(k)
    if k in NORM:
        ok = (tv is not None and sv is not None and re.sub(NORM[k], '', tv) == sv)
        snap = f'剔{NORM[k]!r}后逐字全等'
        kt = '值(清洗)'
    else:
        ok = (tv == sv)
        snap = '逐字全等'
        kt = '值'
    check(f'{num_map[k]:>2} {k} [{kt}]', ok, snap if ok else f'tex={tv!r} 侧={sv!r}')
    est = math.ceil(wlen((tv or '') + (note_vals.get(k) or '')) / 23) if (tv or note_vals.get(k)) else 0
    items.append({'键': k, '印面号': num_map[k], '键型': kt, '值tex': tv, '值源': sv,
                  '值快照': snap, '估高行数': est, '值源字符': len(sv) if sv else 0,
                  '详解字符': len(re.sub(r'\\[a-zA-Z]+', '', note_vals.get(k) or ''))})

print('== ③ 括线判模（承重墙 est>8 ≡ 括线集＋PDF 渲染面） ==')
check(f'tex括线键集≡登记集({len(RULED)}块)', ruled_set == RULED, ','.join(sorted(ruled_set)))
over = {it['键'] for it in items if it['估高行数'] > THRESH}
check(f'承重墙：括线集 ≡ {{估高>{THRESH}行}}', ruled_set == over,
      '超阈未转=' + ','.join(sorted(over - ruled_set)) + ' 顶格误转=' + ','.join(sorted(ruled_set - over)))
rank = sorted(items, key=lambda x: -x['估高行数'])
check('估高梯（前8）', True,
      '｜'.join(f"{it['印面号']}号{it['键'].rsplit('-', 1)[-1]}:{it['估高行数']}" for it in rank[:8]))
check(f'顶格 {THRESH} 行键留灰底（严格 > 口径）',
      all(it['估高行数'] <= THRESH for it in rank[len(RULED):][:3]),
      '｜'.join(f"{it['印面号']}号{it['键'].rsplit('-', 1)[-1]}:{it['估高行数']}" for it in rank[len(RULED):][:3]))

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
check(f'渲染面：灰底大矩形＝{NKEYS - len(RULED)}', gray_n == NKEYS - len(RULED), f'{gray_n}')
check(f'渲染面：ansrule 长线＝{len(RULED)}块×2＋尾框2＝{len(RULED) * 2 + 2}',
      rule_lines == len(RULED) * 2 + 2, f'{rule_lines}')
check('渲染面：尾块框线在末页恰2', last_page_rules == 2, f'{last_page_rules}')
check(f'详解覆盖 {NKEYS}/{NKEYS}', all(k in note_vals for k in keyseq), f'{len(note_vals)}')
for it in items:
    it['判模'] = '括线' if it['键'] in ruled_set else '灰底'

print('== ④ 双档三零读数 ==')
read = {}
for tag in ('true', 'false'):
    t = open(os.path.join(PIECE, f'main-{tag}.log'), encoding='utf-8', errors='replace').read()
    pg = re.search(r'Output written on main-%s\.pdf \((\d+) pages' % tag, t)
    read[tag] = {'err': len(re.findall(r'^! ', t, re.M)),
                 'over': len(re.findall('Overfull', t)),
                 'under': len(re.findall('Underfull', t)),
                 'miss': len(re.findall('Missing character', t)),
                 'ans': len(re.findall(r'^M3-ANSKEY: ', t, re.M)),
                 'pages': int(pg.group(1)) if pg else -1}
    r = read[tag]
    check(f'{tag} 三零＋ANSKEY={NKEYS}',
          r['err'] == 0 and r['over'] == 0 and r['under'] == 0 and r['miss'] == 0 and r['ans'] == NKEYS,
          f"错{r['err']} 溢{r['over']} under{r['under']} 缺字{r['miss']} ANSKEY{r['ans']} {r['pages']}页")
check('页数门 false≤true', read['false']['pages'] <= read['true']['pages'],
      f"true={read['true']['pages']} false={read['false']['pages']}")

json.dump({'keys': keyseq, 'vals': side, 'items': items, '双档读数': read},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('值台账底稿 →', OUT)
print()
print('值快照键型判模门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
