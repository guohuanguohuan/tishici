# -*- coding: utf-8 -*-
r"""v3 练习件后处理器：sec.tex（pandoc 原始输出）→ body.tex（题区）＋ answers.tex（答案与解析区）
＋ chapterhead.tex ＋ postproc_lianxi_log.txt。
高仿目标：全品练习册 p06/p21（已亲看）。结构：章首通栏（章22/节18/小节15/课时14）→ 题区双栏
（花形组行「夯基达标／提能进阶」＋流水号 1．2．3．4．＋6.5pt 灰括注〔源 1.1.1.5-4·简单〕，题面无答案，
题号列恒空 hang 7mm，选项/①链 2em 缩进绑定）→ \clearpage →「答案与解析」通栏标题 → 双栏密集排
（9.5pt/14.5pt，流水号＋【答案】下划线＋【分析】【详解】【点睛】verbatim 连排）。
池子分配（10 题守恒，与导学件互补）：夯基达标＝题4（简单）；提能进阶＝题6/9/10（中档）；
组名「夯基达标／提能进阶」自拟不抄全品。图分档：题6/9/10 立体图 30mm（题4 无图）。
题侧知识点对位标签：6.5pt #777777 灰字「（知识点N）」落题干首行右缘（返工项拍板15，同测评卷口径，答案页不加）。"""
import re

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v3\练习件"
LOG = []
log = LOG.append

tex = open(BASE + r"\sec.tex", encoding='utf-8').read()

# ---- 1. 源清洗（同 v2/导学件）：U+2060、箭头归一化、长下划线挖空 ----
tex = tex.replace('\u2060', '')
tex = tex.replace(r'\overset{⃑}{', r'\overrightarrow{')
n_kong = len(re.findall(r'(?:\\_){4,}', tex))
tex = re.sub(r'(?:\\_){4,}', r'\\kongbai{}', tex)
log(f'1. 源清洗：去 U+2060、\\overset{{⃑}}{{}}→\\overrightarrow{{}}；长下划线→\\kongbai{{}} ×{n_kong}（题面原有空保留）')

blocks = [b.strip() for b in re.split(r'\n\s*\n', tex) if b.strip()]

# ---- 2. 解析（同导学件：讲部条目＋题部组/题；题块路由先于讲部吸收） ----
RE_ENTRY = re.compile(r'^1\.1\.1-(\d)．〔基〕')
RE_GRP = re.compile(r'^\\textbf\{(1\.1\.1\.(\d+) [^}]*)\}$')
RE_TI = re.compile(r'^\\textbf\{(1\.1\.1\.(\d+)-(\d+)．（(简单|中档|难)）)\}(.*)$', re.S)

entries, tis, grp_order = {}, {}, []
cur_entry = cur_grp = cur_ti = None
for b in blocks:
    m = RE_GRP.match(b)
    if m:
        cur_grp = m.group(1)
        cur_ti = None
        if m.group(2) != '1':
            grp_order.append(cur_grp)
        continue
    m = RE_ENTRY.match(b)
    if m:
        cur_entry = int(m.group(1))
        entries[cur_entry] = {'title': b, 'note': None, 'blocks': [], 'tables': 0}
        continue
    m = RE_TI.match(b)
    if m:
        key = (int(m.group(2)), int(m.group(3)))
        cur_ti = key
        tis[key] = {'num': f'1.1.1.{key[0]}-{key[1]}', 'nanidu': m.group(4),
                    'stem': [m.group(5).replace('\n', ' ').strip()] if m.group(5).strip() else [],
                    'ans': '', 'zsd': '', 'fenxi': [], 'xiangjie': [], 'dj': []}
        continue
    if cur_entry is not None and not tis:
        if b.startswith('【编注】') and entries[cur_entry]['note'] is None:
            entries[cur_entry]['note'] = b[len('【编注】'):].strip()
        elif b.startswith('【微提醒】'):
            entries[cur_entry]['blocks'].append(b)
        elif '\\begin{tabular}' in b or '\\begin{longtable}' in b:
            entries[cur_entry]['tables'] += 1
        else:
            entries[cur_entry]['blocks'].append(b)
        continue
    if cur_ti:
        d = tis[cur_ti]
        if b.startswith('【答案】'):
            d['ans'] = b[len('【答案】'):].strip() or 'NEXT'
        elif b.startswith('【知识点】'):
            d['zsd'] = b[len('【知识点】'):].strip() or 'NEXT'
        elif b.startswith('【分析】'):
            d['fenxi'] = [b] if len(b) > len('【分析】') else []
        elif b.startswith('【详解】'):
            d['xiangjie'] = [b]
        elif b.startswith('【点睛】'):
            d['dj'] = [b]
        elif d['ans'] == 'NEXT':
            d['ans'] = b.replace('\n', ' ')
        elif d['zsd'] == 'NEXT':
            d['zsd'] = b.replace('\n', ' ')
        elif d['fenxi'] and not d['xiangjie']:
            d['fenxi'].append(b)
        elif d['xiangjie']:
            d['xiangjie'].append(b)
        else:
            d['stem'].append(b.replace('\n', ' '))
for k, d in tis.items():
    assert d['ans'] and d['ans'] != 'NEXT', f'{d["num"]} 答案缺失'
log('2. 解析：题部组 9 组、题 10 道；讲部条目 9 个（练习件不排讲部）')

# ---- 3. 图分档（立体线框 30mm）＋独立图 7mm 起排 wrapper（同导学件） ----
FIG = {'sub3_B_4.png': '45mm', 'image1.png': '30mm', 'image2.png': '30mm',
       'image3.png': '30mm', 'image4.png': '30mm', 'image5.png': '30mm'}
FIGRE = re.compile(r'\\includegraphics\[(width=[\d.]+in,height=[\d.]+in)(,alt=\{[^}]*\})?\]\{([^}]+)\}')
figs_seen = []

def reflow(blocks_in, tag, out):
    for b in blocks_in:
        if '\\begin{tabular}' in b or not FIGRE.search(b):
            out.append(b)
            continue
        last = 0
        for mm in FIGRE.finditer(b):
            if b[last:mm.start()].strip():
                out.append(b[last:mm.start()].strip())
            name = mm.group(3).split('/')[-1]
            w = FIG.get(name)
            assert w, f'{tag}: {name} 未分档'
            figs_seen.append((name, w, tag))
            tok = mm.group(0).replace(mm.group(1), 'width=' + w)
            out.append(r'\penalty10000\hangindent=0pt\hangafter=1\noindent\hspace*{7mm}'
                       r'\makebox[\dimexpr\linewidth-7mm\relax][c]{' + tok + r'}\par\penalty10000')
            last = mm.end()
        if b[last:].strip():
            out.append(b[last:].strip())
    return out

def emit_blocks(bs, out):
    """续块分类：选项/①链 → 2em 缩进绑定（对齐练习册 p06）；其余段前绑定。"""
    for s in bs:
        if s.startswith(('A．', 'B．', 'C．', 'D．', '①')):
            out.append(r'\bindopt ' + s)
        else:
            out.append(r'\bindp ' + s)

# ---- 4. 组装题区 body.tex ----
body = []
em = body.append
em(r'\huaxing{夯基达标}{基础巩固\quad 稳拿保分}')
log('4a. 花形组行「夯基达标」＝白底黑边圆角字块＋深灰底线＋右侧灰小字；组名自拟（不抄全品），小字自拟')

POOL_JICHU = [(5, 4)]
POOL_TINENG = [(7, 6), (9, 9), (10, 10)]

# ---- 题侧知识点对位标签（返工项拍板15，同测评卷口径）----
# 知识点1＝空间向量的概念、2＝线性运算、3＝夹角/数量积/共面（v2 实验报告 64 行三块映射，测评卷逐题核对一致）；
# 逐题核对：题1 共面充要条件（条目9）→3、题2 数量积求夹角→3、题3 数量积求距离→3、题4 折叠数量积求距离→3。
# 截断点逐题实测：首行＝流水号＋灰括注＋前缀＋标签须容于栏宽——题2 在数学边界前、题3 在「45°」后
# （首个「中，」前缀过长首行容不下）、题4 在首个「中，」；题1 短题干标签尾随。编译后以 pymupdf 实测落位复核。
KY = {(5, 4): (3, None), (7, 6): (3, r'如图，在正方体'),
      (9, 9): (3, r'如图，在大小为45°'), (10, 10): (3, r'已知矩形\(ABCD\)中，')}

def ky_stem(key, stem):
    n, cut = KY[key]
    lab = r'\hfill\kylabel{（知识点' + str(n) + '）}'
    if cut is None:                       # 短题干：标签尾随行末
        assert len(stem) < 20, f'{key} 短题干假设失效：{stem}'
        return stem + lab
    assert stem.startswith(cut), f'{key} 截断前缀与题干不符：{cut}'
    return stem[:len(cut)] + lab + r'\\' + stem[len(cut):]
seq = 0
for gnum, k in POOL_JICHU:
    d = tis[(gnum, k)]
    seq += 1
    em(r'\jx{' + str(seq) + '}{源 ' + d['num'] + '·' + d['nanidu'] + '}{' + ky_stem((gnum, k), d['stem'][0]) + '}')
    tmp = []
    reflow(d['stem'][1:], f'题{seq}', tmp)
    emit_blocks(tmp, body)
    log(f'4b. 夯基达标 题{seq}＝{d["num"]}（{d["nanidu"]}），题面无答案；灰括注〔源 {d["num"]}·{d["nanidu"]}〕')

em(r'\huaxing{提能进阶}{综合应用\quad 进阶提分}')
log('4c. 花形组行「提能进阶」＝同款花形行；组名与小字自拟（登记）')
for gnum, k in POOL_TINENG:
    d = tis[(gnum, k)]
    seq += 1
    em(r'\jx{' + str(seq) + '}{源 ' + d['num'] + '·' + d['nanidu'] + '}{' + ky_stem((gnum, k), d['stem'][0]) + '}')
    tmp = []
    reflow(d['stem'][1:], f'题{seq}', tmp)
    emit_blocks(tmp, body)
    log(f'4d. 提能进阶 题{seq}＝{d["num"]}（{d["nanidu"]}），题面无答案')

log('4e. 题侧知识点对位标签 ×4（返工项拍板15，同测评卷口径）：\\kylabel＝6.5pt/8pt #777777 灰字「（知识点N）」，'
    '\\hfill 弹性胶恒落题干首行右缘——题1 短题干尾随，题2/3/4 长题干在逗号/数学边界截首行（截断点逐题实测见 KY 表注）；'
    '标签为行内右缘元素不进 7mm 题号悬挂窄列，答案页不加；'
    '归属＝知识点3（夹角/数量积/共面，v2 实验报告 64 行三块映射），四题逐题核对无改判')

# ---- 5. 组装答案区 answers.tex（9.5pt/14.5pt 密集连排，由 main 外层设定字号） ----
answers = []
seq = 0
for gnum, k in POOL_JICHU + POOL_TINENG:
    d = tis[(gnum, k)]
    seq += 1
    answers.append(r'\jans{' + str(seq) + r'}{\ansul{' + d['ans'] + '}}')
    tmp = []
    n_fx = len(d['fenxi'])
    n_xj = len(d['xiangjie'])
    n_dj = len(d['dj'])
    for tag, blks in (('【分析】', d['fenxi']), ('【详解】', d['xiangjie']), ('【点睛】', d['dj'])):
        if blks:
            first = blks[0]
            for tg in ('【分析】', '【详解】', '【点睛】'):
                if first.startswith(tg):   # 源块自带标签，剥去防双排
                    first = first[len(tg):].strip()
            rest = ' '.join(blks[1:])
            tmp.append(tag + first + ((' ' + rest) if rest else ''))
    # 解析文本过 reflow：题源里嵌在【详解】的图（如题10 折叠图）统一 30mm 独立块排入答案区
    reflow(tmp, f'答{seq}', answers)
    log(f'5. 答案区 题{seq}＝{d["num"]}：【答案】下划线＋【分析】{n_fx}块＋【详解】{n_xj}块'
        f'＋【点睛】{n_dj}块 verbatim 连排（嵌图随解析入答案区）')

# ---- 6. 巨型公式断点（同 v2 11b）＋输出 ----
log('4. 图独立成块（7mm 起排，题区＋答案区）：' +
    ('；'.join(f'{n}→{w}({k})' for n, w, k in figs_seen) if figs_seen else '无'))
# 题区：块间空行分段；答案区：单换行连排（\jans 起段，【分析】【详解】【点睛】接排同段，图块自带 \par 断段）
text = '\n\n'.join(body)
n_ab = text.count(' = \\left') + text.count(' \\cdot \\left')
text = text.replace(' = \\left', ' = \\allowbreak\\left')
text = text.replace(' \\cdot \\left', ' \\cdot \\allowbreak\\left')
log(f'6. body.tex：巨型行内公式显式断点注入 \\allowbreak ×{n_ab}（同 v2 11b）')
open(BASE + r'\body.tex', 'w', encoding='utf-8').write(text + '\n')
text = '\n'.join(answers)
n_ab = text.count(' = \\left') + text.count(' \\cdot \\left')
text = text.replace(' = \\left', ' = \\allowbreak\\left')
text = text.replace(' \\cdot \\left', ' \\cdot \\allowbreak\\left')
log(f'6. answers.tex：巨型行内公式显式断点注入 \\allowbreak ×{n_ab}（同 v2 11b）')
open(BASE + r'\answers.tex', 'w', encoding='utf-8').write(text + '\n')

head = [
    r'\zhangtitle{第1章 空间向量与立体几何}',
    r'\jietitle{1.1 空间向量及其运算}',
    r'\xiaojietitle{1.1.1 空间向量及其运算}',
    r'\keshi{第1课时\quad 空间向量及其运算}',
]
open(BASE + r'\chapterhead.tex', 'w', encoding='utf-8').write('\n'.join(head) + '\n')
log('7. 章首通栏 4 层同导学件；题区/答案区之间 \\clearpage 由 main.tex 承担（multicols 外）')
open(BASE + r'\postproc_lianxi_log.txt', 'w', encoding='utf-8').write('\n'.join(LOG))
print('\n'.join(LOG))
