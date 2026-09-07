# -*- coding: utf-8 -*-
r"""v4 导学件后处理器：sec.tex（pandoc 原始输出）→ chapterhead.tex + body.tex + postproc_daoxue_log.txt。
v4 改版轮（依据＝总诊断-v4参数表＋导学件对照§四 11 条＋拍板 16/18/21/22/25/27/28/34/35）。
结构：章首通栏（章22/节18/小节15/课时14＋章首灰方块）→【学习目标】×3（楷体化压缩，通栏区）
→ 花形行「课前预习」（通栏）→ ◆知识点×3（条目挖空＋编注段末并排＋三列挖空表；每知识点后紧跟【诊断分析】一块×2 题）
→ 花形行「课中探究」（通栏）→ ◆探究点×9（恒式＝例1＋变式1＋素养小结；◆标题与例1 同段内联）
→ 花形行「课堂检测」（通栏）→ 检测×5（3 单选＋2 填空带提示词）。一切题题后紧跟答案（拍板12）。
题侧＝〔难度（知识点N）〕（拍板15/18，撤〔源〕括注）；★精选标×3 附典型性理由（拍板25）。
题源分配（拍板16 源题优先）：例1×9＝各组第 1 题（题1～7、9、10）；变式1：探究点七＝源题8（池尽前优先池配），
其余 8 点按变式六策命制（逐题亲算，策名逐条登记）；源题 10 题全在场（题量守恒）。
命制登记：本轮新命制 14（变式8＋检测4＋诊断2）≤上限 15；沿用 v3 已亲算 5（检测1＋诊断4），逐条登记。
花形行通栏化＝multicols 切分法（body.tex 内 \end/\begin multicols）。
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
log(f'1. 源清洗：去 U+2060、\\overset{{⃑}}{{}}→\\overrightarrow{{}}（同 v2/v3）；长下划线→\\kongbai ×{n_kong}（15mm 留白线）；'
    f'源节分号计数（清洗后）＝{n_sec_fh}')

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

# ---- 3. 图分档（默认 30mm）＋独立图 7mm 起排 wrapper（同 v2/v3） ----
FIG = {'sub3_B_4.png': '45mm', 'image1.png': '30mm', 'image2.png': '30mm',
       'image3.png': '30mm', 'image4.png': '30mm', 'image5.png': '30mm'}
FIGRE = re.compile(r'\\includegraphics\[(width=[\d.]+in,height=[\d.]+in)(,alt=\{[^}]*\})?\]\{([^}]+)\}')
figs_seen = []

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
            w = FIG.get(name)
            assert w, f'{tag}: {name} 未分档'
            figs_seen.append((name, w, tag))
            tok = mm.group(0).replace(mm.group(1), 'width=' + w)
            out.append(r'\penalty10000\noindent\hangindent=0pt\hangafter=1\hspace*{7mm}'
                       r'\makebox[\dimexpr\linewidth-7mm\relax][c]{' + tok + r'}\par\penalty10000')
            last = mm.end()
        if b[last:].strip():
            out.append(b[last:].strip())
    return out

# ---- 3b. 选项网格（拍板21：极短 4 项/行、短 2 项/行、长 1 行/项；分号字符全保留） ----
COMPOSED = []   # 命制/演示文字流（分号守恒对账用）

def opt_len(s):
    t = re.sub(r'\\[a-zA-Z]+', '', s)
    t = re.sub(r'[\\{}$&%]', '', t)
    return sum(1.0 if ord(ch) > 0x2E7F else 0.55 for ch in t)

def grid_lines(s):
    """A．…；B．…；C．…；D．… → 槽位网格行；分号原样保留（拆分后逐一回填）。"""
    parts = re.split(r'；(?=\s*[A-D]．)', s)
    if len(parts) == 1:
        return [r'\bindopt ' + s]
    opts = [p.strip() for p in parts if p.strip()]
    for i in range(len(opts) - 1):
        if not opts[i].endswith('；'):
            opts[i] += '；'
    lens = [opt_len(o) + 1.5 for o in opts]
    mx, n = max(lens), len(opts)
    per = 4 if (n == 4 and mx <= 2.8) else (2 if mx <= 6.5 else 1)
    rows = []
    for i in range(0, len(opts), per):
        row = opts[i:i + per]
        if len(row) == 1:
            rows.append(r'\bindopt ' + row[0])
        else:
            slot = r'0.25\linewidth-0.5em' if per == 4 else r'0.5\linewidth-1em'
            rows.append(r'\bindopt ' + ''.join(
                r'\makebox[\dimexpr' + slot + r'\relax][l]{' + o + '}' for o in row))
    log(f'3b. 选项网格：{n} 项 {per} 项/行（最长估 {mx:.1f} 字档）')
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

# ---- 4. 挖空遮蔽（原词登记）＋ 三列表生成 ----
n_kb = [0]
def kb(word):
    n_kb[0] += 1
    log(f'4. 挖空遮蔽 #{n_kb[0]}：原词「{word}」→ \\kongbai{{}}（15mm 留白线）')
    return r'\kongbai{}'

TABW = ('16', '34', '22')
n_tab = [0]
def kbtable(h1, h2, h3, rows):
    n_tab[0] += 1
    head = ' & '.join(r'\multicolumn{1}{|>{\centering\arraybackslash}p{' + w + 'mm}|}{\\textbf{' + c + '}}'
                      for c, w in zip((h1, h2, h3), TABW))
    lines = [r'\noindent\hspace*{7mm}\begin{tabular}{|>{\raggedright\arraybackslash}p{' + TABW[0] +
             r'mm}|>{\raggedright\arraybackslash}p{' + TABW[1] +
             r'mm}|>{\raggedright\arraybackslash}p{' + TABW[2] + r'mm}|}', r'\hline', head + r' \\', r'\hline']
    for r in rows:
        lines.append(' & '.join(r) + r' \\ \hline')
    lines.append(r'\end{tabular}\par')
    body.append('\n'.join(lines))
    log(f'4b. 三列挖空表 #{n_tab[0]}：白底黑体表头＋全框 0.4pt 细线（arraystretch 1.15），'
        f'{len(rows)} 行（cells 选编自源讲部表，挖空见 #4 登记）')

# ---- 5. 组装正文 ----
body = []
em = body.append
LAN_OPEN = '\\begin{multicols}{2}\n\\emergencystretch=8em'
LAN_CLOSE = '\\end{multicols}'

def huaxing(k, xiao):
    em(r'\huaxing{' + k + '}{' + xiao + '}')
    COMPOSED.append(k + xiao)

# 学习目标（楷体化压缩，通栏区——见 chapterhead 组装段 7）
log('5a. 【学习目标】3 条＝演示编写（v3 文案压缩：条目压至 ≤1 行/条，三条要点全保留），楷体排印（拍板28），移入章首通栏区（防 multicols 短栏平衡），登记')

huaxing('课前预习', '预习自查\\quad 温故知新')
log('5b. 花形行×3＝白底黑边圆角字块（tcolorbox 近似花形）＋黑底线＋右侧灰小字；小字自拟非全品文案；'
    '本版为通栏行（multicols 切分法，拍板28；v3 栏内实现差异撤）。')
em(LAN_OPEN)

# —— ◆知识点一（诊断块①）——
em(r'\zsd{一}{空间向量的概念}')
em(r'\tiaomu{1}{定义：在空间，我们把具有' + kb('大小') + '和' + kb('方向') + r'的量叫做空间向量．'
   r'\zhuzhu{' + entries[1]['note'] + '}}')
em(r'\tiaomu{2}{（1）字母表示法：用字母 \(\overrightarrow{a},\overrightarrow{b},\overrightarrow{c},\cdots\) 表示．'
   r'（2）几何表示法：用有向线段表示，其' + kb('长度') + r'表示空间向量的模．即若向量 \(\overrightarrow{a}\) 的起点是 \(A\)、终点是 \(B\)，'
   r'则向量 \(\overrightarrow{a}\) 也可记作 \(\overrightarrow{AB}\)，其模记为 \(\left| \overrightarrow{AB} \right|\)．'
   r'\zhuzhu{' + entries[2]['note'] + '}}')
em(r'\tiaomu{3}{几类特殊向量（见下表）；规定：' + kb('零') + r'向量与任意向量平行．即对任意向量 \(\overrightarrow{a}\)，'
   r'都有 \(\overrightarrow{0}\parallel\overrightarrow{a}\)．\zhuzhu{' + entries[3]['note'] + '}}')
kbtable('名称', '定义', '表示', [
    [r'零向量', r'长度为' + kb('0') + r'的向量叫做零向量', r'记作' + kb('0')],
    [r'单位向量', r'模等于' + kb('1') + r'的向量', r'用 \(e\) 表示，\(|e|=1\)'],
    [r'相反向量', r'与 \(\overrightarrow{a}\) 长度相同而方向' + kb('相反') + r'的向量', r'记作 \(-\overrightarrow{a}\)'],
    [r'共线向量或平行向量', r'表示若干空间向量的有向线段所在的直线' + kb('互相平行') + r'或' + kb('重合'), r'记作 \(\overrightarrow{a}\parallel\overrightarrow{b}\)'],
    [r'相等向量', r'方向相同且' + kb('模相等') + r'的向量', r'记作 \(\overrightarrow{a}=\overrightarrow{b}\)'],
])
log('5c. 知识点一：条目 1～3 选编＋挖空；编注以 \\zhuzhu 并入条目段末同段接排（独立段数 0，字符总量不变，对照§四-7）；'
    '三列挖空表 cells 选编自源讲部「特殊向量」表')
em(r'\zhenhead{判断正误（正确的打“√”，错误的打“×”）}')
for i, (t, a) in enumerate([
    (r'两个空间向量的模相等，则这两个向量相等．', '×'),
    (r'相等向量一定是共线向量．', '√'),
], 1):
    em(r'\zhenti{（' + '一二三四五六'[i-1] + '）}{' + t + '}{\\ansul{' + a + '}}')
    COMPOSED.append(t)
log('5c′. 【诊断分析】块①（知识点一后紧跟，拍板35⑤）＝2 道：沿用 v3 已亲算 2 道（模相等⇒相等×；相等⇒共线√），本轮零新命制')

# —— ◆知识点二（诊断块②）——
em(r'\zsd{二}{空间向量的线性运算}')
em(r'\tiaomu{4}{加法可按' + kb('三角形') + r'法则或' + kb('平行四边形') + r'法则作出；减法 \(\overrightarrow{a}-\overrightarrow{b}\) '
   r'为减向量终点指向被减向量终点；数乘 \(\lambda\overrightarrow{a}\)：当 \(\lambda>0\) 时与 \(\overrightarrow{a}\) 方向' + kb('相同') +
   r'，当 \(\lambda<0\) 时方向' + kb('相反') + r'，当 \(\lambda=0\) 时 \(\lambda\overrightarrow{a}=\overrightarrow{0}\)．'
   r'\zhuzhu{' + entries[4]['note'] + '}}')
em(r'\tiaomu{5}{共线的充要条件：对任意两个空间向量 \(\overrightarrow{a},\overrightarrow{b}\)（\(\overrightarrow{b}\neq\overrightarrow{0}\)），'
   r'\(\overrightarrow{a}\parallel\overrightarrow{b}\) 的充要条件是存在' + kb('实数') +
   r' \(\lambda\)，使 \(\overrightarrow{a}=\lambda\overrightarrow{b}\)．\zhuzhu{' + entries[5]['note'] + '}}')
kbtable('运算', '法则要点', '运算律举例', [
    [r'加法', r'三角形法则／平行四边形法则（与平面向量一致）', r'\(\overrightarrow{a}+\overrightarrow{b}=\overrightarrow{b}+\overrightarrow{a}\)'],
    [r'减法', r'减向量终点指向被减向量终点', r'\((\overrightarrow{a}+\overrightarrow{b})+\overrightarrow{c}=\overrightarrow{a}+(\overrightarrow{b}+\overrightarrow{c})\)'],
    [r'数乘', r'实数 \(\lambda\) 与向量 \(\overrightarrow{a}\) 的乘积仍为向量', r'\((\lambda+\mu)\overrightarrow{a}=\lambda\overrightarrow{a}+\mu\overrightarrow{a}\)'],
    [r'共线', r'\(\overrightarrow{a}\parallel\overrightarrow{b}\)（\(\overrightarrow{b}\neq\overrightarrow{0}\)）', r'\(\overrightarrow{a}=\lambda\overrightarrow{b}\)'],
])
log('5d. 知识点二：条目 4～5 选编＋挖空＋编注并段；三列挖空表 cells 选编自源讲部「加法／运算律」表')
em(r'\zhenhead{判断正误（正确的打“√”，错误的打“×”）}')
em(r'\zhenti{（一）}{若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，\(\overrightarrow{b}\parallel\overrightarrow{c}\)，则 \(\overrightarrow{a}\parallel\overrightarrow{c}\)．}{\ansul{×}}')
em(r'\zhenti{（二）}{若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，则存在唯一实数 \(\lambda\)，使 \(\overrightarrow{a}=\lambda\overrightarrow{b}\)．}{\ansul{×}}')
COMPOSED.append(r'若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，\(\overrightarrow{b}\parallel\overrightarrow{c}\)，则 \(\overrightarrow{a}\parallel\overrightarrow{c}\)．')
COMPOSED.append(r'若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，则存在唯一实数 \(\lambda\)，使 \(\overrightarrow{a}=\lambda\overrightarrow{b}\)．')
log('5d′. 【诊断分析】块②＝2 道：第 1 道沿用 v3 已亲算（平行传递×，b=0 反例）；'
    r'第 2 道本轮新命制（亲算：\(\overrightarrow{b}=\overrightarrow{0}\) 时前提失效、\(\overrightarrow{a}=\overrightarrow{0}\) 时 λ 不唯一，故×），共线充要条件前提辨析')

# —— ◆知识点三（诊断块③）——
em(r'\zsd{三}{空间向量的夹角、数量积与共面}')
em(r'\tiaomu{6}{夹角：已知两个非零向量 \(\overrightarrow{a},\overrightarrow{b}\)，在空间中任取一点 \(O\)，'
   r'作 \(\overrightarrow{OA}=\overrightarrow{a},\overrightarrow{OB}=\overrightarrow{b}\)，则大小在' + kb('[0°,180°]') +
   r'内的 \(\angle AOB\) 称为 \(\overrightarrow{a}\) 与 \(\overrightarrow{b}\) 的夹角，记作 \(\langle\overrightarrow{a},\overrightarrow{b}\rangle\)；'
   r'当 \(\langle\overrightarrow{a},\overrightarrow{b}\rangle=\frac{\pi}{2}\) 时，称 \(\overrightarrow{a}\) 与 \(\overrightarrow{b}\)' +
   kb('互相垂直') + r'，记作 \(\overrightarrow{a}\perp\overrightarrow{b}\)．\zhuzhu{' + entries[6]['note'] + '}}')
weiti = next((s for s in entries[7]['blocks'] if s.startswith('【微提醒】')), '')
em(r'\tiaomu{7}{数量积：定义 \(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle\)；'
   '规定' + kb('零向量') + r'与任意向量的数量积为 0．'
   r'性质：\(\overrightarrow{a}\perp\overrightarrow{b}\Leftrightarrow\overrightarrow{a}\cdot\overrightarrow{b}=0\)；'
   r'\(\overrightarrow{a}\cdot\overrightarrow{a}={{\overrightarrow{a}}^{2}}={\left| \overrightarrow{a} \right|}^{2}\)；'
   r'\(\left| \overrightarrow{a}\cdot\overrightarrow{b} \right|\leq\left| \overrightarrow{a} \right|\left| \overrightarrow{b} \right|\)．'
   + (r'\zhuzhu{' + weiti + '}' if weiti else '') +
   r'\zhuzhu{' + entries[7]['note'] + '}}')
blk8 = list(entries[8]['blocks'])
blk8[0] = blk8[0] + r'\zhuzhu{' + entries[8]['note'] + '}'   # 条目8 编注并入首段段末（v3 漏排，v4 补排）
emit_blocks(reflow(blk8, '知识点三'))
log('5e. 知识点三：条目 6～7 选编＋挖空＋编注并段（微提醒同段并排）；条目 8「投影向量」整段源文排印（含投影三联图 45mm 独立居中，编注并入首段段末——v3 漏排，v4 补排登记）；条目 7 源（2）块内容已由条目 7 自编性质句全量覆盖（选编授权，源块不另排）')
em(r'\tiaomu{9}{共面的充要条件：向量 \(\overrightarrow{p}\) 与不共线向量 \(\overrightarrow{a},\overrightarrow{b}\) 共面的充要条件是存在' +
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
])
em(r'\zhenhead{判断正误（正确的打“√”，错误的打“×”）}')
em(r'\zhenti{（一）}{若 \(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\)（\(\overrightarrow{a}\)，\(\overrightarrow{b}\) 不共线），则 \(\overrightarrow{p}\)，\(\overrightarrow{a}\)，\(\overrightarrow{b}\) 共面．}{\ansul{√}}')
em(r'\zhenti{（二）}{两个非零空间向量的数量积大于 \(0\)，则这两个向量的夹角为锐角．}{\ansul{×}}')
COMPOSED.append(r'若 \(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\)（\(\overrightarrow{a}\)，\(\overrightarrow{b}\) 不共线），则 \(\overrightarrow{p}\)，\(\overrightarrow{a}\)，\(\overrightarrow{b}\) 共面．')
COMPOSED.append(r'两个非零空间向量的数量积大于 \(0\)，则这两个向量的夹角为锐角．')
log('5e′. 【诊断分析】块③＝2 道：第 1 道沿用 v3 已亲算（共面表示√）；'
    r'第 2 道本轮新命制（亲算：取 \(\overrightarrow{a}=2\overrightarrow{b}\) 同向得数量积 \(>0\) 而夹角 \(0^\circ\) 非锐角，故×），夹角范围辨析')

# —— 课中探究（探究点×9 恒式）——
em(LAN_CLOSE)
huaxing('课中探究', '例变探究\\quad 素养提升')
em(LAN_OPEN)

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
CN = '一二三四五六七八九'
KN = {2: '一', 3: '二', 4: '二', 5: '三', 6: '三', 7: '三', 8: '三', 9: '三', 10: '三'}   # 组号→知识点块序
STAR = {
    1: r'典型性理由：模、方向、零向量、单位向量、相反向量五类概念一题尽扫，概念辨析母题',
    7: r'典型性理由：数量积条件翻译成不等式再剔除共线解，条件求参高考高频母题',
    9: r'典型性理由：折叠背景下向量链平方展开求距离，方法可迁移到任意折叠距离问题',
}
for g, why in STAR.items():
    COMPOSED.append(why)
log('5f-0. ★精选标×3（拍板25，与难度正交；典型性理由题侧 6.5pt 灰排印＝在场，同一灰档 777777）：'
    '探究点一例1（概念母题）、探究点七例1（求参母题）、探究点九例1（折叠距离方法母题）')

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

GRP_KS = {}
for (gn, k) in tis:
    GRP_KS.setdefault(gn, []).append(k)
for gn in GRP_KS:
    GRP_KS[gn].sort()

for gi, gname in enumerate(grp_order, 1):
    gnum = int(re.match(r'1\.1\.1\.(\d+)', gname).group(1))
    kn = KN[gnum]
    d = tis[(gnum, GRP_KS[gnum][0])]   # 各组第 1 题＝X-1（组2→题1…组8→题7；组8 双题后组9→题9、组10→题10）
    em(r'\tjdnr{' + CN[gi-1] + '｜' + gname.split(' ', 1)[1] + '}{例1}{' + d['nanidu'] + '（知识点' + kn + '）}{'
       + (r'\starblk{' + STAR[gi] + '}' if gi in STAR else '') + '}{' + d['stem'][0] + '}')
    emit_blocks(reflow(d['stem'][1:], f'例{gi}'))
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
        log(f'5g. 探究点{CN[gi-1]}：例1＝{d["num"]}（{d["nanidu"]}，源题原样，【分析】【详解】紧跟'
            + ('＋【点睛】' if d['dj'] else '') + '）；变式1＝新命制（' + v['ce'] + '，' + v['nd'] + '）；' + v['jc'])
    else:
        d8 = tis[(gnum, GRP_KS[gnum][1])]   # 组8 第 2 题＝题8（组内第 2 题按节内全局编号）
        em(r'\li{变式1}{' + d8['nanidu'] + '（知识点' + kn + '）}{}{' + d8['stem'][0] + '}')
        emit_blocks(reflow(d8['stem'][1:], f'变式{gi}'))
        em(r'\ansline{\ansul{' + d8['ans'] + '}}')
        log(f'5g. 探究点{CN[gi-1]}：例1＝{d["num"]}（{d["nanidu"]}，源题原样）；'
            f'变式1＝{d8["num"]}（{d8["nanidu"]}，源题池配——拍板16 源题优先，池尽方命制），仅排答案（下划线紧跟）')
    em(r'\xiaojie{' + SANJU[gnum] + '}')
log('5g-台账. 题源映射（拍板18 撤〔源〕括注，映射留台账）：探究点一↔题1；二↔题2；三↔题3；四↔题4；五↔题5；'
    '六↔题6；七↔题7（变式1＝题8）；八↔题9；九↔题10——源题 10 题全在场（题量守恒），知识点N 侧挂见各题〔〕')
log('5g-台账. 知识点N 映射：题1→知识点一；题2、3→知识点二；题4～10→知识点三（按三列挖空表三块内容域归类）')
log('5g-补. 【点睛】：源题9、题10 含【点睛】，v3 漏排，v4 补排（内容零增删口径，登记）')

# —— 课堂检测（恒 5 题：3 单选＋2 填空带提示词，拍板35④）——
em(LAN_CLOSE)
huaxing('课堂检测', '限时训练\\quad 当堂达标')
em(LAN_OPEN)

def cebiao(nd, kn):
    return r'{\fontsize{9.5pt}{13pt}\selectfont\color{midgray}〔' + nd + '（知识点' + kn + '）〕}'

em(r'\jiancestem{1．' + cebiao('简单', '三')
   + r'已知 \(|\overrightarrow{a}|=2\)，\(|\overrightarrow{b}|=3\)，\(\langle\overrightarrow{a},\overrightarrow{b}\rangle=60^\circ\)，'
     r'则 \(\overrightarrow{a}\cdot\overrightarrow{b}=\)\kongbai{}．'
     r'{\zhuzhu{（提示：\(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle\)）}}}')
em(r'\ansline{\ansul{3}}')
COMPOSED.append(r'（提示：\(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle\)）')
log('5h. 检测1＝沿用 v3 已亲算（数量积定义求值，答案 3），本轮按 35④ 追加提示词（演示性增补，登记）')

jc2_stem = (r'设 \(\overrightarrow{e_1}\)，\(\overrightarrow{e_2}\) 不共线，\(\overrightarrow{a}=2\overrightarrow{e_1}+\overrightarrow{e_2}\)，'
            r'\(\overrightarrow{b}=4\overrightarrow{e_1}+k\overrightarrow{e_2}\)，若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，则 \(k=\)（~~~~）')
jc2_opts = r'A．\(\frac{1}{2}\)；B．\(2\)；C．\(-\frac{1}{2}\)；D．\(3\)'
em(r'\jiancestem{2．' + cebiao('简单', '二') + jc2_stem + '}')
emit_blocks([jc2_opts])
em(r'\ansline{\ansul{B}}')
COMPOSED.append(jc2_stem); COMPOSED.append(jc2_opts)
log('5h. 检测2（单选）＝本轮新命制（亲算：b=λa ⇒ 4=2λ ⇒ λ=2，k=2×1=2，选 B）；共线定理定量应用')

jc3_stem = (r'设 \(\overrightarrow{a}\)，\(\overrightarrow{b}\) 均为非零空间向量，则“\(\overrightarrow{a}\cdot\overrightarrow{b}=0\)”'
            r'是“\(\overrightarrow{a}\perp\overrightarrow{b}\)”的（~~~~）')
jc3_opts = r'A．充分不必要条件；B．必要不充分条件；C．充要条件；D．既不充分也不必要条件'
em(r'\jiancestem{3．' + cebiao('简单', '三') + jc3_stem + '}')
emit_blocks([jc3_opts])
em(r'\ansline{\ansul{C}}')
COMPOSED.append(jc3_stem); COMPOSED.append(jc3_opts)
log('5h. 检测3（单选）＝本轮新命制（亲算：两向量均非零时 a·b=0 ⇔ a⊥b，充要，选 C）；数量积与垂直（充要条件为必修前序知识，不超纲）')

jc4_stem = (r'在空间四边形 \(ABCD\) 中，\(E\)，\(F\) 分别为 \(AB\)，\(CD\) 的中点，'
            r'则 \(\frac{1}{2}(\overrightarrow{AD}+\overrightarrow{BC})=\)（~~~~）')
jc4_opts = r'A．\(2\overrightarrow{EF}\)；B．\(-\overrightarrow{EF}\)；C．\(\overrightarrow{FE}\)；D．\(\overrightarrow{EF}\)'
em(r'\jiancestem{4．' + cebiao('简单', '二') + jc4_stem + '}')
emit_blocks([jc4_opts])
em(r'\ansline{\ansul{D}}')
COMPOSED.append(jc4_stem); COMPOSED.append(jc4_opts)
log(r'5h. 检测4（单选）＝本轮新命制（亲算：\(\overrightarrow{EF}=\frac{1}{2}(\overrightarrow{AD}+\overrightarrow{BC})\)，选 D）；中点向量恒等式（线性运算）')

jc5_stem = (r'已知 \(|\overrightarrow{a}|=4\)，\(|\overrightarrow{b}|=3\)，\(\langle\overrightarrow{a},\overrightarrow{b}\rangle=120^\circ\)，'
            r'则 \(|\overrightarrow{a}+\overrightarrow{b}|=\)\kongbai{}．'
            r'{\zhuzhu{（提示：先算 \(\overrightarrow{a}\cdot\overrightarrow{b}\)，再对 \(|\overrightarrow{a}+\overrightarrow{b}|^2=(\overrightarrow{a}+\overrightarrow{b})^2\) 展开）}}')
em(r'\jiance{5．' + cebiao('简单', '三') + jc5_stem + '}' + r'{\ansul{\(\sqrt{13}\)}}')
COMPOSED.append(jc5_stem)
log('5h. 检测5（填空带提示词）＝本轮新命制（亲算：a·b=12×cos120°=−6；|a+b|²=16−12+9=13，故 √13）；模长平方展开')
log('5h-小结. 课堂检测恒 5 题＝3 单选（检测2/3/4）＋2 填空带提示词（检测1/5），难度均〔简单〕≤例题（拍板35④）；'
    '题侧均挂〔难度（知识点N）〕，题答紧跟（拍板12）')

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
    r'\zhangtitle{第1章 空间向量与立体几何}',
    r'\jietitle{1.1 空间向量及其运算}',
    r'\xiaojietitle{1.1.1 空间向量及其运算}',
    r'\keshi{第1课时\quad 空间向量及其运算}',
    r'\mubiaoline',
    r'\mubiaomu{1}{理解空间向量及其相关概念（模、零向量、单位向量、相等与相反、共线与共面），会用有向线段表示空间向量；}',
    r'\mubiaomu{2}{掌握线性运算（加减、数乘）的法则与运算律，理解共线、共面的充要条件；}',
    r'\mubiaomu{3}{掌握数量积的概念与运算律，会求夹角、投影向量，并能用数量积求距离．}',
]
COMPOSED.extend(h[1:].rstrip('；') for h in head[4:])
open(BASE + r'\chapterhead.tex', 'w', encoding='utf-8').write('\n'.join(head) + '\n')
log('7. 章首通栏：章22（＋777777 实心灰方块 3.2mm，拍板22 演示近似）/节18（行高22）/小节15/课时14（章首间距 4+4pt）；'
    '【学习目标】3 条楷体化压缩（拍板28，演示文案压缩登记）；'
    '讲练件的统计行与 T0 导航表不排入导学件（件型差异，登记）')

# ---- 8. 逻辑断言自检（复测波脚本手工版的数据面） ----
n_tj = body_text.count(r'\tjdnr{')
n_li1 = body_text.count('{例1}')
n_bs = body_text.count('{变式1}')
n_ans = body_text.count(r'\ansline{') + body_text.count(r'\jiance{')
n_star = body_text.count('典型性理由：')
xuankong = [w for w in ('见例', '如下例') if w in body_text] + \
    ([r'衔接\d'] if re.search(r'衔接\d', body_text) else [])
cg_hits = [w for w in ('基本定理', '空间直角') if w in body_text]
cg_zuobiao = [m.group(0) for m in re.finditer(r'.{6}坐标.{6}', body_text)
              if '不建坐标系' not in m.group(0) and '非坐标' not in m.group(0)]   # 否定式表述非坐标法使用
log(f'8. 逻辑断言自检（数据面）：◆探究点 {n_tj}/9；例1 {n_li1}/9；变式1 {n_bs}/9；【答案】行 {n_ans}/14；'
    f'★典型性理由 {n_star}/3；悬空引用 {xuankong or "无"}；超纲禁词（基本定理/空间直角）{cg_hits or "无"}；'
    f'「坐标」非否定式命中 {cg_zuobiao or "无"}（命制/演示文字超纲复查＝0）')
log('8b. 命制对账：本轮新命制 14（变式 8＋检测 4＋诊断 2）≤上限 15，逐题亲算（见 5g/5h 各条）；'
    '沿用 v3 已亲算 5（检测1＋诊断块①2 道＋块②③第 1 道），逐条登记；'
    '变式六策覆盖：逆向化/概念辨析化/换载体/换设问/换数值/换条件')
open(BASE + r'\postproc_daoxue_log.txt', 'w', encoding='utf-8').write('\n'.join(LOG))
print('\n'.join(LOG))
