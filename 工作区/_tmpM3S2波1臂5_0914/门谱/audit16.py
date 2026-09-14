# -*- coding: utf-8 -*-
"""audit16.py — 课时16 main.tex 静态审计＋估高判模读数（波1臂5 过程件）。零写入 main.tex。"""
import io, json, math, re, sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时16-2.7.2抛物线性质'
src = open(PIECE + '/main.tex', encoding='utf-8').read()

ctrl = [c for c in src if ord(c) < 0x20 and c not in '\n\t\r']
print('控制符:', len(ctrl))

absorb = re.findall(r'\\[a-zA-Z]+[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', src)
print('控制词吸CJK:', len(absorb), absorb[:5])

anchors = re.findall(r'^[ \t]*%[ \t]*ans:(\S+)', src, re.M)
blocks = re.findall(r'\\begin\{ansblock\}\[([^\]]+)\]', src)
nums = [int(n) for n in re.findall(r'\\ansitem\{(\d+)\}\{', src)]
notes = re.findall(r'\\ansnote\{详解\}\{', src)
print('锚:', len(anchors), '块:', len(blocks), 'ansitem:', len(nums), '详解行:', len(notes))
print('锚≡块:', anchors == blocks, '序号连号1..50:', nums == list(range(1, 51)))

BAD = ['\\newpage', '\\clearpage', '\\pagebreak', '\\vbox', '\\vtop', '\\ketangboxed', '\\columnbreak', '\\eject']
body = '\n'.join(l.split('%', 1)[0] if not l.lstrip().startswith('%') else '' for l in src.split('\n'))
print('回流禁词:', {w: body.count(w) for w in BAD if body.count(w)})

# 花括号平衡解析 ansitem/ansnote
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
    raise ValueError('花括号不配平 @' + str(i))

# 逐块抓 值＋详解 估高
lines = src.split('\n')
cur, vals, note_vals, ruled, order = None, {}, {}, set(), []
pending = False
for ln in lines:
    ls = ln.strip()
    if ls.startswith('%'):
        continue
    if '{\\ansblockgrayfalse' in ls.replace(' ', ''):
        pending = True
        continue
    mb = re.match(r'\\begin\{ansblock\}\[([^\]]+)\]', ls)
    if mb:
        cur = mb.group(1)
        order.append(cur)
        if pending:
            ruled.add(cur)
        pending = False
        continue
    ma = re.search(r'\\ansitem\{(\d+)\}\{', ls)
    if ma and cur:
        b, _ = braces(ls, ma.end() - 1)
        vals[cur] = b
    mn = re.search(r'\\ansnote\{详解\}\{', ls)
    if mn and cur:
        b, _ = braces(ls, mn.end() - 1)
        note_vals[cur] = b

def wlen(s):
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    return sum(0.5 if ord(c) < 128 else 1.0 for c in s)

est = {}
for k in order:
    est[k] = math.ceil(wlen(vals.get(k, '') + note_vals.get(k, '')) / 23)
    print(f"{'括线' if k in ruled else '灰底'} est={est[k]:>3}  {k}")
need = {k for k in order if est[k] > 8}
cur_wrapped = {k for k in order if k in ruled}
print()
print('est>8 应括线集:', len(need), '键')
print('现括线集:', len(cur_wrapped), '键')
print('缺包:', sorted(need - cur_wrapped))
print('多包:', sorted(cur_wrapped - need))
flat = sorted(need, key=lambda k: -est[k])
print('应括线明细:', [(k.rsplit('-', 1)[-1], est[k]) for k in flat])
gray_max = max((est[k] for k in order if k not in need), default=0)
ruled_min = min((est[k] for k in need), default=99)
print(f'灰底最大est={gray_max}（须≤8） 括线最小est={ruled_min}（须≥9）')
