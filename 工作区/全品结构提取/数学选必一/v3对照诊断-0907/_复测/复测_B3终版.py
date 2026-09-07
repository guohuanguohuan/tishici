# -*- coding: utf-8 -*-
r"""B③ 终版对账：整块（题干+选项）抽取（允许空行）、导学↔源、导学↔测评、练习↔导学/测评。"""
import re, difflib, io, sys
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
    raise ValueError('unbalanced')
def split_groups(s, i):
    gs = []; ws = ' ' + NL + chr(13) + chr(9)
    while i < len(s) and s[i] in ws: i += 1
    try:
        while i < len(s) and s[i] == '{':
            g, i = next_group(s, i); gs.append(g)
            while i < len(s) and s[i] in ws: i += 1
    except ValueError:
        pass
    return gs, i
def norm(s):
    s = re.sub(R('@@overset@{[^}]*@}@{([^{}]*)@}'), R('@1'), s)
    for cmd in ('overrightarrow', 'emph', 'textbf', 'mathrm', 'mathbf', 'text', 'boldsymbol', 'textsubscript', 'fenzhi'):
        s = re.sub(R('@@' + cmd + '@{([^{}]*)@}'), R('@1'), s)
    s = re.sub(R('@@left|@@right|@!|@,|@;|@:|@@quad|@@qquad|@@kongbai|@@allowbreak|@@penalty10000|@@noindent|@@hfill|@@kylabel@{[^}]*@}|@@newline|~~~~|~'), '', s)
    s = re.sub(R('@@[a-zA-Z]+@?'), '', s)
    s = re.sub('[{}$' + BS + BS + ']', '', s)
    ok = r'[^0-9a-zA-Z' + chr(0x4e00) + '-' + chr(0x9fff) + chr(0x3000) + '-' + chr(0x303f) + chr(0xFF00) + '-' + chr(0xFFEF) + '=+*/^°√|，、；：．（）().-]'
    return re.sub(ok, '', s)
def ratio(a, b): return difflib.SequenceMatcher(None, a, b).ratio()
lx = rd(V4 + r'\导学件\body.tex'); sec = rd(V4 + r'\导学件\sec.tex')
p1 = rd(V4 + r'\练习件\body.tex'); cp = rd(V4 + r'\测评卷\main.tex')

# --- sec.tex 源题块（题干+选项） ---
heads = list(re.finditer(R('@@textbf@{(1@.1@.1@.[@.@d@-]+．（[^）]+）)}'), sec))
SRC = []
for k, m in enumerate(heads):
    end = heads[k+1].start() if k+1 < len(heads) else len(sec)
    c = sec[m.end():end]; cut = c.find('【')
    SRC.append((m.group(1), norm(c[:cut] if cut >= 0 else c)))
# --- 导学 例1/变式1 整块 ---
lines = lx.splitlines(); GX = []
for i, ln in enumerate(lines):
    if ln.startswith(BS + 'tjdnr'):
        gs, _ = split_groups(ln, ln.index('{'))
        if len(gs) >= 5 and gs[1].strip() == '例1':
            blk = gs[4]; k = i + 1
            while k < len(lines):
                t = lines[k].strip()
                if t == '': k += 1; continue
                if t.startswith(BS + 'bindopt'): blk += t; k += 1; continue
                break
            GX.append(('导学·例1·' + gs[0].split('｜')[0], norm(blk)))
vv = []
for i, ln in enumerate(lines):
    if ln.startswith(BS + 'li{') :
        gs, _ = split_groups(ln, ln.index('{'))
        if gs and gs[0].strip() == '变式1':
            vv.append(('导学·变式1·' + '一二三四五六七八九'[len(vv)], norm(gs[3])))
# --- 练习 整块（按条目块解析：jx/jxfig 参数跨行安全） ---
LX = []
ents = []
cur = None
for ln in p1.splitlines():
    t = ln.strip()
    if t.startswith(BS + 'jx'):
        if cur: ents.append(cur)
        cur = ln
    elif cur is not None and (t.startswith(BS + 'bindopt') or t == ''):
        cur += NL + ln
    else:
        if cur: ents.append(cur)
        cur = None
if cur: ents.append(cur)
for e in ents:
    head = e.strip().splitlines()[0]
    kind = 'jxfig' if head.startswith(BS + 'jxfig') else 'jx'
    gs, _ = split_groups(e, e.index('{'))
    want = 4 if kind == 'jxfig' else 3
    if len(gs) >= want:
        stem = gs[2] if kind == 'jxfig' else gs[2]
        LX.append(('练习·题' + gs[0], norm(stem)))
LX.sort(key=lambda x: int(re.sub(r'[^0-9]', '', x[0])))
# --- 测评 整块（timu 行→下一 timu/quku/daan 前） ---
cl = cp.splitlines(); CX = []; idx = [i for i, l in enumerate(cl) if l.strip().startswith(BS + 'timu')]
for n, i in enumerate(idx):
    j = i + 1
    while j < len(cl) and not (cl[j].strip().startswith(BS + 'timu') or cl[j].strip().startswith(BS + 'quku') or cl[j].strip().startswith(BS + 'daan') or cl[j].strip().startswith(BS + 'begin{multicols')):
        j += 1
    blk = NL.join(cl[i:j])
    num = re.sub(r'[^0-9]', '', cl[i].split('．')[0])
    CX.append(('测评·Q' + num, norm(blk)))
print(f'抽取：源 {len(SRC)} 导学例 {len(GX)} 导学变式 {len(vv)} 练习 {len(LX)} 测评 {len(CX)}')
def best(s):
    return max(SRC, key=lambda x: ratio(s, x[1]))
print()
print('== 导学例1/变式1 ↔ 源题（整块相似度） ==')
for t, s in GX + vv:
    b = best(s); r = ratio(s, b[1])
    print(f'  {t} ↔ {b[0]} {r:.2f}' + ('' if r >= 0.93 else '  ←'))
print()
print('== 导学例1 ↔ 测评Q（整块相似度，重复检测） ==')
pairs = 0
for t, s in GX:
    b = max(CX, key=lambda x: ratio(s, x[1])); r = ratio(s, b[1])
    if r >= 0.93: pairs += 1; print(f'  重复：{t} ↔ {b[0]} {r:.2f}')
print(f'导学例1↔测评 重复对：{pairs}/9')
print()
print('== 导学变式1 ↔ 练习/测评（整块） ==')
for t, s in vv:
    b1 = max(LX, key=lambda x: ratio(s, x[1])); r1 = ratio(s, b1[1])
    b2 = max(CX, key=lambda x: ratio(s, x[1])); r2 = ratio(s, b2[1])
    if r1 >= 0.93 or r2 >= 0.93:
        print(f'  重复：{t} ↔ {b1[0]}({r1:.2f}) / {b2[0]}({r2:.2f})')
print()
print('== 练习 ↔ 测评（整块） ==')
for t, s in LX:
    b = max(CX, key=lambda x: ratio(s, x[1])); r = ratio(s, b[1])
    if r >= 0.93: print(f'  重复：{t} ↔ {b[0]} {r:.2f}')
print()
print('== 练习题1 ↔ 导学变式1·七（整块全等?） ==')
a = [s for t, s in LX if t == '练习·题1'][0]
b = [s for t, s in vv if '七' in t][0]
print(f'  练习题1 == 导学变式七：{a == b}（len {len(a)}）；相似 {ratio(a, b):.2f}')
