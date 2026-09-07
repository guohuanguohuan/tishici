# -*- coding: utf-8 -*-
r"""v4.2 导学件后处理器：sec.tex（pandoc 原始输出）→ chapterhead.tex + body.tex + postproc_daoxue_log.txt。
v4.2 对齐全品轮（22 条改版指令，逐条登记交付报告§九；口径＝与全品原书完全一致）：
A 类：撤页眉（翻拍板8②回归原旨）、四级标题仿粗黑 \heibf、栏间竖线恢复（翻拍板28，black!25＝拍板39 派生档）、
页脚小字黑粗、课时名内容式（第1课时 空间向量的概念及线性运算）、题干图 minipage 并排（图 30mm 档提档至≈34mm）
＋详解图 40mm、花形微调、编注/解析 8pt 黑、题侧 8pt；C 类：条目（1）（2）各自成段、素养小结①②③各自成段、
【诊断分析】单行化、表格列宽内容驱动、选项 4 项/行扩域；D 类：变式/检测补【解析】简析 ×15（逐题亲算）；
E 类：撤★精选标（翻拍板25 导学件部分）；F 类：\kongda 印答盒 \kern0.15em 防粘连；G 类：条目号/检测题号加粗。
v4.1 用户过目轮（依据＝用户以全品原书 p04/p05/p06 提出的 11 条改版指令，逐条登记交付报告§八）：
知识点区挖空印答（\kongda，原词下划线印出，仅例题/变式/检测题干保留 \kongbai）、判断题加第 4 参【解析】＋
全品式（1）（2）序号、花形行栏内化（撤 multicols 切分，单一 multicols，花形为栏内首元素，菱形标＋栏宽灰线）、
条目号按知识点重起（知识点一 1～3／二 1～2／三 1～4，投影向量入号）、章名「第一章」。
结构：章首通栏（章22 左对齐/节18/小节15/课时14＋章首错位灰方块）→【学习目标】×3（楷体化压缩，通栏区）
→ \begin{multicols}{2} → 花形行「课前预习」（栏内首元素）→ ◆知识点×3（条目挖空印答＋编注段末并排＋三列挖空表；每知识点后紧跟【诊断分析】判断块×2 题）
→ 花形行「课中探究」（栏内）→ ◆探究点×9（恒式＝例1＋变式1＋素养小结；◆标题与例1 同段内联）
→ 花形行「课堂评价」（栏内）→ 检测×5（3 单选＋2 填空带提示词）→ \end{multicols}。一切题题后紧跟答案（拍板12）。
题侧＝〔难度（知识点N）〕（拍板15/18，撤〔源〕括注）。
题源分配（拍板16 源题优先）：例1×9＝各组第 1 题（题1～7、9、10）；变式1：探究点七＝源题8（池尽前优先池配），
其余 8 点按变式六策命制（逐题亲算，策名逐条登记）；源题 10 题全在场（题量守恒）。
命制登记：v4 轮新命制 14（变式8＋检测4＋诊断2）≤上限 15；沿用 v3 已亲算 5（检测1＋诊断4），逐条登记；
v4.1 轮新增＝判断解析 6 句（逐题亲算复核）＋挖空答案印出（原词来自源/条目文意，逐个核对）；
v4.2 轮新增＝变式解析 9＋检测解析 5（逐题亲算文字转写，D 类16/17）。
模板 8 条坑（v3 交付报告§七）全程规避：\kongbai{} 空组隔离／hangafter 数字后留界／raw 反斜杠纪律／
\underline 只包值／图块段 hangindent 残留靠首行不缩进规避＋控制字符扫描兜底／reflow 输出流分离／渲染前清 png。"""
import re

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件"
LOG = []
log = LOG.append

tex = open(BASE + r"\sec.tex", encoding='utf-8').read()
n_sec_fh = tex.count('；')

# ---- 1. 源清洗（同 v2/v3）：U+2060、箭头归一化、长下划线挖空 ----
tex = tex.replace('\u2060', '')
tex = tex.replace(r'\overset{⃑}{', r'\overrightarrow{')
n_kong = len(re.findall(r'(?:\\_){4,}', tex))
tex = re.sub(r'(?:\\_){4,}', r'\\kongbai{}', tex)
log(f'1. 源清洗：去 U+2060、\\overset{{⃑}}{{}}→\\overrightarrow{{}}（同 v2/v3）；长下划线→\\kongbai ×{n_kong}（题干挖空留白线，'
    f'仅例题/变式/检测；课前预习知识点区挖空经 #4 段改 \\kongda 印答）；源节分号计数（清洗后）＝{n_sec_fh}')

blocks = [b.strip() for b in re.split(r'\n\s*\n', tex) if b.strip()]

# ---- 2. 解析：讲部条目 ＋ 题部组/题 ----
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
log(f'2. 解析：讲部条目 {len(entries)} 个（编注 {sum(1 for e in entries.values() if e["note"])} 条、'
    f'讲部表 {sum(e["tables"] for e in entries.values())} 张，longtable 环境不排印）；题部组 {len(grp_order)} 组、题 {len(tis)} 道：'
    + '；'.join(f'{d["num"]}({d["nanidu"]})' for d in tis.values()))
log('2b. 组数核对：题部组 9 组（1.1.1.2～1.1.1.10，其中 1.1.1.8 含 2 题）＋讲部组 1 组（1.1.1.1）；'
    '【知识点】标签不排印（登记），题侧改挂（知识点N）（见 5g 映射台账）')

# ---- 3. 图分档＋处置（v4.2-A6 重写）：
#      side=题干图 minipage 并排（左 0.56\linewidth 题干文字／右 0.40\linewidth 图 width=\linewidth≈34mm，30mm 档提档）；
#      center=详解内图维持居中独立行（40mm 提档）；三联图 45mm 居中不动。逐图定性登记见 reflow/emit 处 log。
FIG = {'sub3_B_4.png': ('center', '45mm'),   # 条目3 投影三联图：居中独立行不动（v4.2-A6 维持）
       'image1.png': ('side', ''),           # 探究点二例1（题2）图：v4.2-返修2 居中→题干 minipage 并排（5g 段特判抽图）
       'image2.png': ('side', ''),           # 探究点三例1（题3）题干图：minipage 并排
       'image3.png': ('side', ''),           # 探究点六例1（题6）题干图：minipage 并排
       'image4.png': ('side', ''),           # 探究点八例1（题9）题干图：minipage 并排
       'image5.png': ('center', '40mm')}     # 探究点九例1（题10）详解内图：居中 30→40mm 提档
FIGRE = re.compile(r'\\includegraphics\[(width=[\d.]+in,height=[\d.]+in)(,alt=\{[^}]*\})?\]\{([^}]+)\}')
figs_seen = []

def side_row(text, tok, tag):
    r"""v4.2-A6：题干文字（左 0.56\linewidth）＋图（右 0.40\linewidth 居中）minipage 并排行（全品 p06 变式版式）。
    返修3：\includegraphics 基线在图底缘，minipage [t] 联排按首行基线对齐 ⇒ 图底=题干首行基线、
    图顶高出首行顶约整图高（p3 探二实测 dy=−52.2mm）。\raisebox 把基线提到图顶下 \ht\strutbox
    （=0.7\baselineskip=12.6pt≈题干首行盒高）处，图顶≈题干首行顶（实测 |dy|≤0.3mm）。"""
    figs_seen.append(('side', tok, tag))
    return (r'\noindent\begin{minipage}[t]{0.56\linewidth}' + text + r'\end{minipage}\hfill'
            r'\begin{minipage}[t]{0.40\linewidth}\centering'
            r'\raisebox{\dimexpr-\height+\ht\strutbox\relax}{' + tok + r'}\end{minipage}\par')

def reflow(blocks_in, tag):
    out = []
    for b in blocks_in:
        if '\\begin{tabular}' in b or not FIGRE.search(b):
            out.append(b)
            continue
        last = 0
        for mm in FIGRE.finditer(b):
            if b[last:mm.start()].strip():
                out.append(b[last:mm.start()].strip())
            name = mm.group(3).split('/')[-1]
            kind, w = FIG.get(name, ('center', '30mm'))
            assert w, f'{tag}: {name} 未分档'
            tok = mm.group(0).replace(mm.group(1), 'width=' + w)
            if kind == 'side':
                # side 图独立成块抵达此处（不应发生）：与块内已有文字并排，无文字则退化为居中
                out.append(side_row(b[last:mm.start()].strip() or r'\hfill', tok, tag))
            else:
                figs_seen.append((name, w, tag))
                out.append(r'\penalty10000\noindent\makebox[\linewidth][c]{' + tok + r'}\par\penalty10000')
            last = mm.end()
        if b[last:].strip():
            out.append(b[last:].strip())
    return out

def consume_side(stem_list, tag):
    """v4.2-A6：题干块列内首个 side 图——抽出图 token，返回（题干余块、图 token）。无 side 图返回 (原列, None)。"""
    for i, b in enumerate(stem_list):
        for mm in FIGRE.finditer(b):
            name = mm.group(3).split('/')[-1]
            if FIG.get(name, ('', ''))[0] == 'side':
                tok = mm.group(0).replace(mm.group(1), 'width=\\linewidth')
                rest = stem_list[:i] + [b[:mm.start()] + b[mm.end():]] + stem_list[i+1:]
                rest = [x for x in rest if x.strip()]
                return rest, tok
    return stem_list, None

def extract_fig(blocks, figname):
    """v4.2-返修2：从块列中抽出指定图 token（width=\\linewidth）——图在题干后续块（详解流内）时配题干用；
    块内剩余文字保留（空块删除）。找不到即 assert（图源漂移防漏改）。"""
    for i, b in enumerate(blocks):
        for mm in FIGRE.finditer(b):
            if mm.group(3).split('/')[-1] == figname:
                tok = mm.group(0).replace(mm.group(1), 'width=\\linewidth')
                rest = blocks[:i] + [b[:mm.start()] + b[mm.end():]] + blocks[i+1:]
                rest = [x for x in rest if x.strip()]
                return rest, tok
    assert False, f'返修2：{figname} 在块列中未找到（图源漂移，人工复核）'

# ---- 3b. 选项网格（拍板21：极短 4 项/行、短 2 项/行、长 1 行/项；分号字符全保留） ----
COMPOSED = []   # 命制/演示文字流（分号守恒对账用）

def opt_len(s):
    """v4.2-C15 修复：原把 \( \) 括号计入宽度致检测2/检测4 短数学项被判 1 项/行——
    剥控制词（\frac 等）、非字母控制符（\( \) \{ \}）、括号（）()[] 与花括号后再估宽。"""
    t = re.sub(r'\\[a-zA-Z]+', '', s)
    t = re.sub(r'\\[^a-zA-Z]', '', t)
    t = re.sub(r'[\\{}$&%()\[\]（）]', '', t)
    return sum(1.0 if ord(ch) > 0x2E7F else 0.55 for ch in t)

def grid_lines(s):
    """A．…；B．…；C．…；D．… → 槽位网格行；分号原样保留（拆分后逐一回填）。
    v4.2-C15：剥括号后短数学项估宽大降，4 项/行阈值 2.8→4.8（4 槽容量 0.25×栏宽−0.5em≈55.9pt≈5.3 字档，
    阈值 4.8＝内容 ≤3.3 字档≈34.7pt 留余量；检测3 长选项仍 >6.5 判 1 项/行）。"""
    parts = re.split(r'；(?=\s*[A-D]．)', s)
    if len(parts) == 1:
        return [r'\bindopt ' + s]
    opts = [p.strip() for p in parts if p.strip()]
    for i in range(len(opts) - 1):
        if not opts[i].endswith('；'):
            opts[i] += '；'
    # v4.2-C15：项尾「；」为分隔符非选项内容，估宽前剥除（回填原文不动）
    lens = [opt_len(o.rstrip('；')) + 1.5 for o in opts]
    mx, n = max(lens), len(opts)
    per = 4 if (n == 4 and mx <= 4.8) else (2 if mx <= 6.5 else 1)
    rows = []
    for i in range(0, len(opts), per):
        row = opts[i:i + per]
        if len(row) == 1:
            rows.append(r'\bindopt ' + row[0])
        else:
            slot = r'0.25\linewidth-0.5em' if per == 4 else r'0.5\linewidth-1em'
            rows.append(r'\bindopt ' + ''.join(
                r'\makebox[\dimexpr' + slot + r'\relax][l]{' + o + '}' for o in row))
    log(f'3b. 选项网格：{n} 项 {per} 项/行（最长估 {mx:.1f} 字档，v4.2 剥括号估宽）')
    return rows

def emit_blocks(bs):
    """续块分类：A．起且含分号→选项网格；A．/①起→2em 缩进绑定；其余段前绑定。"""
    for s in bs:
        if re.match(r'^A．', s) and '；' in s:
            body.extend(grid_lines(s))
        elif s.startswith(('A．', 'B．', 'C．', 'D．', '①')):
            body.append(r'\bindopt ' + s)
        else:
            body.append(r'\bindp ' + s)

# ---- 4. 挖空印答（原词登记，v4.1 指令1：知识点区 \kongbai→\kongda 印出下划线答案） ----
n_kb = [0]
def kb(word):
    n_kb[0] += 1
    log(f'4. 挖空印答 #{n_kb[0]}：原词「{word}」→ \\kongda{{{word}}}（下划线印出，最小宽 15mm 自适应）')
    return r'\kongda{' + word + '}'

TABW = ('17', '37', '25')   # v4.2-C14 起按表配宽（kbtable 第 5 参显式传入），此默认仅存档
n_tab = [0]
def kbtable(h1, h2, h3, rows, widths, tcsep=3):
    """v4.2-C14：列宽内容驱动（对照全品 p04 表三列宽比 19%:41%:40%）——
    可用宽＝栏宽 86.2mm−框线 4×0.4pt−tabcolsep 6×tcsep；三列和 ≤可用宽；逐表编译目检微调。
    v4.2-表1 翻修：tcsep 2pt 档（组内局部 \setlength，不影响全局 3pt）——配合 (16,35,29) 使
    定义列 35mm（省 2 折行行、表1 装进 p1 左栏）且名称列保 16mm（4 字名不折行）。"""
    n_tab[0] += 1
    usable = 86.2 - 1.6 * 25.4 / 72 - 6 * tcsep * 25.4 / 72   # 框线 4×0.4pt＋tabcolsep 6×tcsep，折 mm
    head = ' & '.join(r'\multicolumn{1}{|>{\centering\arraybackslash}p{' + w + 'mm}|}{\\textbf{' + c + '}}'
                      for c, w in zip((h1, h2, h3), widths))
    lines = ['{\\setlength{\\tabcolsep}{' + str(tcsep) + 'pt}',
             r'\noindent\begin{tabular}{|>{\raggedright\arraybackslash}p{' + widths[0] +
             r'mm}|>{\raggedright\arraybackslash}p{' + widths[1] +
             r'mm}|>{\raggedright\arraybackslash}p{' + widths[2] + r'mm}|}', r'\hline', head + r' \\', r'\hline']
    for r in rows:
        lines.append(' & '.join(r) + r' \\ \hline')
    lines.append(r'\end{tabular}\par')
    lines.append('}')
    body.append('\n'.join(lines))
    log(f'4b. 三列挖空表 #{n_tab[0]}：白底黑体表头＋全框 0.4pt 细线（arraystretch 1.05（v4.2 让位后 1.15→1.05），'
        f'列宽内容驱动 {"/".join(widths)}mm＋tabcolsep {tcsep}pt——v4.2-C14 按表配宽，三列和 '
        f'{sum(int(x) for x in widths)}mm≤{usable:.1f}mm 门），'
        f'{len(rows)} 行（cells 选编自源讲部表，挖空印答见 #4 登记）')

# ---- 5. 组装正文 ----
body = []
em = body.append
LAN_OPEN = '\\begin{multicols}{2}\n\\emergencystretch=8em'
LAN_CLOSE = '\\end{multicols}'

def huaxing(chars, xiao):
    em(r'\huaxing{' + '}{'.join(chars) + '}{' + xiao + '}')
    COMPOSED.append(chars + xiao)

# 学习目标（楷体化压缩，通栏区——见 chapterhead 组装段 7）
log('5a. 【学习目标】3 条＝演示编写（v3 文案压缩：条目压至 ≤1 行/条，三条要点全保留），楷体排印（拍板28），移入章首通栏区（防 multicols 短栏平衡），登记')

em(LAN_OPEN)
huaxing('课前预习', '知识导学\\quad 素养初识')
log('5b. 花形行×3＝4 字菱形标（tikz diamond 白底黑边黑字连排）＋右侧灰小字＋栏宽 midgray 细线（v4.1 指令6 栏内化，'
    '推翻拍板28 通栏与拍板27 黑线，登记）；文案对齐全品（v4.2-21 新实证修订）：课前预习＝知识导学　素养初识（p04）、'
    '课中探究＝考点探究　素养小结（p05，v4.1 误作「素养提升」已正）、课堂评价＝知识评价　素养形成（p07；'
    '全品第三花形名＝「课堂评价」非「课堂检测」，v4.1「限时训练　当堂达标」撤）；'
    '单一 multicols，课前预习花形为栏内首元素')

# —— ◆知识点一（诊断块①）——
em(r'\zsd{一}{空间向量的概念}')
em(r'\tiaomu{1}{定义：在空间，我们把具有' + kb('大小') + '和' + kb('方向') + r'的量叫做空间向量．'
   r'\zhuzhu{' + entries[1]['note'] + '}}')
# v4.2-C11：条目内（1）（2）并列子项各自成段——条目 2 拆为条目号段（（1）字母表示法）＋ \bindp（2）几何表示法段（序号保留）
em(r'\tiaomu{2}{（1）字母表示法：用字母 \(\overrightarrow{a},\overrightarrow{b},\overrightarrow{c},\cdots\) 表示．}')
em(r'\bindp （2）几何表示法：用有向线段表示，其' + kb('长度') + r'表示空间向量的模．即若向量 \(\overrightarrow{a}\) 的起点是 \(A\)、终点是 \(B\)，'
   r'则向量 \(\overrightarrow{a}\) 也可记作 \(\overrightarrow{AB}\)，其模记为 \(\left| \overrightarrow{AB} \right|\)．'
   r'\zhuzhu{' + entries[2]['note'] + '}')
em(r'\tiaomu{3}{几类特殊向量（见下表）；规定：' + kb('零') + r'向量与任意向量平行．即对任意向量 \(\overrightarrow{a}\)，'
   r'都有 \(\overrightarrow{0}\parallel\overrightarrow{a}\)．\zhuzhu{' + entries[3]['note'] + '}}')
kbtable('名称', '定义', '表示', [
    [r'零向量', r'长度为' + kb('0') + r'的向量叫做零向量', r'记作' + kb('0')],
    [r'单位向量', r'模等于' + kb('1') + r'的向量', r'用 \(e\) 表示，\(|e|=1\)'],
    [r'相反向量', r'与 \(\overrightarrow{a}\) 长度相同而方向' + kb('相反') + r'的向量', r'记作 \(-\overrightarrow{a}\)'],
    [r'共线向量或平行向量', r'表示若干空间向量的有向线段所在的直线' + kb('互相平行') + r'或' + kb('重合'), r'记作 \(\overrightarrow{a}\parallel\overrightarrow{b}\)'],
    [r'相等向量', r'方向相同且' + kb('模相等') + r'的向量', r'记作 \(\overrightarrow{a}=\overrightarrow{b}\)'],
], ('16', '35', '29'), tcsep=2)
log('5c-表1. 列宽翻修（16,33,30）→（16,35,29）＋tabcolsep 3→2pt（本表局部组内）：拍板22 版心底 20mm 让位页脚后 '
    'p1 左栏余 81.1mm，(16,33,30) 档表1 实测 85.0mm 装不下（arraystretch 1.15→1.05 仅省 1.2mm——表高主体是折行内容非 strut，'
    '预估 5.8mm 落空）；定义列 33→35mm 使「模等于□1的向量」与「共线向量或平行向量」行各省 1 折行行，表1 → 78.7mm 归位左栏底'
    '（余 2.4mm），p1 左栏利用率 69%→99%；曾试（14,35,30）同装下但名称列 4 字名全折行，目检不过，改 tabcolsep 让宽保名称列')
log('5c. 知识点一：条目 1～3 选编＋挖空印答（v4.1 指令1）；编注以 \\zhuzhu 并入条目段末同段接排（独立段数 0，字符总量不变，对照§四-7）；'
    '三列挖空表 cells 选编自源讲部「特殊向量」表；'
    'v4.2-C11：条目 2（1）（2）并列子项各自成段（全件扫描：条目体内（N）并列且同段连排仅此 1 处——'
    '条目 3 投影向量源文已分段、其余条目无（N）并列，登记），条目号段（（1）字母表示法）＋\\bindp（2）段，序号保留')
em(r'\zhenhead{判断正误（正确的打“√”，错误的打“×”）}')
PANDUAN = {
    1: [(r'两个空间向量的模相等，则这两个向量相等．', '×',
         r'模相等方向未必相同，还可能相反或斜交，两向量未必相等，故×．'),
        (r'相等向量一定是共线向量．', '√',
         r'相等向量方向相同，所在直线平行或重合，符合共线向量（平行向量）定义，故√．')],
    2: [(r'若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，\(\overrightarrow{b}\parallel\overrightarrow{c}\)，则 \(\overrightarrow{a}\parallel\overrightarrow{c}\)．', '×',
         r'平行传递需 \(\overrightarrow{b}\neq\overrightarrow{0}\)；\(\overrightarrow{b}=\overrightarrow{0}\) 时零向量与任意向量平行，传递性失效，故×．'),
        (r'若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，则存在唯一实数 \(\lambda\)，使 \(\overrightarrow{a}=\lambda\overrightarrow{b}\)．', '×',
         r'缺 \(\overrightarrow{b}\neq\overrightarrow{0}\) 前提；且 \(\overrightarrow{a}=\overrightarrow{0}\) 时 \(\lambda\) 不唯一，故×．')],
    3: [(r'若 \(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\)（\(\overrightarrow{a}\)，\(\overrightarrow{b}\) 不共线），则 \(\overrightarrow{p}\)，\(\overrightarrow{a}\)，\(\overrightarrow{b}\) 共面．', '√',
         r'\(\overrightarrow{p}\) 是 \(\overrightarrow{a}\)、\(\overrightarrow{b}\) 的线性组合，由共面向量定理知三向量共面，故√．'),
        (r'两个非零空间向量的数量积大于 \(0\)，则这两个向量的夹角为锐角．', '×',
         r'数量积大于 0 仅保证 \(\cos\theta>0\)，夹角 \(\theta\in[0^\circ,90^\circ)\)；\(\theta=0^\circ\)（同向）时数量积也为正而非锐角，故×．')],
}
def panduan_block(bh):
    for i, (t, a, jx) in enumerate(PANDUAN[bh], 1):
        em(r'\zhenti{（' + str(i) + '）}{' + t + '}{' + a + '}{' + jx + '}')
        COMPOSED.append(t)
    COMPOSED.extend(jx for _, _, jx in PANDUAN[bh])
panduan_block(1)
log('5c′. 【诊断分析】块①（知识点一后紧跟，拍板35⑤）＝2 道：沿用 v3 已亲算 2 道（模相等⇒相等×；相等⇒共线√）；'
    'v4.1 指令2：序号（一）（二）→全品式（1）（2），逐题加一句话【解析】（6.5pt 灰顶格，数学正确性逐题复核），登记')

# —— ◆知识点二（诊断块②）——
em(r'\zsd{二}{空间向量的线性运算}')
em(r'\tiaomu{1}{加法可按' + kb('三角形') + r'法则或' + kb('平行四边形') + r'法则作出；减法 \(\overrightarrow{a}-\overrightarrow{b}\) '
   r'为减向量终点指向被减向量终点；数乘 \(\lambda\overrightarrow{a}\)：当 \(\lambda>0\) 时与 \(\overrightarrow{a}\) 方向' + kb('相同') +
   r'，当 \(\lambda<0\) 时方向' + kb('相反') + r'，当 \(\lambda=0\) 时 \(\lambda\overrightarrow{a}=\overrightarrow{0}\)．'
   r'\zhuzhu{' + entries[4]['note'] + '}}')
em(r'\tiaomu{2}{共线的充要条件：对任意两个空间向量 \(\overrightarrow{a},\overrightarrow{b}\)（\(\overrightarrow{b}\neq\overrightarrow{0}\)），'
   r'\(\overrightarrow{a}\parallel\overrightarrow{b}\) 的充要条件是存在' + kb('实数') +
   r' \(\lambda\)，使 \(\overrightarrow{a}=\lambda\overrightarrow{b}\)．\zhuzhu{' + entries[5]['note'] + '}}')
kbtable('运算', '法则要点', '运算律举例', [
    [r'加法', r'三角形法则／平行四边形法则（与平面向量一致）', r'\(\overrightarrow{a}+\overrightarrow{b}=\overrightarrow{b}+\overrightarrow{a}\)'],
    [r'减法', r'减向量终点指向被减向量终点', r'\((\overrightarrow{a}+\overrightarrow{b})+\overrightarrow{c}=\overrightarrow{a}+(\overrightarrow{b}+\overrightarrow{c})\)'],
    [r'数乘', r'实数 \(\lambda\) 与向量 \(\overrightarrow{a}\) 的乘积仍为向量', r'\((\lambda+\mu)\overrightarrow{a}=\lambda\overrightarrow{a}+\mu\overrightarrow{a}\)'],
    [r'共线', r'\(\overrightarrow{a}\parallel\overrightarrow{b}\)（\(\overrightarrow{b}\neq\overrightarrow{0}\)）', r'\(\overrightarrow{a}=\lambda\overrightarrow{b}\)'],
], ('10', '37', '32'))
log('5d. 知识点二：条目 1～2（原 4～5 重编号，v4.1 指令8 按知识点重起）＋挖空印答＋编注并段；三列挖空表 cells 选编自源讲部「加法／运算律」表')
em(r'\zhenhead{判断正误（正确的打“√”，错误的打“×”）}')
panduan_block(2)
log('5d′. 【诊断分析】块②＝2 道：第 1 道沿用 v3 已亲算（平行传递×，b=0 反例）；'
    r'第 2 道 v4 轮新命制（亲算：\(\overrightarrow{b}=\overrightarrow{0}\) 时前提失效、\(\overrightarrow{a}=\overrightarrow{0}\) 时 λ 不唯一，故×），共线充要条件前提辨析；'
    'v4.1 指令2：全品式序号＋逐题加【解析】，登记')

# —— ◆知识点三（诊断块③）——
em(r'\zsd{三}{空间向量的夹角、数量积与共面}')
em(r'\tiaomu{1}{夹角：已知两个非零向量 \(\overrightarrow{a},\overrightarrow{b}\)，在空间中任取一点 \(O\)，'
   r'作 \(\overrightarrow{OA}=\overrightarrow{a},\overrightarrow{OB}=\overrightarrow{b}\)，则大小在' + kb('[0°,180°]') +
   r'内的 \(\angle AOB\) 称为 \(\overrightarrow{a}\) 与 \(\overrightarrow{b}\) 的夹角，记作 \(\langle\overrightarrow{a},\overrightarrow{b}\rangle\)；'
   r'当 \(\langle\overrightarrow{a},\overrightarrow{b}\rangle=\frac{\pi}{2}\) 时，称 \(\overrightarrow{a}\) 与 \(\overrightarrow{b}\)' +
   kb('互相垂直') + r'，记作 \(\overrightarrow{a}\perp\overrightarrow{b}\)．\zhuzhu{' + entries[6]['note'] + '}}')
weiti = next((s for s in entries[7]['blocks'] if s.startswith('【微提醒】')), '')
em(r'\tiaomu{2}{数量积：定义 \(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle\)；'
   '规定' + kb('零向量') + r'与任意向量的数量积为 0．'
   r'性质：\(\overrightarrow{a}\perp\overrightarrow{b}\Leftrightarrow\overrightarrow{a}\cdot\overrightarrow{b}=0\)；'
   r'\(\overrightarrow{a}\cdot\overrightarrow{a}={{\overrightarrow{a}}^{2}}={\left| \overrightarrow{a} \right|}^{2}\)；'
   r'\(\left| \overrightarrow{a}\cdot\overrightarrow{b} \right|\leq\left| \overrightarrow{a} \right|\left| \overrightarrow{b} \right|\)．'
   + (r'\zhuzhu{' + weiti + '}' if weiti else '') +
   r'\zhuzhu{' + entries[7]['note'] + '}}')
blk8 = list(entries[8]['blocks'])
blk8[0] = blk8[0] + r'\zhuzhu{' + entries[8]['note'] + '}'   # 条目8 编注并入首段段末（v3 漏排，v4 补排）
em(r'\tiaomu{3}{投影向量：' + blk8[0] + '}')
emit_blocks(reflow(blk8[1:], '知识点三'))
log('5e. 知识点三：条目 1～2（原 6～7 重编号）选编＋挖空印答＋编注并段（微提醒同段并排）；'
    '条目 3（原条目 8「投影向量」，v4.1 指令8 入号，题名「投影向量」取自源条目名）整段源文排印（含投影三联图 45mm 独立居中，编注并入首段段末——v3 漏排，v4 补排登记）；'
    '条目 2 源（2）块内容已由条目 2 自编性质句全量覆盖（选编授权，源块不另排）')
em(r'\tiaomu{4}{共面的充要条件：向量 \(\overrightarrow{p}\) 与不共线向量 \(\overrightarrow{a},\overrightarrow{b}\) 共面的充要条件是存在' +
   kb('有序实数对') + r' \((x,y)\)，使 \(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\)．\zhuzhu{' + entries[9]['note'] + '}}')
kbtable('概念', '要点', '记号／范围', [
    [r'夹角', r'\(\angle AOB\)（\(\overrightarrow{OA}=\overrightarrow{a},\overrightarrow{OB}=\overrightarrow{b}\)）',
     r'\(0^\circ\leq\langle\overrightarrow{a},\overrightarrow{b}\rangle\leq180^\circ\)'],
    [r'数量积', r'\(\overrightarrow{a}\) 的模与 \(\overrightarrow{b}\) 在 \(\overrightarrow{a}\) 上投影的数量之积',
     r'\(\overrightarrow{a}\allowbreak\cdot\allowbreak\overrightarrow{b}\allowbreak=\allowbreak|\overrightarrow{a}|\allowbreak|\overrightarrow{b}|\allowbreak\cos\allowbreak\langle\overrightarrow{a},\overrightarrow{b}\rangle\)'],
    [r'投影向量', r'与 \(\overrightarrow{b}\) 同向（\(\cos\allowbreak\langle\overrightarrow{a},\overrightarrow{b}\rangle\allowbreak>0\) 时）',
     r'模为 \(|\overrightarrow{a}|\allowbreak\cos\allowbreak\langle\overrightarrow{a},\overrightarrow{b}\rangle\)'],
    [r'共面', r'存在 \((x,y)\) 使 \(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\)（\(\overrightarrow{a},\overrightarrow{b}\) 不共线）',
     r'\(\overrightarrow{p},\overrightarrow{a},\overrightarrow{b}\) 共面'],
], ('10', '36', '33'))
em(r'\zhenhead{判断正误（正确的打“√”，错误的打“×”）}')
panduan_block(3)
log('5e′. 【诊断分析】块③＝2 道：第 1 道沿用 v3 已亲算（共面表示√）；'
    r'第 2 道 v4 轮新命制（亲算：取 \(\overrightarrow{a}=2\overrightarrow{b}\) 同向得数量积 \(>0\) 而夹角 \(0^\circ\) 非锐角，故×），夹角范围辨析；'
    'v4.1 指令2：全品式序号＋逐题加【解析】，登记')

# —— 课中探究（探究点×9 恒式；花形行栏内化，无 multicols 切分）——
# v4.2-21：右侧文案对齐全品 p05 实证＝「考点探究　素养小结」（v4.1 误作「素养提升」，正）
huaxing('课中探究', '考点探究\\quad 素养小结')

SANJU = {
    2: r'①识别：题干围绕模、方向、零向量、单位向量、相等向量与相反向量罗列说法要求辨误时，判归本题型。'
       r'②操作：对照定义逐条核验，存疑条目用反例否定。③收束：排除错误项定答案，忌凭直觉误选。',
    3: r'①识别：在几何体中给出若干已知向量、要求表示指定向量时，判归本题型。'
       r'②操作：为目标向量选一条首尾相接的路径写出加减链，再把链中各段用相等或共线的已知向量替换，最后合并化简得表达式。'
       r'③收束：复查每段方向与起讫点，防抄错向量。',
    4: r'①识别：指定三个不共面的向量作基底、要求把目标向量写成基底向量的线性组合并求系数时，判归本题型。'
       r'②操作：先把目标向量沿几何路径分解为基底向量的和，再把各段按比例关系代入基底。'
       r'③收束：比较等式两边系数求出待定值，防漏写中间段。',
    5: r'①识别：题干给出 p=xa+yb 或 MP=xMA+yMB 一类线性表示与“共面”结论的互推说法判断时，判归本题型。'
       r'②操作：核对充要条件的前提（两向量不共线或三点不共线）是否齐备，再对缺前提的说法举共线反例排除。'
       r'③收束：最后汇总正确序号定选项。',
    6: r'①识别：题干列出数量积相关的若干等式（平方、商式、乘积展开）要求判断正误时，判归本题型。'
       r'②操作：按定义 a·b=|a||b|cosθ 逐式展开核验，展开后移项验算。'
       r'③收束：警惕向量无除法、数量积无结合律等误用。',
    7: r'①识别：题干在几何体中求两向量的夹角、模长或投影而不建坐标系时，判归本题型。'
       r'②操作：先平移向量使起点共点或选不共面的三个向量作基底，再把相关向量用基底表示并算出数量积与模长。'
       r'③收束：最后代入夹角公式并按向量夹角范围 [0,π] 取角。',
    8: r'①识别：题干给出两向量的模与夹角、并以夹角为锐角/钝角或两向量垂直为条件求参数时，判归本题型。'
       r'②操作：第一步用数量积把条件翻译成不等式或方程（锐角 cos>0、钝角 cos<0、垂直 cos=0）。'
       r'③收束：再求解并剔除使两向量共线的参数，最后写出参数值或取值范围。',
    9: r'①识别：题干在含二面角的拼接图形中求两点距离时，判归本题型。'
       r'②操作：第一步把待求线段对应的向量写成已知棱向量的首尾相接和链，再对模长平方作数量积展开，'
       r'逐项代入模长与夹角（端点处两条垂线段的夹角由二面角决定，注意取 45° 还是 135°）。③收束：最后开方得距离。',
    10: r'①识别：题干为平面图形沿一条直线折起且折后两面垂直、求两点间距离时，判归本题型。'
        r'②操作：第一步在折后图形中过两点对折痕作垂线定出垂足，再把目标向量写成两段垂线与折痕段的和链并平方展开。'
        r'③收束：最后利用面面垂直带来的向量垂直逐项化简、开方得距离。',
}
# v4.2-E18 撤★精选标（翻拍板25 导学件部分：全品导学案无★，★属练习册体系）——原 STAR 字典
# （探究点一/七/九典型性理由）整体撤除，\tjdnr 形参 #4 一并撤（宏签名 4 参），COMPOSED 不再收入理由文字
log('5f-0. ★精选标撤除（v4.2-E18，翻拍板25 导学件部分）：原 v4 拍板25 ★×3（探究点一概念母题/七求参母题/九折叠距离方法母题'
    '＋典型性理由题侧 6.5pt 灰）整体撤——全品导学案无★精选标（★属练习册体系，p04-p07 实证）；'
    '\\tjdnr 宏签名 5 参→4 参（撤 #4 ★块位），COMPOSED 同步不再收入理由文字，断言⑥ ★=0')
CN = '一二三四五六七八九'
KN = {2: '一', 3: '二', 4: '二', 5: '三', 6: '三', 7: '三', 8: '三', 9: '三', 10: '三'}   # 组号→知识点块序

# 变式六策命制（探究点一～六、八、九；亲算核验逐条登记）
BIAN_COMPOSED = {
    1: {'ce': '逆向化＋概念辨析化（选正确→选错误）', 'nd': '简单',
        'stem': r'下列说法错误的是（~~~~）',
        'opts': r'A．零向量与任意向量都平行；B．若 \(|\overrightarrow{a}|=0\)，则 \(\overrightarrow{a}=\overrightarrow{0}\)；'
                r'C．若 \(\overrightarrow{a}=\overrightarrow{b}\)，则 \(|\overrightarrow{a}|=|\overrightarrow{b}|\)；'
                r'D．若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，则 \(|\overrightarrow{a}|=|\overrightarrow{b}|\)',
        'ans': r'\ansul{D}',
        'jc': r'亲算：A 规定成立；B 模为 0 即零向量；C 相等必等模；D 平行不需等模（反例 \(\overrightarrow{a}=2\overrightarrow{b}\)），故选 D．'},
    2: {'ce': '换载体（直三棱柱→平行六面体）＋换设问', 'nd': '简单',
        'stem': r'在平行六面体 \(ABCD-A_1B_1C_1D_1\) 中，\(\overrightarrow{AB}=\overrightarrow{a}\)，\(\overrightarrow{AD}=\overrightarrow{b}\)，'
                r'\(\overrightarrow{AA_1}=\overrightarrow{c}\)，则 \(\overrightarrow{D_1B}=\)\kongbai{}．（用 \(\overrightarrow{a}\)，\(\overrightarrow{b}\)，\(\overrightarrow{c}\) 表示）',
        'ans': r'\ansul{\(\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\)}',
        'jc': r'亲算：\(\overrightarrow{D_1B}=\overrightarrow{D_1A_1}+\overrightarrow{A_1A}+\overrightarrow{AB}=-\overrightarrow{b}-\overrightarrow{c}+\overrightarrow{a}\)．'},
    3: {'ce': '换载体＋换数值（正方体 1/4→平行六面体 1/2）', 'nd': '简单',
        'stem': r'在平行六面体 \(ABCD-A_1B_1C_1D_1\) 中，点 \(E\) 在 \(A_1C_1\) 上，且 \(\overrightarrow{A_1E}=\frac{1}{2}\overrightarrow{A_1C_1}\)，'
                r'若 \(\overrightarrow{AE}=x\overrightarrow{AA_1}+y(\overrightarrow{AB}+\overrightarrow{AD})\)，则 \(x=\)\kongbai{}，\(y=\)\kongbai{}．',
        'ans': r'\ansul{\(x=1\)}，\ansul{\(y=\frac{1}{2}\)}',
        'jc': r'亲算：\(\overrightarrow{AE}=\overrightarrow{AA_1}+\overrightarrow{A_1E}=\overrightarrow{AA_1}+\frac{1}{2}(\overrightarrow{AB}+\overrightarrow{AD})\)，故 x=1，y=1/2．'},
    4: {'ce': '换设问（互推选择→判定说明）', 'nd': '简单',
        'stem': r'已知 \(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\)，判断 \(P\)，\(M\)，\(A\)，\(B\) 四点是否共面，并说明理由．',
        'ans': r'\ansul{共面}（\(\overrightarrow{MP}\) 可由 \(\overrightarrow{MA}\)，\(\overrightarrow{MB}\) 线性表示，故 \(\overrightarrow{MP}\)，\(\overrightarrow{MA}\)，\(\overrightarrow{MB}\) 共面，即 \(P\) 在平面 \(MAB\) 内）',
        'jc': r'亲算：MP=3MA−2MB 为 MA、MB 的线性组合 ⇒ 三向量共面 ⇒ P∈平面 MAB．'},
    5: {'ce': '换设问（辨析→展开计算）', 'nd': '简单',
        'stem': r'已知 \(|\overrightarrow{a}|=2\)，\(|\overrightarrow{b}|=3\)，\(\langle\overrightarrow{a},\overrightarrow{b}\rangle=60^\circ\)，'
                r'则 \((\overrightarrow{a}+2\overrightarrow{b})\cdot(\overrightarrow{a}-\overrightarrow{b})=\)\kongbai{}．',
        'ans': r'\ansul{\(-11\)}',
        'jc': r'亲算：a·b=2×3×cos60°=3；原式=a²+a·b−2b²=4+3−18=−11．'},
    6: {'ce': '换载体（正方体→长方体）＋换设问（求角→求余弦值）', 'nd': '中档',
        'stem': r'在长方体 \(ABCD-A_1B_1C_1D_1\) 中，\(AB=2\)，\(AD=2\)，\(AA_1=1\)，则向量 \(\overrightarrow{AB_1}\) 与 \(\overrightarrow{AC}\) 夹角的余弦值为\kongbai{}．',
        'ans': r'\ansul{\(\frac{\sqrt{10}}{5}\)}',
        'jc': r'亲算：\(\overrightarrow{AB_1}\cdot\overrightarrow{AC}=(\overrightarrow{AB}+\overrightarrow{BB_1})\cdot(\overrightarrow{AB}+\overrightarrow{BC})=|\overrightarrow{AB}|^2=4\)；'
              r'\(|\overrightarrow{AB_1}|=\sqrt5\)，\(|\overrightarrow{AC}|=2\sqrt2\)；cos=4/(√5·2√2)=√10/5．'},
    8: {'ce': '换数值（二面角 45°→60°）', 'nd': '简单',
        'stem': r'在大小为 \(60^\circ\) 的二面角 \(A-EF-D\) 中，四边形 \(ABFE\)，\(CDEF\) 都是边长为 \(1\) 的正方形，'
                r'则 \(B\)，\(D\) 两点间的距离为\kongbai{}．',
        'ans': r'\ansul{\(\sqrt{2}\)}',
        'jc': r'亲算：\(|\overrightarrow{BD}|^2=1+1+1+2\overrightarrow{BF}\cdot\overrightarrow{ED}=3+2\cos120^\circ=2\)，故 √2．'},
    9: {'ce': '换条件（折起 90°→60° 二面角）', 'nd': '中档',
        'stem': r'已知矩形 \(ABCD\) 中，\(AB=1\)，\(BC=\sqrt{3}\)，将矩形 \(ABCD\) 沿对角线 \(AC\) 折起，使二面角 \(B-AC-D\) 的大小为 \(60^\circ\)，'
                r'则 \(|\overrightarrow{BD}|=\)\kongbai{}．',
        'ans': r'\ansul{\(\frac{\sqrt{13}}{2}\)}',
        'jc': r'亲算：BM=DN=√3/2，MN=1，两垂线向量夹角随二面角 60° 得 \(\overrightarrow{BM}\cdot\overrightarrow{ND}=\frac{3}{4}\cos60^\circ=\frac{3}{8}\)；'
              r'\(|\overrightarrow{BD}|^2=\frac{3}{4}+1+\frac{3}{4}+2\cdot\frac{3}{8}=\frac{13}{4}\)，故 √13/2．'},
}
for g, d in BIAN_COMPOSED.items():
    COMPOSED.append(d['stem'])
    if 'opts' in d:
        COMPOSED.append(d['opts'])
    COMPOSED.append(d['ans'])

# v4.2-D16：变式1×9 补【解析】简析行（8pt 黑，排【答案】行下一行）——亲算文字即 BIAN_COMPOSED 各 jc 字段转写；
# 探究点七变式1（源题8）简析由题干答案自明，自拟一句亲算句（m·n=0 展开，λ=−3/2）
BIAN_JX = {
    1: r'A 规定成立；B 模为 0 即零向量；C 相等必等模；D 平行不需等模（反例 \(\overrightarrow{a}=2\overrightarrow{b}\)），故选 D．',
    2: r'\(\overrightarrow{D_1B}=\overrightarrow{D_1A_1}+\overrightarrow{A_1A}+\overrightarrow{AB}=-\overrightarrow{b}-\overrightarrow{c}+\overrightarrow{a}\)．',
    3: r'\(\overrightarrow{AE}=\overrightarrow{AA_1}+\overrightarrow{A_1E}=\overrightarrow{AA_1}+\frac{1}{2}(\overrightarrow{AB}+\overrightarrow{AD})\)，故 \(x=1\)，\(y=\frac{1}{2}\)．',
    4: r'\(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\) 为 \(\overrightarrow{MA}\)、\(\overrightarrow{MB}\) 的线性组合，故三向量共面，\(P\) 在平面 \(MAB\) 内．',
    5: r'\(\overrightarrow{a}\cdot\overrightarrow{b}=2\times3\times\cos60^\circ=3\)；原式 \(=\overrightarrow{a}^2+\overrightarrow{a}\cdot\overrightarrow{b}-2\overrightarrow{b}^2=4+3-18=-11\)．',
    6: r'\(\overrightarrow{AB_1}\cdot\overrightarrow{AC}=(\overrightarrow{AB}+\overrightarrow{BB_1})\cdot(\overrightarrow{AB}+\overrightarrow{BC})=|\overrightarrow{AB}|^2=4\)，\(|\overrightarrow{AB_1}|=\sqrt{5}\)，\(|\overrightarrow{AC}|=2\sqrt{2}\)，故 \(\cos\langle\overrightarrow{AB_1},\overrightarrow{AC}\rangle=\frac{4}{\sqrt{5}\times2\sqrt{2}}=\frac{\sqrt{10}}{5}\)．',
    7: r'\(\overrightarrow{m}\cdot\overrightarrow{n}=(\overrightarrow{a}+\overrightarrow{b})\cdot(\overrightarrow{a}+\lambda\overrightarrow{b})=|\overrightarrow{a}|^2+\lambda|\overrightarrow{b}|^2+(1+\lambda)\overrightarrow{a}\cdot\overrightarrow{b}=18+16\lambda-12(1+\lambda)=6+4\lambda=0\)，故 \(\lambda=-\frac{3}{2}\)．',
    8: r'\(|\overrightarrow{BD}|^2=1+1+1+2\overrightarrow{BF}\cdot\overrightarrow{ED}=3+2\cos120^\circ=2\)，故 \(|\overrightarrow{BD}|=\sqrt{2}\)．',
    9: r'\(BM=DN=\frac{\sqrt{3}}{2}\)，\(MN=1\)；两垂线向量夹角随二面角为 \(60^\circ\)，\(\overrightarrow{BM}\cdot\overrightarrow{ND}=\frac{3}{4}\cos60^\circ=\frac{3}{8}\)；'
       r'\(|\overrightarrow{BD}|^2=\frac{3}{4}+1+\frac{3}{4}+2\times\frac{3}{8}=\frac{13}{4}\)，故 \(|\overrightarrow{BD}|=\frac{\sqrt{13}}{2}\)．',
}
for g, jx in BIAN_JX.items():
    COMPOSED.append(jx)

GRP_KS = {}
for (gn, k) in tis:
    GRP_KS.setdefault(gn, []).append(k)
for gn in GRP_KS:
    GRP_KS[gn].sort()

def sanju_rows(s):
    """v4.2-C12：素养小结三句式按①②③拆行——首段（①识别）随【素养小结】标签，②③各自 \\bindp 顶格独立段。"""
    i2, i3 = s.find('②'), s.find('③')
    assert 0 < i2 < i3, f'素养小结三句式拆分异常：{s[:24]}'
    return s[:i2], s[i2:i3], s[i3:]

for gi, gname in enumerate(grp_order, 1):
    gnum = int(re.match(r'1\.1\.1\.(\d+)', gname).group(1))
    kn = KN[gnum]
    d = tis[(gnum, GRP_KS[gnum][0])]   # 各组第 1 题＝X-1（组2→题1…组8→题7；组8 双题后组9→题9、组10→题10）
    stem_rest, side_tok = consume_side(d['stem'][1:], f'例{gi}')
    if side_tok is None and gi == 2:
        # v4.2-返修2：探究点二例1 题图并排漏改补——image1 在源题 stem 后续块（【详解】流内，居中独立行），
        # 特判抽图与题干 minipage 并排（与探三/六/八同款：题左 0.56／图右 0.40）
        d['xiangjie'], side_tok = extract_fig(d['xiangjie'], 'image1.png')
        log('3-图. 探究点二例1 图 image1 详解流内居中→题干 minipage 并排（返修2：题左 0.56\\linewidth／'
            '图右 0.40\\linewidth≈34mm，与探三/六/八同款；图在源题 stem 后续块，extract_fig 特判抽图）')
    if side_tok is not None:
        # v4.2-A6：题干图 minipage 并排（全品 p06 变式版式：题左图右）——◆标签行题干位传空，题干文字入图行左栏
        em(r'\tjdnr{' + CN[gi-1] + '｜' + gname.split(' ', 1)[1] + '}{例1}{' + d['nanidu'] + '（知识点' + kn + '）}{}')
        em(side_row(d['stem'][0], side_tok, f'例{gi}'))
        log(f'3-图. 探究点{CN[gi-1]}例1 题干图→minipage 并排（左 0.56\\linewidth 题干／右 0.40\\linewidth 图≈34mm，30mm 档提档；'
            f'图文并排全品 p06 实证：图约占栏宽 42%、文字约 55%；返修3 图盒 \\raisebox 顶对齐题干首行）')
    else:
        em(r'\tjdnr{' + CN[gi-1] + '｜' + gname.split(' ', 1)[1] + '}{例1}{' + d['nanidu'] + '（知识点' + kn + '）}{' + d['stem'][0] + '}')
    emit_blocks(reflow(stem_rest, f'例{gi}'))
    emit_blocks(reflow(d['fenxi'], f'例{gi}'))
    emit_blocks(reflow(d['xiangjie'], f'例{gi}'))
    if d['dj']:
        emit_blocks(reflow(d['dj'], f'例{gi}'))
    if gi in BIAN_COMPOSED:
        v = BIAN_COMPOSED[gi]
        em(r'\li{变式1}{' + v['nd'] + '（知识点' + kn + '）}{}{' + v['stem'] + '}')
        if 'opts' in v:
            emit_blocks([v['opts']])
        em(r'\ansline{' + v['ans'] + '}')
        em(r'\jiexi{' + BIAN_JX[gi] + '}')
        log(f'5g. 探究点{CN[gi-1]}：例1＝{d["num"]}（{d["nanidu"]}，源题原样，【分析】【详解】紧跟'
            + ('＋【点睛】' if d['dj'] else '') + '）；变式1＝新命制（' + v['ce'] + '，' + v['nd'] + '）；' + v['jc']
            + '；v4.2-D16 补【解析】简析行（8pt 黑，答案行下一行，jc 转写）')
    else:
        d8 = tis[(gnum, GRP_KS[gnum][1])]   # 组8 第 2 题＝题8（组内第 2 题按节内全局编号）
        em(r'\li{变式1}{' + d8['nanidu'] + '（知识点' + kn + '）}{}{' + d8['stem'][0] + '}')
        emit_blocks(reflow(d8['stem'][1:], f'变式{gi}'))
        em(r'\ansline{\ansul{' + d8['ans'] + '}}')
        em(r'\jiexi{' + BIAN_JX[gi] + '}')
        log(f'5g. 探究点{CN[gi-1]}：例1＝{d["num"]}（{d["nanidu"]}，源题原样）；'
            f'变式1＝{d8["num"]}（{d8["nanidu"]}，源题池配——拍板16 源题优先，池尽方命制），答案行紧跟；'
            'v4.2-D16 补【解析】简析行（简析由题干答案自明，自拟一句亲算句：m·n=0 展开得 λ=−3/2）')
    p1_, p2_, p3_ = sanju_rows(SANJU[gnum])
    em(r'\xiaojie{' + p1_ + '}')
    em(r'\bindp ' + p2_)
    em(r'\bindp ' + p3_)
log('5g-台账. 题源映射（拍板18 撤〔源〕括注，映射留台账）：探究点一↔题1；二↔题2；三↔题3；四↔题4；五↔题5；'
    '六↔题6；七↔题7（变式1＝题8）；八↔题9；九↔题10——源题 10 题全在场（题量守恒），知识点N 侧挂见各题〔〕')
log('5g-台账. 知识点N 映射：题1→知识点一；题2、3→知识点二；题4～10→知识点三（按三列挖空表三块内容域归类）')
log('5g-补. 【点睛】：源题9、题10 含【点睛】，v3 漏排，v4 补排（内容零增删口径，登记）')

# —— 课堂检测（恒 5 题：3 单选＋2 填空带提示词，拍板35④；花形行栏内化，无 multicols 切分）——
# v4.2-21：第三花形名对齐全品 p07 实证＝「课堂评价」（非「课堂检测」），右侧＝「知识评价　素养形成」
# v4.2-⑦：花形行＋检测 5 题整体装 \vbox（box 不可切列）——末页 multicol 平衡断点原恰落花形线后，
# 标线悬空左栏底、题目全数右栏（实测 p6：标线 y=192.7mm 栏末无下级）；整节 vbox 后归位右栏顶，
# 花形线→检测1 缝回 ≤8mm 断言域。左栏末页留白参差收尾＝拍板23，⑤b 实测登记
em(r'\vbox{')
huaxing('课堂评价', '知识评价\\quad 素养形成')

def cebiao(nd, kn):
    # v4.2-A10：题侧 9.5pt→8pt midgray（层级＝粗黑题号＋8pt 灰括注＋10.5pt 题干）
    return r'{\fontsize{8pt}{11pt}\selectfont\color{midgray}〔' + nd + '（知识点' + kn + '）〕}'

# v4.2-D17：课堂检测 5 题各补【解析】简析行（8pt 黑，【答案】行下一行）——亲算文字逐题转写
DET_JX = {
    1: r'\(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos60^\circ=2\times3\times0.5=3\)．',
    2: r'\(\overrightarrow{b}=\lambda\overrightarrow{a}\Rightarrow4=2\lambda\Rightarrow\lambda=2\)，\(k=2\)，选 B．',
    3: r'非零向量 \(\overrightarrow{a}\cdot\overrightarrow{b}=0\Leftrightarrow\overrightarrow{a}\perp\overrightarrow{b}\)，充要条件，选 C．',
    4: r'取 \(AC\) 中点 \(G\)，\(\overrightarrow{EF}=\overrightarrow{EG}+\overrightarrow{GF}=\frac{1}{2}\overrightarrow{BC}+\frac{1}{2}\overrightarrow{AD}\)，选 D．',
    5: r'\(\overrightarrow{a}\cdot\overrightarrow{b}=4\times3\times\cos120^\circ=-6\)，\(|\overrightarrow{a}+\overrightarrow{b}|^2=16+9-12=13\)，故 \(\sqrt{13}\)．',
}
for g, jx in DET_JX.items():
    COMPOSED.append(jx)

# v4.2-G20：检测题号加粗（全品实证检测题号 1. 2. 3. 粗黑）＝postproc 输出 {\heiti N．}
em(r'\jiancestem{{\heiti 1．}' + cebiao('简单', '三')
   + r'已知 \(|\overrightarrow{a}|=2\)，\(|\overrightarrow{b}|=3\)，\(\langle\overrightarrow{a},\overrightarrow{b}\rangle=60^\circ\)，'
     r'则 \(\overrightarrow{a}\cdot\overrightarrow{b}=\)\kongbai{}．'
     r'{\zhuzhu{（提示：\(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle\)）}}}')
em(r'\ansline{\ansul{3}}')
em(r'\jiexi{' + DET_JX[1] + '}')
COMPOSED.append(r'（提示：\(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle\)）')
log('5h. 检测1＝沿用 v3 已亲算（数量积定义求值，答案 3），本轮按 35④ 追加提示词（演示性增补，登记）；v4.2-D17 补【解析】简析行')

jc2_stem = (r'设 \(\overrightarrow{e_1}\)，\(\overrightarrow{e_2}\) 不共线，\(\overrightarrow{a}=2\overrightarrow{e_1}+\overrightarrow{e_2}\)，'
            r'\(\overrightarrow{b}=4\overrightarrow{e_1}+k\overrightarrow{e_2}\)，若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，则 \(k=\)（~~~~）')
jc2_opts = r'A．\(\frac{1}{2}\)；B．\(2\)；C．\(-\frac{1}{2}\)；D．\(3\)'
em(r'\jiancestem{{\heiti 2．}' + cebiao('简单', '二') + jc2_stem + '}')
emit_blocks([jc2_opts])
em(r'\ansline{\ansul{B}}')
em(r'\jiexi{' + DET_JX[2] + '}')
COMPOSED.append(jc2_stem); COMPOSED.append(jc2_opts)
log('5h. 检测2（单选）＝本轮新命制（亲算：b=λa ⇒ 4=2λ ⇒ λ=2，k=2×1=2，选 B）；共线定理定量应用；v4.2-D17 补【解析】简析行')

jc3_stem = (r'设 \(\overrightarrow{a}\)，\(\overrightarrow{b}\) 均为非零空间向量，则“\(\overrightarrow{a}\cdot\overrightarrow{b}=0\)”'
            r'是“\(\overrightarrow{a}\perp\overrightarrow{b}\)”的（~~~~）')
jc3_opts = r'A．充分不必要条件；B．必要不充分条件；C．充要条件；D．既不充分也不必要条件'
em(r'\jiancestem{{\heiti 3．}' + cebiao('简单', '三') + jc3_stem + '}')
emit_blocks([jc3_opts])
em(r'\ansline{\ansul{C}}')
em(r'\jiexi{' + DET_JX[3] + '}')
COMPOSED.append(jc3_stem); COMPOSED.append(jc3_opts)
log('5h. 检测3（单选）＝本轮新命制（亲算：两向量均非零时 a·b=0 ⇔ a⊥b，充要，选 C）；数量积与垂直（充要条件为必修前序知识，不超纲）；v4.2-D17 补【解析】简析行')

jc4_stem = (r'在空间四边形 \(ABCD\) 中，\(E\)，\(F\) 分别为 \(AB\)，\(CD\) 的中点，'
            r'则 \(\frac{1}{2}(\overrightarrow{AD}+\overrightarrow{BC})=\)（~~~~）')
jc4_opts = r'A．\(2\overrightarrow{EF}\)；B．\(-\overrightarrow{EF}\)；C．\(\overrightarrow{FE}\)；D．\(\overrightarrow{EF}\)'
em(r'\jiancestem{{\heiti 4．}' + cebiao('简单', '二') + jc4_stem + '}')
emit_blocks([jc4_opts])
em(r'\ansline{\ansul{D}}')
em(r'\jiexi{' + DET_JX[4] + '}')
COMPOSED.append(jc4_stem); COMPOSED.append(jc4_opts)
log(r'5h. 检测4（单选）＝本轮新命制（亲算：\(\overrightarrow{EF}=\frac{1}{2}(\overrightarrow{AD}+\overrightarrow{BC})\)，选 D）；中点向量恒等式（线性运算）；v4.2-D17 补【解析】简析行')

jc5_stem = (r'已知 \(|\overrightarrow{a}|=4\)，\(|\overrightarrow{b}|=3\)，\(\langle\overrightarrow{a},\overrightarrow{b}\rangle=120^\circ\)，'
            r'则 \(|\overrightarrow{a}+\overrightarrow{b}|=\)\kongbai{}．'
            r'{\zhuzhu{（提示：先算 \(\overrightarrow{a}\cdot\overrightarrow{b}\)，再对 \(|\overrightarrow{a}+\overrightarrow{b}|^2=(\overrightarrow{a}+\overrightarrow{b})^2\) 展开）}}')
em(r'\jiance{' + r'{\heiti 5．}' + cebiao('简单', '三') + jc5_stem + '}' + r'{\ansul{\(\sqrt{13}\)}}')
em(r'\jiexi{' + DET_JX[5] + '}')
em(r'}')
COMPOSED.append(jc5_stem)
log('5h. 检测5（填空带提示词）＝本轮新命制（亲算：a·b=12×cos120°=−6；|a+b|²=16−12+9=13，故 √13）；模长平方展开；v4.2-D17 补【解析】简析行')
log('5h-小结. 课堂检测恒 5 题＝3 单选（检测2/3/4）＋2 填空带提示词（检测1/5），难度均〔简单〕≤例题（拍板35④）；'
    '题侧均挂〔难度（知识点N）〕，题答紧跟（拍板12）；'
    'v4.2-⑦：花形行＋检测 5 题整体 \\vbox 装栏（防「课堂评价」标线悬空栏底——multicol 平衡断点切列无视段间 penalty，实测登记）')

em(LAN_CLOSE)

# ---- 6. 巨型公式断点（同 v2/v3）＋分号守恒＋控制字符扫描＋输出 ----
body_text = '\n\n'.join(body)
n_ab = body_text.count(' = \\left') + body_text.count(' \\cdot \\left')
body_text = body_text.replace(' = \\left', ' = \\allowbreak\\left')
body_text = body_text.replace(' \\cdot \\left', ' \\cdot \\allowbreak\\left')
log(f'6. 巨型行内公式显式断点：顶层 = 与 · 后注入 \\allowbreak ×{n_ab}（同 v2 11b，详解C 溯源链）')

# ---- 6b. 分号守恒对账（拍板21；片段级，剥 \allowbreak 注入与空白差） ----
def _norm(s):
    return re.sub(r'\s+', '', s).replace(r'\allowbreak', '')
body_n = _norm(body_text)
fh_tongshi = fh_unprint = fh_verbatim = 0
fh_miss = []
for b in blocks:
    n = b.count('；')
    if n == 0:
        continue
    if b.startswith('【编注】') and '题型通式' in b:
        fh_tongshi += n          # 授权转换：通式编注→素养小结三句式（v3 登记沿用）
        continue
    frag = _norm(b[len('【编注】'):]) if b.startswith('【编注】') else _norm(b)
    if frag.startswith('A．') and '；' in frag:
        pieces = [_norm(p) for p in re.split(r'；(?=[A-D]．)', b) if _norm(p)]
        if all(p in body_n for p in pieces):
            fh_verbatim += n
        else:
            fh_miss.append((n, b[:40]))
        continue
    if frag in body_n:
        fh_verbatim += n
    else:
        fh_miss.append((n, b[:40]))
fh_unprint = sum(n for n, _ in fh_miss)   # 未排印块（讲部表×2＋条目7（2）选编，登记）
n_comp_fh = sum(s.count('；') for s in COMPOSED)
n_body_fh = body_text.count('；')
log(f'6b. 分号守恒对账（拍板21，片段级）：源节 {n_sec_fh} ＝ 逐字在场 {fh_verbatim}（选项网格拆分回填含内）'
    f'＋通式编注→三句式授权转换 {fh_tongshi}（v3 登记沿用）＋未排印块 {fh_unprint}（讲部表×2＋条目7（2）选编，其内容由条目7 自编性质句覆盖）；'
    f'成件 body 共 {n_body_fh} ＝ 源逐字 {fh_verbatim}＋命制/演示自编 {n_body_fh - fh_verbatim}（对账 COMPOSED 计 {n_comp_fh}，余为条目/学习目标自编句）')
assert fh_unprint <= 3, f'分号对账异常：{fh_miss}'
ctrl = re.findall(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', body_text)
assert not ctrl, f'控制字符污染：{ctrl[:5]}'
log('6c. 控制字符扫描兜底（v3 交付报告§七-4）：0 处')
open(BASE + r'\body.tex', 'w', encoding='utf-8').write(body_text + '\n')
head = [
    r'\zhangtitle{第一章\quad 空间向量与立体几何}',
    r'\jietitle{1.1 空间向量及其运算}',
    r'\xiaojietitle{1.1.1 空间向量及其运算}',
    r'\keshi{第1课时\quad 空间向量的概念及线性运算}',
    r'\mubiaoline',
    r'\mubiaomu{1}{理解空间向量及其相关概念（模、零向量、单位向量、相等与相反、共线与共面），会用有向线段表示空间向量；}',
    r'\mubiaomu{2}{掌握线性运算（加减、数乘）的法则与运算律，理解共线、共面的充要条件；}',
    r'\mubiaomu{3}{掌握数量积的概念与运算律，会求夹角、投影向量，并能用数量积求距离．}',
]
COMPOSED.extend(h[1:].rstrip('；') for h in head[4:])
open(BASE + r'\chapterhead.tex', 'w', encoding='utf-8').write('\n'.join(head) + '\n')
log('7. 章首通栏：章22（v4.1 指令7 全品式左对齐＝两个错位交叠灰方块 DDDDDD＋777777＋章名黑体左排，「第1章」改「第一章」；'
    '节/小节/课时维持居中）/节18（行高22）/小节15/课时14（章首间距 4+4pt）；'
    'v4.2-5：课时名内容式对齐全品 p04 实证＝「第1课时　空间向量的概念及线性运算」（原「空间向量及其运算」撤）；'
    'v4.2-2：章/节/小节/课时四级标题换 \\heibf 仿粗黑（FakeBold=2.2，全品标题加重实证，正文【】标签与◆标题维持 \\heiti/\\bfseries 不动）；'
    '【学习目标】3 条楷体化压缩（拍板28，演示文案压缩登记）；'
    '讲练件的统计行与 T0 导航表不排入导学件（件型差异，登记）')

# ---- 8. 逻辑断言自检（复测波脚本手工版的数据面） ----
n_tj = body_text.count(r'\tjdnr{')
n_li1 = body_text.count('{例1}')
n_bs = body_text.count('{变式1}')
n_ans = body_text.count(r'\ansline{') + body_text.count(r'\jiance{')
n_star = body_text.count('典型性理由：')
n_kd = body_text.count(r'\kongda{')
n_kb_stem = body_text.count(r'\kongbai{}')
n_zt = body_text.count(r'\zhenti{')
n_jx = body_text.count(r'\jiexi{')
n_mini = body_text.count(r'\begin{minipage}')
n_hao_bold = len(re.findall(r'\{\\heiti \d．\}', body_text))
n_side = body_text.count(r'\begin{minipage}[t]{0.56\linewidth}')
xuankong = [w for w in ('见例', '如下例') if w in body_text] + \
    ([r'衔接\d'] if re.search(r'衔接\d', body_text) else [])
cg_hits = [w for w in ('基本定理', '空间直角') if w in body_text]
cg_zuobiao = [m.group(0) for m in re.finditer(r'.{6}坐标.{6}', body_text)
              if '不建坐标系' not in m.group(0) and '非坐标' not in m.group(0)]   # 否定式表述非坐标法使用
log(f'8. 逻辑断言自检（数据面）：◆探究点 {n_tj}/9；例1 {n_li1}/9；变式1 {n_bs}/9；【答案】行 {n_ans}/14；'
    f'★典型性理由 {n_star}/0（v4.2-E18 撤★）；【解析】简析 \\jiexi {n_jx}/14（变式9＋检测5，D 类16/17）；'
    f'图文并排 minipage {n_mini}（{n_side} 组题干并排，左 0.56/右 0.40）；'
    f'挖空印答 \\kongda {n_kd}/20（课前预习知识点区全部空，答案逐个核对条目语义）；'
    f'题干留白 \\kongbai {n_kb_stem}（例题/变式/课堂检测，答案由【答案】/【详解】紧跟）；'
    f'判断题 \\zhenti {n_zt}/6（第 4 参【解析】由宏排印，字面在 qp-blocks）；'
    f'检测题号加粗 {{\\heiti N．}} {n_hao_bold}/5（G20）；悬空引用 {xuankong or "无"}；'
    f'超纲禁词（基本定理/空间直角）{cg_hits or "无"}；'
    f'「坐标」非否定式命中 {cg_zuobiao or "无"}（命制/演示文字超纲复查＝0）')
assert n_kd == 20 and n_zt == 6, f'v4.1 印答/解析计数异常：kongda={n_kd} zhenti={n_zt}'
assert n_star == 0 and n_jx == 14 and n_side == 4 and n_hao_bold == 5, \
    f'v4.2 撤★/解析/并排/题号加粗计数异常：star={n_star} jiexi={n_jx} side={n_side} haobold={n_hao_bold}（返修2 后并排 4 组）'
log('8b. 命制对账：本轮新命制 14（变式 8＋检测 4＋诊断 2）≤上限 15，逐题亲算（见 5g/5h 各条）；'
    '沿用 v3 已亲算 5（检测1＋诊断块①2 道＋块②③第 1 道），逐条登记；'
    '变式六策覆盖：逆向化/概念辨析化/换载体/换设问/换数值/换条件')
log('8c. v4.2 图定性处置台账（A6＋返修2，全件 6 图）：sub3_B_4＝条目3 投影三联图 45mm 居中不动；'
    'image1（探究点二例1 详解内）＝返修2 居中 40mm→题干 minipage 并排（与探三/六/八同款）；'
    'image5（探究点九例1 详解内）＝居中独立行 30→40mm 提档；'
    'image2（探究点三例1 题干图）／image3（探究点六例1 题干图）／image4（探究点八例1 题干图）＝题干 minipage 并排 '
    '（左 0.56\\linewidth 题干文字／右 0.40\\linewidth 图≈34mm——30mm 档提档，全品 p06 变式版式实证）')
open(BASE + r'\postproc_daoxue_log.txt', 'w', encoding='utf-8').write('\n'.join(LOG))
print('\n'.join(LOG))
