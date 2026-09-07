# -*- coding: utf-8 -*-
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BS = chr(92); NL = chr(10)
def R(p): return p.replace('@', BS)
V4 = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4"
def rd(p): return open(p, encoding='utf-8', errors='ignore').read()
def next_group(s, i):
    depth = 0; j = i
    while j < len(s):
        c = s[j]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return s[i+1:j], j+1
        elif c == BS: j += 1
        j += 1
    raise ValueError
def split_groups(s, i):
    gs = []; ws = ' ' + NL + chr(13) + chr(9)
    while i < len(s) and s[i] in ws: i += 1
    try:
        while i < len(s) and s[i] == '{':
            g, i = next_group(s, i); gs.append(g)
            while i < len(s) and s[i] in ws: i += 1
    except ValueError: pass
    return gs, i
def norm(s):
    s = re.sub(R('@@overset@{[^}]*@}@{([^{}]*)@}'), R('@1'), s)
    for cmd in ('overrightarrow', 'emph', 'textbf', 'mathrm', 'textsubscript', 'fenzhi'):
        s = re.sub(R('@@' + cmd + '@{([^{}]*)@}'), R('@1'), s)
    s = re.sub(R('@@left|@@right|@!|@,|@;|@:|@@quad|@@kongbai|@@allowbreak|@@penalty10000|@@noindent|@@hfill|@@newline|~~~~|~'), '', s)
    s = re.sub(R('@@[a-zA-Z]+@?'), '', s)
    s = re.sub('[{}$' + BS + BS + ']', '', s)
    ok = r'[^0-9a-zA-Z' + chr(0x4e00) + '-' + chr(0x9fff) + chr(0x3000) + '-' + chr(0x303f) + chr(0xFF00) + '-' + chr(0xFFEF) + '=+*/^°√|，、；：．（）().-]'
    return re.sub(ok, '', s)
lx = rd(V4 + r'\导学件\body.tex'); sec = rd(V4 + r'\导学件\sec.tex'); cp = rd(V4 + r'\测评卷\main.tex')
# 源题 stem：header 后到第一个空行的首段
heads = list(re.finditer(R('@@textbf@{(1@.1@.1@.[@.@d@-]+．（[^）]+）)}'), sec))
SRC = {}
for k, m in enumerate(heads):
    rest = sec[m.end():]
    para = rest.split(NL + NL)[0]
    SRC[m.group(1)[:9]] = norm(para)
# 导学 例1 stem
GX = {}
for ln in lx.splitlines():
    if ln.startswith(BS + 'tjdnr'):
        gs, _ = split_groups(ln, ln.index('{'))
        if len(gs) >= 5 and gs[1].strip() == '例1':
            GX[gs[0].split('｜')[0]] = norm(gs[4])
# 测评 stem
CX = {}
for ln in cp.splitlines():
    t = ln.strip()
    if t.startswith(BS + 'timu') and 'newcommand' not in t:
        gs, _ = split_groups(t, t.index('{'))
        if len(gs) >= 5:
            CX['Q' + re.sub(r'[^0-9]', '', gs[0].split('．')[0])] = norm(gs[4])
print('源题 stem 字数:', {k: len(v) for k, v in SRC.items()})
print()
print('== stem 精确全等（归一化） ==')
for name in ['一', '二', '三', '四', '五', '六', '七', '八', '九']:
    s = GX[name]
    hit = [k for k, v in SRC.items() if v == s and len(s) > 20]
    print(f'  导学例1·{name} (stem {len(s)} 字) == 源 {hit if hit else "无精确匹配"}')
for q, s in CX.items():
    hit = [k for k, v in SRC.items() if v == s and len(s) > 20]
    gx = [n for n in GX if GX[n] == s and len(s) > 20]
    print(f'  测评{q} (stem {len(s)} 字) == 源 {hit if hit else "无"} ；== 导学例1·{gx if gx else "无"}')
