# -*- coding: utf-8 -*-
"""A1: 我方 PDF 字符级度量——标点占宽、行首行尾、字间空档、拉伸行占比。只读。"""
import json, math, collections
import pymupdf as fitz

PDF = r'C:/提示词/工作区/字替对照-0909/variantF/main.pdf'
doc = fitz.open(PDF)

PUNCT = set('。，、；：（）《》〈〉“”‘’！？…—')
HALF_PUNCT = set(',.;:()!?')

rows = []          # 每个字符：page, line_key, ch, x0,x1,y0,y1, size, font, adv
spans_all = []
for pno in range(doc.page_count):
    page = doc[pno]
    d = page.get_text('rawdict')
    for block in d['blocks']:
        if block.get('type') != 0:
            continue
        for line in block['lines']:
            for span in line['spans']:
                chars = span['chars']
                if not chars:
                    continue
                size = span['size']
                font = span['font']
                for i, ch in enumerate(chars):
                    c = ch['c']
                    x0, y0, x1, y1 = ch['bbox']
                    ox = ch['origin'][0]
                    if i + 1 < len(chars):
                        adv = chars[i + 1]['origin'][0] - ox
                    else:
                        adv = x1 - ox if x1 > ox else None
                    rows.append(dict(p=pno + 1, lk=f'{pno+1}-{round(span["origin"][1],1)}-{round(span["origin"][0],1)}',
                                     ch=c, x0=x0, x1=x1, y0=y0, y1=y1, adv=adv, size=size, font=font,
                                     ox=ox, oy=ch['origin'][1], ly=line['bbox'][1], lx0=line['bbox'][0], lx1=line['bbox'][2]))
                spans_all.append(dict(p=pno+1, size=size, font=font, text=''.join(c['c'] for c in chars),
                                      bbox=span['bbox'], origin=span['origin'], flags=span['flags']))

# ---- 字号/行距统计 ----
sizes = collections.Counter(round(r['size'], 2) for r in rows)
fonts = collections.Counter(r['font'] for r in rows)
print('=== 字号分布(字符数) ===')
for k, v in sizes.most_common(12):
    print(f'  {k}pt : {v}')
print('=== 字体分布 ===')
for k, v in fonts.most_common(12):
    print(f'  {k} : {v}')

# ---- 标点占宽（相对 em）----
print('\n=== 标点占宽（advance / em）===')
by = collections.defaultdict(list)
for r in rows:
    if r['ch'] in PUNCT or r['ch'] in HALF_PUNCT:
        if r['adv']:
            by[r['ch']].append(r['adv'] / r['size'])
for ch in sorted(by, key=lambda c: -len(by[c])):
    v = sorted(by[ch])
    n = len(v)
    print(f'  {ch!r} n={n:4d} adv/em 中位={v[n//2]:.3f} 均值={sum(v)/n:.3f} 范围=[{v[0]:.3f},{v[-1]:.3f}]')

# ---- 行首行尾标点 ----
linechars = collections.defaultdict(list)
for r in rows:
    linechars[r['lk']].append(r)
linechars = {k: sorted(v, key=lambda r: r['ox']) for k, v in linechars.items()}
head_p, tail_p = [], []
for lk, cs in linechars.items():
    txt = ''.join(c['ch'] for c in cs).strip()
    if not txt:
        continue
    if txt[0] in PUNCT:
        head_p.append((lk, txt[:12]))
    if txt[-1] in PUNCT:
        tail_p.append((lk, txt[-12:]))
print(f'\n=== 行首标点 {len(head_p)} 处 ===')
for lk, t in head_p[:20]:
    print('  ', lk, t)
print(f'=== 行尾标点 {len(tail_p)} 处（列前20）===')
for lk, t in tail_p[:20]:
    print('  ', lk, t)

# ---- 字间空档分布（同 span 内相邻 CJK/全角字符的 ink 间隙）----
# ink 间隙 = next.x0 - cur.x1（同一 span 内）
gaps = []
gaps_by_line = collections.defaultdict(list)
for lk, cs in linechars.items():
    for a, b in zip(cs, cs[1:]):
        if abs(a['oy'] - b['oy']) > 0.5:
            continue
        if a['adv'] is None:
            continue
        # 仅取两个均为全角字符（adv≈em）的情形
        if a['adv'] / a['size'] > 0.8 and (b['adv'] is None or b['adv'] / b['size'] > 0.8):
            g = b['x0'] - a['x1']
            if -0.5 < g < a['size']:
                gaps.append(g / a['size'])
                gaps_by_line[lk].append(g / a['size'])
print(f'\n=== 全角字间 ink 空档（/em）n={len(gaps)} ===')
if gaps:
    v = sorted(gaps)
    n = len(v)
    mean = sum(v) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in v) / n)
    print(f'  均值={mean:.4f} 中位={v[n//2]:.4f} 标准差={sd:.4f} p10={v[n//10]:.4f} p90={v[9*n//10]:.4f} max={v[-1]:.4f}')

# 每行最大空档 >0.5em 的行数（拉伸行）
stretch_lines = [lk for lk, gs in gaps_by_line.items() if gs and max(gs) > 0.5]
print(f'  含>0.5em空档的行: {len(stretch_lines)}/{len(gaps_by_line)}')
for lk in stretch_lines[:10]:
    print('   ', lk, [round(x,3) for x in gaps_by_line[lk] if x > 0.3][:8])

# ---- 正文行距（按页面栏内行基线）----
print('\n=== 行距（同栏相邻行 oy 差，pt）===')
for pno in [2, 3, 4]:
    oys = sorted({round(r['oy'], 2) for r in rows if r['p'] == pno and r['size'] > 9.5})
    diffs = [round(b - a, 3) for a, b in zip(oys, oys[1:]) if 5 < b - a < 40]
    c = collections.Counter(diffs)
    print(f'  p{pno}: 众数 {c.most_common(6)}')

json.dump(rows, open('a1_rows.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('\nsaved a1_rows.json')
