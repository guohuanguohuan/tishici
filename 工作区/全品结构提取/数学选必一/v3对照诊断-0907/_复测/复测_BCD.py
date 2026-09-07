# -*- coding: utf-8 -*-
r"""v4 复测 B/C/D（独立复测代理，只读）。@@=正则双反斜杠，@=单反斜杠占位。"""
import re, difflib, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BS = chr(92); NL = chr(10)
def R(p): return p.replace('@', BS)
V4 = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4"
V3 = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v3"
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
    return None, i
def split_groups(s, i):
    gs = []
    ws = ' ' + NL + chr(13) + chr(9)
    while i < len(s) and s[i] in ws: i += 1
    while i < len(s) and s[i] == '{':
        g, i = next_group(s, i); gs.append(g)
        while i < len(s) and s[i] in ws: i += 1
    return gs, i
def calls(src, cmd):
    out = []
    for m in re.finditer(re.escape(BS + cmd) + R('(?![a-zA-Z])'), src):
        gs, _ = split_groups(src, m.end())
        out.append(gs)
    return out
def norm(s):
    s = re.sub(R('@@overset@{[^}]*@}@{([^{}]*)@}'), R('@1'), s)
    for cmd in ('overrightarrow', 'emph', 'textbf', 'mathrm', 'mathbf', 'text', 'boldsymbol', 'textsubscript', 'fenzhi'):
        s = re.sub(R('@@' + cmd + '@{([^{}]*)@}'), R('@1'), s)
    s = re.sub(R('@@left|@@right|@!|@,|@;|@:|@@quad|@@qquad|@@kongbai|@@allowbreak|@@penalty10000|@@noindent|@@hfill|@@kylabel@{[^}]*@}|~~~~|~'), '', s)
    s = re.sub(R('@@[a-zA-Z]+@?'), '', s)
    s = re.sub('[{}$' + BS + BS + ']', '', s)
    ok = r'[^0-9a-zA-Z' + chr(0x4e00) + '-' + chr(0x9fff) + chr(0x3000) + '-' + chr(0x303f) + chr(0xFF00) + '-' + chr(0xFFEF) + '=+*/^°√|，、；：．（）().-]'
    return re.sub(ok, '', s)
def ratio(a, b): return difflib.SequenceMatcher(None, a, b).ratio()

lx  = rd(V4 + r'\导学件\body.tex')
sec = rd(V4 + r'\导学件\sec.tex')
p1  = rd(V4 + r'\练习件\body.tex')
at  = rd(V4 + r'\练习件\answers.tex')
cp  = rd(V4 + r'\测评卷\main.tex')

print('===== B③-1 导学件：sec.tex 源题 10 道 → 在场性 =====')
heads = list(re.finditer(R('@@textbf@{(1@.1@.1@.[@.@d@-]+．（[^）]+）)}'), sec))
print('源题头数:', len(heads))
nbody = norm(lx)
ok_all = True
for k, m in enumerate(heads):
    end = heads[k+1].start() if k+1 < len(heads) else len(sec)
    chunk = sec[m.end():end]
    cut = chunk.find('【')
    if cut >= 0: chunk = chunk[:cut]
    nc = norm(chunk)
    hit = nc in nbody
    ok_all &= hit
    print(f'  {m.group(1)}: 归一 {len(nc)} 字 → 包含于导学body={hit}')
print('源题10全在场（题干+选项包含口径）:', ok_all)

print()
print('===== B③-2 三册题干抽取与两两查重 =====')
tj = calls(lx, 'tjdnr')
vv = [g for g in calls(lx, 'li') if g[0].strip() == '变式1']
cn = '一二三四五六七八九'
d_g = [['导学·例1·' + g[0].split('｜')[0], g[4]] for g in tj if len(g) >= 5 and g[1].strip() == '例1']
d_g += [['导学·变式1·' + cn[i], g[3]] for i, g in enumerate(vv)]
d_l = [['练习·题' + g[0], g[2]] for g in calls(p1, 'jx') + calls(p1, 'jxfig')]
d_c = []
for g in calls(cp, 'timu'):
    if len(g) >= 5:
        num = re.sub(r'[^0-9]', '', g[0].split('．')[0])
        d_c.append(['测评·Q' + num, g[4]])
print(f'抽取：导学 例1×{len(tj and [1 for g in tj if len(g)>=5 and g[1].strip()=="例1"])}＋变式×{len(vv)}（应9+9）；练习 {len(d_l)}（应11）；测评 {len(d_c)}（应10）')
G = [(t, norm(s)) for t, s in d_g]; L = [(t, norm(s)) for t, s in d_l]; C = [(t, norm(s)) for t, s in d_c]
dup = []
for i in range(len(G)):
    for other in (L, C):
        for t2, s2 in other:
            if G[i][1] and G[i][1] == s2: dup.append((G[i][0], t2, '全等'))
            elif G[i][1] and len(G[i][1]) > 24 and ratio(G[i][1], s2) >= 0.97:
                dup.append((G[i][0], t2, f'相似{ratio(G[i][1], s2):.2f}'))
for i in range(len(L)):
    for t2, s2 in C:
        if L[i][1] and L[i][1] == s2: dup.append((L[i][0], t2, '全等'))
        elif L[i][1] and len(L[i][1]) > 24 and ratio(L[i][1], s2) >= 0.97:
            dup.append((L[i][0], t2, f'相似{ratio(L[i][1], s2):.2f}'))
print(f'跨册重复对 {len(dup)} 对：')
for a, b, how in dup: print(f'  {a} ↔ {b}（{how}）')

print()
print('===== B③-3 导学例1/变式 ↔ 源题 对应（相似度） =====')
srcs = []
for k, m in enumerate(heads):
    end = heads[k+1].start() if k+1 < len(heads) else len(sec)
    c = sec[m.end():end]; cut = c.find('【')
    if cut >= 0: c = c[:cut]
    srcs.append((m.group(1), norm(c)))
for t, s in G:
    best = max(srcs, key=lambda x: ratio(s, x[1]))
    r = ratio(s, best[1])
    print(f'  {t} ↔ {best[0]} 相似度 {r:.2f}' + ('' if r >= 0.93 else '  ← 低相似'))

print()
print('===== B① 知识点N 对位 =====')
zsd = calls(lx, 'zsd')
print('导学件知识点块:', [(g[0], g[1]) for g in zsd])
kmap = {'一': 1, '二': 2, '三': 3}
gset = sorted(kmap[g[0]] for g in zsd if g[0] in kmap)
tagstr = ' '.join(g[1] for g in calls(p1, 'jx') + calls(p1, 'jxfig'))
tags_l = re.findall(R('（知识点(@d)）'), tagstr)
tags_c = [g[3] for g in calls(cp, 'timu') if len(g) >= 5]
print('练习题侧号:', tags_l, '；测评题侧号:', tags_c, '；导学块号:', gset)
print('练习⊆导学:', set(map(int, tags_l)) <= set(gset), '；测评⊆导学:', set(map(int, tags_c)) <= set(gset))
gx = {}
for g in tj:
    if len(g) >= 5 and g[1].strip() == '例1':
        pass
tmap = {}
srcmap = {}
for t, s in G:
    for k, m in enumerate(heads):
        pass
print('（同题异册标签同号核对见 B③-2 重复对：全等对两侧知识点号逐对人工核对于报告）')

print()
print('===== B② 探究点↔源题型通式 映射守恒 =====')
tongshi = re.findall('题型通式：(.*?)' + NL + NL, sec, re.S)
xiaojie = [g[0] for g in calls(lx, 'xiaojie')]
print(f'源通式 {len(tongshi)} / v4 小结 {len(xiaojie)}')
for i, (t, x) in enumerate(zip(tongshi, xiaojie), 1):
    print(f'  组{i}: 小结↔通式 相似度 {ratio(norm(t), norm(x)):.2f}')

print()
print('===== B④ 答案在场性 =====')
print(f'导学：变式1×{len(vv)}（应9）；ansline×{lx.count(R("@ansline{"))}（应14）')
lines = lx.splitlines(); miss = []
for i, ln in enumerate(lines):
    if ln.startswith(R('@li{变式1')) or ln.startswith(R('@jiancestem')) or ln.startswith(R('@jiance{')):
        if R('@ansline') not in NL.join(lines[i:i+15]): miss.append(i+1)
print('导学：变式/检测 15 行窗口内缺 ansline：', miss if miss else '无（逐题紧跟）')
qnos = [int(g[0]) for g in calls(p1, 'jx') + calls(p1, 'jxfig')]
anos = [int(g[0]) for g in calls(at, 'jans')]
print(f'练习源层：题号 {qnos} ↔ 答案号 {anos} → 一一对应 {qnos == anos == list(range(1, 12))}')
import pymupdf
dl = pymupdf.open(V4 + r'\练习件\main.pdf')
t1 = dl[0].get_text(); t2 = dl[1].get_text()
pq = sorted(set(int(x) for x in re.findall(R('(?m)^(@d+)．'), t1)))
pa = sorted(set(int(x) for x in re.findall(R('(?m)^(@d+)．'), t2)))
print(f'练习 PDF 层：p1 题号 {pq}；p2 答案条目 {pa} → 对位 {pq == pa == list(range(1, 12))}')

print()
print('===== B⑤ ★标与典型性理由 =====')
gstar = calls(lx, 'starblk')
print(f'导学 starblk×{len(gstar)}（应3）：')
for g in gstar: print('   ·', g[0][:36], '…')
print('练习 body ★×' + str(p1.count('★')) + '（应2=题9/题11）；理由载体＝练习 postproc log 5c（2 条台账，前查在场）')
print('测评 timu ★实参：', [repr(g[2]) for g in calls(cp, 'timu') if len(g) >= 5], '；理由载体＝测评 交付报告 §四-11 表（3 行，前查在场）')

print()
print('===== B⑥ 悬空引用扫描 =====')
allt = NL.join([lx, p1, at, cp])
for pat, name in [(R('见例@d+'), '见例N'), ('如下例', '如下例'), (R('见探究点'), '见探究点'),
                  (R('衔接@d*'), '衔接N'), (R('见条目@d+'), '见条目N'), (R('条目@d+'), '条目N'),
                  (R('如图[①②③④⑤@d]*'), '如图'), (R('见图@d*'), '见图'),
                  ('见下表|如下表|见上表|上表', '表引用')]:
    hits = re.findall(pat, allt)
    if hits: print(f'  {name}: {sorted(set(hits))} ×{len(hits)}')
tms = sorted(set(int(g[0]) for g in calls(lx, 'tiaomu')), key=int)
print('  导学条目号在场:', tms, '；引用 条目10/16/17/33/34/38 → 成件无（v3 同源编注同文在案）')

print()
print('===== B⑦ 难度档格式 =====')
fmts = set()
for g in tj:
    if len(g) >= 5 and g[1].strip() == '例1': fmts.add('导学例侧:' + g[2])
for g in vv: fmts.add('导学变式侧:' + g[1])
for m in re.finditer(R('〔(简单|中档|困难)（知识点[一二三@d]）〕'), lx): fmts.add('导学检测侧:〔' + m.group(1) + '…〕')
for g in calls(p1, 'jx') + calls(p1, 'jxfig'): fmts.add('练习:' + g[1])
for g in calls(cp, 'timu'):
    if len(g) >= 5: fmts.add('测评:难度=' + g[1] + ' 知识点=' + g[3] + ' ★=' + ('有' if g[2].strip() else '无'))
for f in sorted(fmts): print('  ', f)
vals = set(re.findall('简单|中档|困难|容易|较难', allt))
print('  档位值全集:', vals, '；禁用变体命中:', vals & {'容易', '较难'})

print()
print('===== B⑧ 超纲关键词扫描 =====')
for pat in ['基本定理', '空间直角', '坐标', '基底', '法向量', '线面角', '点面距', '点到平面', '1.1.2', '1.1.3']:
    for fn, t in (('导学body', lx), ('练习body', p1), ('练习answers', at), ('测评正文', cp.split(R('@begin{document}'))[1])):
        for m in re.finditer(pat, t):
            ctx = t[max(0, m.start()-30):m.end()+30].replace(NL, ' ')
            print(f'  [{fn}] «{pat}» …{ctx}…')

print()
print('===== C 分号计数（「；」） =====')
def cnt(s): return s.count('；')
sec3 = rd(V3 + r'\导学件\sec.tex'); lb3 = rd(V3 + r'\导学件\body.tex')
lb3p = rd(V3 + r'\练习件\body.tex'); la3 = rd(V3 + r'\练习件\answers.tex')
c3 = rd(V3 + r'\测评卷\main.tex')
c3b = c3.split(R('@begin{document}'))[1]; c4b = cp.split(R('@begin{document}'))[1]
print(f'导学：sec(源节) v3={cnt(sec3)} v4={cnt(sec)}；body v3={cnt(lb3)} v4={cnt(lx)}')
print(f'练习：body v3={cnt(lb3p)} v4={cnt(p1)}；answers v3={cnt(la3)} v4={cnt(at)}；合计 v3={cnt(lb3p)+cnt(la3)} v4={cnt(p1)+cnt(at)}')
print(f'测评：正文 v3={cnt(c3b)} v4={cnt(c4b)}；文件级 v3={cnt(c3)} v4={cnt(cp)}')

print()
print('===== D v3 测评卷 卷头评分说明 =====')
d3 = pymupdf.open(V3 + r'\测评卷\main.pdf')
t31 = d3[0].get_text()
print('v3 p1 含「考生注意」:', '考生注意' in t31, '；含「答题纸」:', '答题纸' in t31, '；含「无效」:', '无效' in t31)
print('v3 p1 前 10 行:', ' | '.join(t31.splitlines()[:10]))
d4 = pymupdf.open(V4 + r'\测评卷\main.pdf')
print('v4 p1 含「考生注意」:', '考生注意' in d4[0].get_text())

print()
print('===== B③-1b 精化：导学 例1（题干+选项整块） ↔ 源题 题干+选项 =====')
lines = lx.splitlines()
res = []
for i, ln in enumerate(lines):
    if ln.startswith(BS + 'tjdnr'):
        gs, _ = split_groups(ln, ln.index('{'))
        if len(gs) >= 5 and gs[1].strip() == '例1':
            block = gs[4]; k = i + 1
            while k < len(lines) and lines[k].startswith(BS + 'bindopt'):
                block += lines[k]; k += 1
            res.append((gs[0].split('｜')[0], norm(block)))
for name, blk in res:
    best = max(srcs, key=lambda x: ratio(blk, x[1]))
    r = ratio(blk, best[1])
    print(f'  例1·{name}: ↔ {best[0]} 相似度 {r:.2f}' + ('' if r >= 0.93 else '  ← 低'))
