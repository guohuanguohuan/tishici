# -*- coding: utf-8 -*-
r"""v3 导学件后处理器：sec.tex（pandoc 原始输出）→ chapterhead.tex + body.tex + postproc_daoxue_log.txt。
高仿目标：全品导学案 p04/p08（已亲看）。结构：章首通栏（章22/节18/小节15/课时14）→【学习目标】×3
→ 课前预习花形行 → ◆知识点×3（条目挖空正文＋投影图30mm＋三列挖空表）→【诊断分析】判断正误×4
→ 课中探究花形行 → ◆探究点×9（例1带【分析】【详解】紧跟／变式答案紧跟／【素养小结】三句式后置）
→ 课堂检测花形行 → 检测题×2。一切题题后紧跟答案。
登记要点（详见 log 与交付报告）：讲部 5 张 longtable（1 对比表＋4 minipage 图文混排表）不排印，以 3 张自编三列挖空表替代；
条目重点词挖空＝演示性遮蔽（原词逐条登记）；
例1 分配 5 组＋变式 1（池子 10 题守恒，余 4 题让渡练习件）；通式编注移位改三句式；
【知识点】标签不排印；对比项表与统计行不排入。"""
import re

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v3\导学件"
LOG = []
log = LOG.append

tex = open(BASE + r"\sec.tex", encoding='utf-8').read()

# ---- 1. 源清洗（同 v2）：U+2060、箭头归一化、长下划线挖空 ----
tex = tex.replace('\u2060', '')
tex = tex.replace(r'\overset{⃑}{', r'\overrightarrow{')
n_kong = len(re.findall(r'(?:\\_){4,}', tex))
tex = re.sub(r'(?:\\_){4,}', r'\\kongbai{}', tex)
log(f'1. 源清洗：去 U+2060、\\overset{{⃑}}{{}}→\\overrightarrow{{}}（同 v2）；长下划线→\\kongbai ×{n_kong}（15mm 留白线）')

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
    'T0 导航表「题型组数 9」指题部组——v2 报告「探究点九组」与源节一致，无误')

# ---- 3. 图分档（默认 30mm）＋独立图 7mm 起排 wrapper（同 v2.1） ----
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
            out.append(r'\penalty10000\noindent\hspace*{7mm}'
                       r'\makebox[\dimexpr\linewidth-7mm\relax][c]{' + tok + r'}\par\penalty10000')
            last = mm.end()
        if b[last:].strip():
            out.append(b[last:].strip())
    return out

def emit_blocks(bs):
    """续块分类：选项/①链 → 2em 缩进绑定（对齐练习册 p06）；其余段前绑定。"""
    for s in bs:
        if s.startswith(('A．', 'B．', 'C．', 'D．', '①')):
            body.append(r'\bindopt ' + s)
        else:
            body.append(r'\bindp ' + s)

# ---- 4. 挖空遮蔽（原词登记）＋ 三列表生成 ----
n_kb = [0]
def kb(word):
    n_kb[0] += 1
    log(f'4. 挖空遮蔽 #{n_kb[0]}：原词「{word}」→ \\kongbai{{}}（15mm 留白线）')
    return r'\kongbai{}'

TABW = ('16', '34', '22')   # 三列挖空表列宽（合计 72mm；+7mm 起排 ≤79.25 ≤ 栏宽 86.25）
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
    log(f'4b. 三列挖空表 #{n_tab[0]}：白底黑体表头＋全框 0.4pt 细线，列宽 16/34/22mm，'
        f'{len(rows)} 行（cells 选编自源讲部表，挖空见 #4 登记）')

# ---- 5. 组装正文 ----
body = []
em = body.append
em(r'\mubiaoline')
for i, t in enumerate([
    r'理解空间向量的相关概念（模、零向量、单位向量、相等向量、共线与共面），会用有向线段表示空间向量；',
    r'掌握空间向量线性运算（加减、数乘）的法则与运算律，理解共线、共面的充要条件；',
    r'掌握空间向量数量积的概念、性质与运算律，会求两向量的夹角与投影向量，并能用数量积求距离．',
], 1):
    em(r'\mubiaomu{' + str(i) + '}{' + t + '}')
log('5a. 【学习目标】3 条＝演示编写（本节内容概览，非源节原文），登记')

em(r'\huaxing{课前预习}{预习自查\quad 温故知新}')
log('5b. 花形行：白底黑边圆角字块（tcolorbox 近似花形）＋深灰底线＋右侧灰小字；小字自拟，非全品文案')

# —— ◆知识点一 ——
em(r'\zsd{一}{空间向量的概念}')
em(r'\tiaomu{1}{定义：在空间，我们把具有' + kb('大小') + '和' + kb('方向') + r'的量叫做空间向量．}')
em(r'\zhuzhu{' + entries[1]['note'] + '}')
em(r'\tiaomu{2}{（1）字母表示法：用字母 \(\overrightarrow{a},\overrightarrow{b},\overrightarrow{c},\cdots\) 表示．'
   r'（2）几何表示法：用有向线段表示，其' + kb('长度') + r'表示空间向量的模．即若向量 \(\overrightarrow{a}\) 的起点是 \(A\)、终点是 \(B\)，'
   r'则向量 \(\overrightarrow{a}\) 也可记作 \(\overrightarrow{AB}\)，其模记为 \(\left| \overrightarrow{AB} \right|\)．}')
em(r'\zhuzhu{' + entries[2]['note'] + '}')
em(r'\tiaomu{3}{几类特殊向量（见下表）；规定：' + kb('零') + r'向量与任意向量平行．即对任意向量 \(\overrightarrow{a}\)，'
   r'都有 \(\overrightarrow{0}\parallel\overrightarrow{a}\)．}')
em(r'\zhuzhu{' + entries[3]['note'] + '}')
kbtable('名称', '定义', '表示', [
    [r'零向量', r'长度为' + kb('0') + r'的向量叫做零向量', r'记作' + kb('0')],
    [r'单位向量', r'模等于' + kb('1') + r'的向量', r'用 \(e\) 表示，\(|e|=1\)'],
    [r'相反向量', r'与 \(\overrightarrow{a}\) 长度相同而方向' + kb('相反') + r'的向量', r'记作 \(-\overrightarrow{a}\)'],
    [r'共线向量或平行向量', r'表示若干空间向量的有向线段所在的直线' + kb('互相平行') + r'或' + kb('重合'), r'记作 \(\overrightarrow{a}\parallel\overrightarrow{b}\)'],
    [r'相等向量', r'方向相同且' + kb('模相等') + r'的向量', r'记作 \(\overrightarrow{a}=\overrightarrow{b}\)'],
])
log('5c. 知识点一：条目 1～3 选编＋挖空；三列挖空表 cells 选编自源讲部「特殊向量」表')

# —— ◆知识点二 ——
em(r'\zsd{二}{空间向量的线性运算}')
em(r'\tiaomu{4}{加法可按' + kb('三角形') + r'法则或' + kb('平行四边形') + r'法则作出；减法 \(\overrightarrow{a}-\overrightarrow{b}\) '
   r'为减向量终点指向被减向量终点；数乘 \(\lambda\overrightarrow{a}\)：当 \(\lambda>0\) 时与 \(\overrightarrow{a}\) 方向' + kb('相同') +
   r'，当 \(\lambda<0\) 时方向' + kb('相反') + r'，当 \(\lambda=0\) 时 \(\lambda\overrightarrow{a}=\overrightarrow{0}\)．}')
em(r'\zhuzhu{' + entries[4]['note'] + '}')
em(r'\tiaomu{5}{共线的充要条件：对任意两个空间向量 \(\overrightarrow{a},\overrightarrow{b}\)（\(\overrightarrow{b}\neq\overrightarrow{0}\)），'
   r'\(\overrightarrow{a}\parallel\overrightarrow{b}\) 的充要条件是存在' + kb('实数') +
   r' \(\lambda\)，使 \(\overrightarrow{a}=\lambda\overrightarrow{b}\)．}')
em(r'\zhuzhu{' + entries[5]['note'] + '}')
kbtable('运算', '法则要点', '运算律举例', [
    [r'加法', r'三角形法则／平行四边形法则（与平面向量一致）', r'\(\overrightarrow{a}+\overrightarrow{b}=\overrightarrow{b}+\overrightarrow{a}\)'],
    [r'减法', r'减向量终点指向被减向量终点', r'\((\overrightarrow{a}+\overrightarrow{b})+\overrightarrow{c}=\overrightarrow{a}+(\overrightarrow{b}+\overrightarrow{c})\)'],
    [r'数乘', r'实数 \(\lambda\) 与向量 \(\overrightarrow{a}\) 的乘积仍为向量', r'\((\lambda+\mu)\overrightarrow{a}=\lambda\overrightarrow{a}+\mu\overrightarrow{a}\)'],
    [r'共线', r'\(\overrightarrow{a}\parallel\overrightarrow{b}\)（\(\overrightarrow{b}\neq\overrightarrow{0}\)）', r'\(\overrightarrow{a}=\lambda\overrightarrow{b}\)'],
])
log('5d. 知识点二：条目 4～5 选编＋挖空；三列挖空表 cells 选编自源讲部「加法／运算律」表')

# —— ◆知识点三 ——
em(r'\zsd{三}{空间向量的夹角、数量积与共面}')
em(r'\tiaomu{6}{夹角：已知两个非零向量 \(\overrightarrow{a},\overrightarrow{b}\)，在空间中任取一点 \(O\)，'
   r'作 \(\overrightarrow{OA}=\overrightarrow{a},\overrightarrow{OB}=\overrightarrow{b}\)，则大小在' + kb('[0°,180°]') +
   r'内的 \(\angle AOB\) 称为 \(\overrightarrow{a}\) 与 \(\overrightarrow{b}\) 的夹角，记作 \(\langle\overrightarrow{a},\overrightarrow{b}\rangle\)；'
   r'当 \(\langle\overrightarrow{a},\overrightarrow{b}\rangle=\frac{\pi}{2}\) 时，称 \(\overrightarrow{a}\) 与 \(\overrightarrow{b}\)' +
   kb('互相垂直') + r'，记作 \(\overrightarrow{a}\perp\overrightarrow{b}\)．}')
em(r'\zhuzhu{' + entries[6]['note'] + '}')
em(r'\tiaomu{7}{数量积：定义 \(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle\)；'
   '规定' + kb('零向量') + r'与任意向量的数量积为 0．'
   r'性质：\(\overrightarrow{a}\perp\overrightarrow{b}\Leftrightarrow\overrightarrow{a}\cdot\overrightarrow{b}=0\)；'
   r'\(\overrightarrow{a}\cdot\overrightarrow{a}={{\overrightarrow{a}}^{2}}={\left| \overrightarrow{a} \right|}^{2}\)；'
   r'\(\left| \overrightarrow{a}\cdot\overrightarrow{b} \right|\leq\left| \overrightarrow{a} \right|\left| \overrightarrow{b} \right|\)．}')
for s in entries[7]['blocks']:
    if s.startswith('【微提醒】'):
        em(r'\zhuzhu{' + s + '}')
em(r'\zhuzhu{' + entries[7]['note'] + '}')
emit_blocks(reflow(entries[8]['blocks'], '知识点三'))
log('5e. 知识点三：条目 6～7、9 选编＋挖空；条目 8「投影向量」整段源文排印（含投影三联图 30mm 独立居中）')
em(r'\tiaomu{9}{共面的充要条件：向量 \(\overrightarrow{p}\) 与不共线向量 \(\overrightarrow{a},\overrightarrow{b}\) 共面的充要条件是存在' +
   kb('有序实数对') + r' \((x,y)\)，使 \(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\)．}')
em(r'\zhuzhu{' + entries[9]['note'] + '}')
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

# —— 诊断分析（演示命制 ×4）——
em(r'\zhenhead{判断正误（正确的打“√”，错误的打“×”）}')
for i, (t, a) in enumerate([
    (r'相等向量一定是共线向量．', '√'),
    (r'若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，\(\overrightarrow{b}\parallel\overrightarrow{c}\)，则 \(\overrightarrow{a}\parallel\overrightarrow{c}\)．', '×'),
    (r'两个空间向量的模相等，则这两个向量相等．', '×'),
    (r'若 \(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\)（\(\overrightarrow{a},\overrightarrow{b}\) 不共线），则 \(\overrightarrow{p},\overrightarrow{a},\overrightarrow{b}\) 共面．', '√'),
], 1):
    em(r'\zhenti{（' + '一二三四'[i-1] + '）}{' + t + '}{\\ansul{' + a + '}}')
log('5f. 【诊断分析】判断正误 4 道＝按诊断题型模板（概念辨析／条件判定／定理适用）演示命制，非源节原题；'
    '答案 √××√ 下划线紧跟')

# —— 课中探究 ——
em(r'\huaxing{课中探究}{例变探究\quad 素养提升}')

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
EXEMPLAR = {1: (2, 1), 2: (3, 2), 3: (4, 3), 5: (6, 5), 7: (8, 7)}   # 探究点序 → (组号, 题号k)
BIANSHI = {7: (8, 8)}
for gi, gname in enumerate(grp_order, 1):
    gnum = int(re.match(r'1\.1\.1\.(\d+)', gname).group(1))
    em(r'\tjd{' + CN[gi-1] + '｜' + gname.split(' ', 1)[1] + '}')
    if gi in EXEMPLAR:
        k = EXEMPLAR[gi][1]
        d = tis[(gnum, k)]
        em(r'\li{例1}{源 ' + d['num'] + '·' + d['nanidu'] + '}{' + d['stem'][0] + '}')
        emit_blocks(reflow(d['stem'][1:], f'例{gi}'))
        emit_blocks(reflow(d['fenxi'], f'例{gi}'))
        emit_blocks(reflow(d['xiangjie'], f'例{gi}'))
        log(f'5g. 探究点{CN[gi-1]}：例1＝{d["num"]}（{d["nanidu"]}）带【分析】【详解】紧跟；【知识点】标签不排印（登记）')
    if gi in BIANSHI:
        k = BIANSHI[gi][1]
        d = tis[(gnum, k)]
        em(r'\li{变式1}{源 ' + d['num'] + '·' + d['nanidu'] + '}{' + d['stem'][0] + '}')
        emit_blocks(reflow(d['stem'][1:], f'变式{gi}'))
        em(r'\ansline{' + d['ans'] + '}')
        log(f'5g. 探究点{CN[gi-1]}：变式＝{d["num"]}（{d["nanidu"]}）仅排答案（下划线紧跟），不排【分析】【详解】')
    if gi not in EXEMPLAR and gi not in BIANSHI:
        log(f'5g. 探究点{CN[gi-1]}（{gname.split(" ", 1)[1]}）：不设例1——组题让渡练习件（池子守恒取舍，登记）')
    em(r'\xiaojie{' + SANJU[gnum] + '}')
log('5g. 【素养小结】9 组＝源「题型通式」编注移位改三句式（识别／操作／收束），通式原文不再单独排印（登记）')

# —— 课堂检测（演示命制 ×2）——
em(r'\huaxing{课堂检测}{限时训练\quad 当堂达标}')
em(r'\jiance{1．已知 \(|\overrightarrow{a}|=2\)，\(|\overrightarrow{b}|=3\)，\(\langle\overrightarrow{a},\overrightarrow{b}\rangle=60^\circ\)，则 \(\overrightarrow{a}\cdot\overrightarrow{b}=\)\kongbai{}．}{\ansul{3}}')
em(r'\jiance{2．已知 \(\overrightarrow{a}=\overrightarrow{e_1}\allowbreak+\allowbreak2\overrightarrow{e_2}\)，\(\overrightarrow{b}=\allowbreak2\overrightarrow{e_1}\allowbreak-\allowbreak\overrightarrow{e_2}\allowbreak\)（\(\overrightarrow{e_1}\allowbreak,\allowbreak\overrightarrow{e_2}\) 不共线），判断 \(\overrightarrow{a}\) 与 \(\overrightarrow{b}\) 是否共线．}'
   r'{\ansul{不共线}\allowbreak（设 \(\overrightarrow{a}=\lambda\overrightarrow{b}\) 得 \(\lambda=2\) 且 \(2\lambda=-1\)，矛盾）}')
log('5h. 课堂检测 2 题＝演示命制（数量积定义求值＋共线判定），答案下划线紧跟')

log('5. 图独立成块（7mm 起排，默认 30mm 档）：' + '；'.join(f'{n}→{w}({k})' for n, w, k in figs_seen))

# ---- 6. 巨型公式断点（同 v2 11b）＋输出 ----
body_text = '\n\n'.join(body)
n_ab = body_text.count(' = \\left') + body_text.count(' \\cdot \\left')
body_text = body_text.replace(' = \\left', ' = \\allowbreak\\left')
body_text = body_text.replace(' \\cdot \\left', ' \\cdot \\allowbreak\\left')
log(f'6. 巨型行内公式显式断点：顶层 = 与 · 后注入 \\allowbreak ×{n_ab}（同 v2 11b，详解C 溯源链）')
open(BASE + r'\body.tex', 'w', encoding='utf-8').write(body_text + '\n')
head = [
    r'\zhangtitle{第1章 空间向量与立体几何}',
    r'\jietitle{1.1 空间向量及其运算}',
    r'\xiaojietitle{1.1.1 空间向量及其运算}',
    r'\keshi{第1课时\quad 空间向量及其运算}',
]
open(BASE + r'\chapterhead.tex', 'w', encoding='utf-8').write('\n'.join(head) + '\n')
log('7. 章首通栏：章22/节18/小节15/课时14（源节未分课时，课时名沿用小节名——演示性定名，登记）；'
    '讲练件的统计行与 T0 导航表不排入导学件（件型差异，登记）')
open(BASE + r'\postproc_daoxue_log.txt', 'w', encoding='utf-8').write('\n'.join(LOG))
print('\n'.join(LOG))
