# -*- coding: utf-8 -*-
"""v2 后处理器：sec.tex（pandoc 原始输出）→ chapterhead_v2.tex + body_v2.tex + postproc_v2_log.txt。
相对 v1（postproc.py）的全部结构性差异逐项登记到 LOG：
  A. 表格：booktabs 三线制 → 全框 0.4pt \\hline 网格；T0/T1/T2 表头行白底黑体加粗居中（v2.1 弃
     thbg 灰底）；T3/T4/T5 无表头行、首列标签黑体；列宽定长（T0 通栏 166mm；正文表收缩至
     合计 ≤79mm 以留出题号列 7mm，6 表逐一登记）；\\tabcolsep 3pt
  B. 图：86mm 档禁用，按内容分档 30/45mm 逐张登记；正文图一律独立成块、从题号右缘 7mm 起排
     （\\makebox 定宽 linewidth−7mm 栏内居中＋段前后 \\penalty10000 绑定；行内图改独立，
     行首落位不定无法断言题号列）；表内图按格宽定宽居中
  C. 结构：节/小节/本节统计行抽出进 chapterhead_v2（multicol 外通栏）；题型组标题挂
     「探究点N｜」编号（逐组登记）；讲部 9 条目聚 3 个知识点块（\\zhishi 插入，映射登记）；
     章标题删「·讲练件（140题）」改「第1章 空间向量与立体几何」（演示性改动）
  D. 逻辑绑定：题干→选项/①链/「故答案为|故选」尾句段前 \\penalty10000；选项与①段 \\noindent
正文题目文字与公式零增删（新增仅为结构标题、版式标记与绑定惩罚点）。"""
import re

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v2-latex"
SRC = BASE + r"\sec.tex"
LOG = []
log = LOG.append

tex = open(SRC, encoding='utf-8').read()

# ---- 1. 词连接符（同 v1） ----
n = tex.count('\u2060')
tex = tex.replace('\u2060', '')
log(f'1. 去除 U+2060 词连接符 {n} 个（同 v1）')

# ---- 2. 向量箭头归一化（同 v1，语义等价） ----
n = len(re.findall(r'\\overset\{⃑\}\{', tex))
tex = tex.replace(r'\overset{⃑}{', r'\overrightarrow{')
log(f'2. \\overset{{⃑}}{{X}} → \\overrightarrow{{X}} 归一化 {n} 处（同 v1，语义等价：源为箭头重音）')

# ---- 3. longtable → tabular；booktabs 规则线全部移除（v2 改全框网格） ----
tex = tex.replace(r'\begin{longtable}[]{@{}', r'\begin{tabular}{@{}')
tex = tex.replace(r'\end{longtable}', r'\end{tabular}')
lines = tex.split('\n')
out = []
for ln in lines:
    s = ln.strip()
    if s in (r'\endhead', r'\endlastfoot', r'{\def\LTcaptype{none} % do not increment counter'):
        continue
    if re.fullmatch(r'\\(toprule|midrule|bottomrule)(\\noalign\{\})?', s):
        continue  # v2：三线制规则线一律移除，网格 \\hline 后补
    if s == '}' and out and out[-1].strip() == r'\end{tabular}':
        continue  # LTcaptype 组闭括号，丢弃
    out.append(ln)
tex = '\n'.join(out)
log('3. longtable→tabular 转换 6 表；booktabs top/mid/bottomrule 全部移除（v2 改全框 0.4pt \\hline 网格）')

# ---- 4. 去 pandoc 表格单元格 minipage 包装 ----
n_mini = len(re.findall(r'\\begin\{minipage\}\[b\]\{\\linewidth\}\\raggedright', tex))
tex = re.sub(r'\\begin\{minipage\}\[b\]\{\\linewidth\}\\raggedright\s*\n?(.*?)\s*\\end\{minipage\}',
             r'\1', tex, flags=re.S)
log(f'4. 去 pandoc 表格单元格 minipage 包装 {n_mini} 处（行结构归一，便于表头样式与网格处理）')

# ---- 5. 表格重构：列宽按内容定长 + 全框网格 + 表头样式 + 首列黑体 ----
SPECS = [
    # (表头关键字, 列格式串)——T0 通栏导航表不缩（multicols 外无题号语境）；正文表内容宽度收缩
    # （题号列恒空：表从栏左+7mm 起排，n 列合计 = Σp + 2n·tabcolsep + (n+1)·0.4pt 线 ≤ 79.25mm
    #  → n=3 内容 ≤72mm（合计 78.91）、n=2 内容 ≤74mm（合计 78.65），加 7mm 后 ≤85.91 ≤ 栏宽 86.25mm）
    ('节名',   r'|>{\raggedright\arraybackslash}p{78mm}|>{\centering\arraybackslash}p{14mm}|>{\raggedright\arraybackslash}p{44mm}|>{\centering\arraybackslash}p{30mm}|'),
    ('对比项', r'|>{\raggedright\arraybackslash}p{13mm}|>{\raggedright\arraybackslash}p{27mm}|>{\raggedright\arraybackslash}p{32mm}|'),
    ('特殊向量', r'|>{\raggedright\arraybackslash}p{22mm}|>{\raggedright\arraybackslash}p{52mm}|'),
    ('加法',   r'|>{\raggedright\arraybackslash}p{15mm}|>{\raggedright\arraybackslash}p{26mm}|>{\centering\arraybackslash}p{31mm}|'),
    ('交换律', r'|>{\raggedright\arraybackslash}p{18mm}|>{\raggedright\arraybackslash}p{56mm}|'),
    ('图示',   r'|>{\raggedright\arraybackslash}p{16mm}|>{\raggedright\arraybackslash}p{58mm}|'),
]
HEADER_TABLES = {'节名', '对比项', '特殊向量'}       # 有表头行 → 灰底黑体居中
LABELBOLD_TABLES = {'加法', '交换律', '图示'}        # 无表头行 → 首列标签黑体
FIG_IN = {'sub3_B_1.png': '30mm', 'sub3_B_2.png': '30mm', 'sub3_B_3.png': '45mm'}
MROW_VMOVE = '0pt'   # multirow 图片垂直修正（scan_vmove 实测定值：0pt→Overfull \vbox=0 且 sub3_B_1/2 图顶低于顶线 4.4/3.8pt；6/8pt 图上浮越线 1.6/3.6pt，弃）

PRE_RE = re.compile(r'\\begin\{tabular\}\{(?:[^{}]|\{[^{}]*\})*\}', re.S)

def strip_textbf(c):
    c = c.strip().replace('\n', ' ')
    m = re.fullmatch(r'\\textbf\{(.*)\}', c)
    return m.group(1).strip() if m else c

def build_table(t, idx):
    kw, spec = SPECS[idx]
    i0 = t.index(r'\begin{tabular}{@{}')
    i1 = t.index('@{}}', i0 + 20) + len('@{}}')
    t = t[:i0] + r'\begin{tabular}{' + spec + '}' + t[i1:]
    # 表头关键字校验（顺序错配则响亮失败）
    pe = PRE_RE.search(t, i0).end()
    first_row = t[pe:i0 + len(t[i0:].split('\\\\')[0])].replace('\n', ' ')
    assert kw in first_row, f'表格顺序错配：第 {idx+1} 表预期表头含「{kw}」，实际「{first_row[:80]}」'
    # 表头行样式（仅 T0/T1/T2）：\\rowcolor 灰底＋\\multicolumn 居中＋黑体加粗
    if kw in HEADER_TABLES:
        m = re.search(r'(?s)(.*?)\\\\', t[pe:])
        head_raw = m.group(1)
        widths = re.findall(r'p\{(\d+)mm\}', spec)
        cells = [strip_textbf(c) for c in head_raw.split('&')]
        newcells = []
        for j, c in enumerate(cells):
            bar = r'|>{\centering\arraybackslash}p{' + widths[j] + 'mm}|'
            newcells.append(r'\multicolumn{1}{' + bar + r'}{\textbf{' + c + r'}}')
        newhead = ' & '.join(newcells) + r' \\'
        t = t[:pe] + t[pe:].replace(head_raw + r'\\', newhead, 1)
        log(f'5-{idx+1} [{kw}] 表头行样式：白底黑体加粗＋\\multicolumn 定宽 p{{Wmm}} 居中'
            f'（弃 |c| 自然宽度：T1 实测 col2 被撑宽 3.9mm→右缘超栏 6.77pt；v2.1 弃 \\rowcolor{{thbg}} 灰底）'
            f'，{len(cells)} 列，宽 {widths}')
    # 全框网格：preamble 后插首线；每个行尾 \\\\ 后补 \\hline
    pe = PRE_RE.search(t, i0).end()
    body = t[pe:]
    n_rows = [0]
    def add_hline(mm):
        n_rows[0] += 1
        return mm.group(0) + r' \hline'
    body = re.sub(r'\\\\(?=\s*\n)', add_hline, body)
    t = t[:pe] + '\n\\hline' + body
    log(f'5-{idx+1} [{kw}] 列宽定长：{spec}（弃 pandoc \\real 占比）＋全框 \\hline ×{n_rows[0]+1}（含首末线）')
    # 首列标签黑体（无表头行的表）
    if kw in LABELBOLD_TABLES:
        nb = [0]
        def bold_first(mm):
            nb[0] += 1
            return mm.group(1) + r'\textbf{' + mm.group(2) + '}' + mm.group(3)
        body = t[pe:]
        nb2 = [0]
        def bold_first2(mm):
            nb2[0] += 1
            return r'\textbf{' + mm.group(1) + '}'
        body = re.sub(r'(?m)^([^&\\\n][^&\n]*?)(?=[ \t]*&)', bold_first2, body)
        body = re.sub(r'(?m)^(\\multirow\{\d+\}\{=\}\{)([^{}\\]+)(\})', bold_first, body)
        t = t[:pe] + body
        log(f'5-{idx+1} [{kw}] 表无表头行：首列标签黑体 ×{nb[0] + nb2[0]}')
    # 表内图片：按 FIG_IN 定宽并居中（sec.tex 原始为 width=Nin,height=Nin）
    n_fig = [0]
    done_names = []
    def fig_in(mm):
        name = mm.group(3).split('/')[-1]
        w = FIG_IN.get(name)
        if not w:
            return mm.group(0)
        n_fig[0] += 1
        done_names.append(f'{name}→{w}')
        return r'\includegraphics[width=' + w + (mm.group(2) or '') + r']{' + mm.group(3) + r'}'
    t = re.sub(r'\\includegraphics\[(width=[\d.]+in,height=[\d.]+in)(,alt=\{[^}]*\})?\]\{([^}]+)\}', fig_in, t)
    # multirow 图片格注入垂直修正（multirow 对 \arraystretch 行高估算偏大，实测溢出 ~12pt，迭代定值）。
    # 格内用裸图：multirow {=} 路径为 \strut#6\strut\par，外包 {\centering…\par} 会多出一行 → Overfull \vbox；
    # 水平居中由 main_v2.tex 的 \multirowsetup{\centering} 承担
    t = re.sub(r'(\\multirow\{\d+\}\{=\})\{(\s*\\includegraphics)',
               lambda mm: mm.group(1) + '[' + MROW_VMOVE + ']{' + mm.group(2), t)
    # 单元格内空段 → \par（防后续按空行分块时把表格拆开；渲染等价）
    n_par = len(re.findall(r'\n[ \t]*\n', t))
    if n_par:
        t = re.sub(r'\n[ \t]*\n', lambda mm: '\n\\par\n', t)
        log(f'5-{idx+1} [{kw}] 表内单元格空段 → \\par ×{n_par}（防分块拆表）')
    if n_fig[0]:
        log(f'5-{idx+1} [{kw}] 表内图片 {n_fig[0]} 处定宽（水平居中由 \\multirowsetup 承担）：' + '，'.join(done_names))
    return t

tab_spans = [(m.start(), m.end()) for m in re.finditer(r'\\begin\{tabular\}.*?\\end\{tabular\}', tex, flags=re.S)]
assert len(tab_spans) == 6, f'预期 6 表，实得 {len(tab_spans)}'
new_tex, last = [], 0
for idx, (a, b) in enumerate(tab_spans):
    new_tex.append(tex[last:a])
    new_tex.append(build_table(tex[a:b], idx))
    last = b
new_tex.append(tex[last:])
tex = ''.join(new_tex)

# ---- 6. 分块 ----
blocks = [b for b in re.split(r'\n\s*\n', tex) if b.strip()]

# ---- 7. 删隐藏节名锚段（同 v1） ----
anchors = {'1.1 空间向量及其运算', '1.1.1 空间向量及其运算'}
dropped = [b.strip() for b in blocks if b.strip() in anchors]
blocks = [b for b in blocks if b.strip() not in anchors]
log(f'7. 删隐藏节名锚段 {len(dropped)} 个：{[d[:20] for d in dropped]}（同 v1，按渲染语义删除）')

# ---- 8. 章标题（演示性改动）＋标题映射 ----
HEAD_MARK = '\x00HEAD\x00'
head_pre = []      # 章首表之前的通栏块（章标题、全件统计行）
head_post = []     # 章首表之后的通栏块（节/小节标题、本节统计行）
chap_title_old = ''
t0_seen = False
if blocks and re.fullmatch(r'\\textbf\{[^}]*\}', blocks[0].strip()) and '讲练件' in blocks[0]:
    chap_title_old = re.fullmatch(r'\\textbf\{([^}]*)\}', blocks[0].strip()).group(1)
    blocks[0] = ''
    head_pre.append(r'\zhangtitle{第1章 空间向量与立体几何}')
    log(f'8a. 章标题（演示性改动）：「{chap_title_old}」→「第1章 空间向量与立体几何」（删「人教B版选必1」前缀与「·讲练件（140题）」后缀）')

CN = '一二三四五六七八九'
tan_count = 0
timu_count = 0
jietext = xiaotext = ''
for bi, b in enumerate(blocks):
    s = b.strip()
    if r'\begin{tabular}' in s:
        t0_seen = True
    # 节/小节标题 → 通栏区
    m = re.fullmatch(r'\\subsubsection\{\\texorpdfstring\{\\textbf\{([^}]*)\}\}\{[^}]*\}\}\\label\{[^}]*\}', s, re.S)
    if m:
        t = re.sub(r'\s+', ' ', m.group(1)).strip()
        if re.match(r'^1\.1\.\d+\s', t):
            xiaotext = t
            cmd = r'\xiaojietitle{' + t + '}'
        elif re.match(r'^1\.1\s', t):
            jietext = t
            cmd = r'\jietitle{' + t + '}'
        else:
            cmd = r'\xiaojietitle{' + t + '}'
        (head_post if t0_seen else head_pre).append(cmd)
        blocks[bi] = ''
        continue
    # 节级/本节统计行 → 通栏区
    if re.match(r'^(全件\d+题|本节\d+题)：', s):
        (head_post if t0_seen else head_pre).append(r'\statsline{' + s.replace('\n', ' ') + '}')
        blocks[bi] = ''
        continue
    # 题号：整块以 \textbf{X．（难度）} 起头 → \timu
    m = re.match(r'\\textbf\{(\d+\.\d+\.\d+\.\d+-\d+．（(?:简单|中档|难)）)\}(.*)$', s, re.S)
    if m:
        rest = m.group(2).replace('\n', ' ')
        blocks[bi] = r'\timu{' + m.group(1) + '}{' + rest + '}'
        timu_count += 1
        continue
    # 题型组标题：讲部组保持原名；题部组挂探究点编号（演示性改动）
    m = re.fullmatch(r'\\textbf\{(\d+\.\d+\.\d+\.\d+[^}]*)\}', s, re.S)
    if m and '．（' not in m.group(1):
        orig = m.group(1)
        if re.match(r'^1\.1\.1\.1(?!\d)', orig):
            blocks[bi] = r'\zutit{' + orig + '}'
        else:
            tan_count += 1
            blocks[bi] = r'\zutit{探究点' + CN[tan_count - 1] + '｜' + orig + '}'
            log(f'8b. 探究点挂号（演示性改动）：题型组「{orig}」→「探究点{CN[tan_count-1]}｜{orig}」')
        continue
blocks = [b for b in blocks if b != '']
log(f'8. 标题映射：节「{jietext}」/小节「{xiaotext}」/节级与本节统计行抽出为通栏块（multicol 外）；'
    f'题型组 \\zutit×{tan_count+1}（讲部组 1.1.1.1 保持原名＋探究点 {tan_count} 个）；\\timu×{timu_count}')

# ---- 9. 知识点块插入（演示性改动：映射逐块登记） ----
ZHISHI = {
    '1': ('一', '空间向量的概念', '条目1～3（定义→表示法→特殊向量）'),
    '4': ('二', '空间向量的线性运算', '条目4～5（加减数乘与运算律→共线充要条件）'),
    '6': ('三', '空间向量的夹角、数量积与共面', '条目6～9（夹角→数量积→投影向量→共面充要条件）'),
}
n_zs = 0
for bi, b in enumerate(blocks):
    m = re.match(r'^1\.1\.1-(\d)．〔基〕', b.strip())
    if m and m.group(1) in ZHISHI:
        cn, name, rng = ZHISHI[m.group(1)]
        blocks[bi] = r'\zhishi{' + cn + '}{' + name + '}' + '\n\n' + b
        log(f'9. 知识点块（演示性改动）：◆ 知识点{cn}　{name} ← {rng}')
        n_zs += 1
log(f'9. 知识点块共 {n_zs} 个（讲部 9 条目按内容聚类，块内条目顺序保持源序不动；正文条目文字零增删）')

# ---- 10. 答案行一行式合并（同 v1） ----
def is_label_alone(b, lab):
    return b.strip() == '【' + lab + '】'

def starts_label(b, lab):
    return b.strip().startswith('【' + lab + '】')

merged = 0
res = []
i = 0
while i < len(blocks):
    b = blocks[i]
    if starts_label(b, '答案'):
        s = b.strip()
        if is_label_alone(b, '答案') and i + 1 < len(blocks) and not starts_label(blocks[i + 1], '知识点') and blocks[i + 1].strip().startswith('【') is False:
            value = blocks[i + 1].strip().strip('　 ')
            i += 2
        else:
            value = s[len('【答案】'):].strip('　 ')
            i += 1
        part = r'\noindent\hangindent=7mm\hangafter=0\biaoqian{【答案】}\ansbox{' + value + '}'
        if i < len(blocks) and is_label_alone(blocks[i], '知识点') and i + 1 < len(blocks):
            part += r'\quad\biaoqian{【知识点】}' + blocks[i + 1].strip().replace('\n', ' ')
            i += 2
        res.append(part)
        merged += 1
        continue
    res.append(b)
    i += 1
blocks = res
log(f'10. 答案行一行式合并 {merged} 处（\\hangindent=7mm\\hangafter=0 全行缩进：题号列恒空，答案行'
    f'从题号右缘起排；\\ansbox \\fboxsep 收紧至 1pt）')

# ---- 11. 标签黑体化＋挖空（同 v1） ----
body_text = '\n\n'.join(blocks)
n_lab = len(re.findall(r'【(?:编注|微提醒|分析|详解|点睛)】', body_text))
body_text = re.sub(r'【(编注|微提醒|分析|详解|点睛)】', r'\\biaoqian{【\1】}', body_text)
n_kong = len(re.findall(r'(?:\\_){4,}', body_text))
body_text = re.sub(r'(?:\\_){4,}', r'\\kongbai', body_text)
log(f'11. 【】标签黑体化 {n_lab} 处；长下划线挖空 → \\kongbai {n_kong} 处（同 v1）')

# ---- 11b. 巨型行内公式显式断点（v2 实测修正） ----
# 1.1.1.6-5 详解 C：\tracingparagraphs 实证 TeX 对 \left\right 密集嵌套公式未建 rel/bin 自动断点
# （全公式仅 2 个断点候选：第 2 个 = 后、段末），首行被迫塞至第 2 个 = → 29.68pt overfull，
# 且与 \tolerance/\emergencystretch 取值无关（应急遍已运行、唯一候选 badness=∞）。
# 在顶层 =、· 之后显式注入 \allowbreak 恢复断点候选：纯惩罚点、零字形增删，
# TeX 仅在能降低总 demerits 时采用，不影响已可行段落
n_ab = body_text.count(' = \\left') + body_text.count(' \\cdot \\left')
body_text = body_text.replace(' = \\left', ' = \\allowbreak\\left')
body_text = body_text.replace(' \\cdot \\left', ' \\cdot \\allowbreak\\left')
log(f'11b. 巨型行内公式显式断点：顶层 = 与 · 后注入 \\allowbreak ×{n_ab} '
    '（1.1.1.6-5 详解 C 实证：\\left\\right 密集公式无自动断点→首行 29.68pt overfull，'
    '且与 tolerance/emergencystretch 无关；\\allowbreak 纯惩罚点零字形增删）')

# ---- 12. 图分档（86mm 禁用）＋独立图居中绑定 ----
FIG_OUT = {'sub3_B_4.png': '45mm', 'image1.png': '30mm', 'image2.png': '30mm',
           'image3.png': '30mm', 'image4.png': '30mm', 'image5.png': '30mm'}
FIG_NOTE = {
    'sub3_B_4.png': '投影三联图①②③（组合图元素繁多）',
    'image1.png': '直三棱柱线框（立体几何）',
    'image2.png': '正方体+AE 线框（立体几何）',
    'image3.png': '正方体+BC₁/AC 线框（立体几何）',
    'image4.png': '二面角两正方形拼接线框（立体几何）',
    'image5.png': '折叠矩形垂线图（立体几何）',
}
fig_registry = []
n_reflow = [0]     # 行内→独立改置的段计数（题号列恒空：行内图行首落位不定，一律改独立）
blocks = [b for b in body_text.split('\n\n') if b.strip()]
FIGRE = re.compile(r'\\includegraphics\[(width=[\d.]+in,height=[\d.]+in)(,alt=\{[^}]*\})?\]\{([^}]+)\}')

def fig_resized(mm):
    name = mm.group(3).split('/')[-1]
    w = FIG_OUT.get(name)
    if not w:
        return mm.group(0)   # 未分档：保留原样，稍后断言响亮失败
    return mm.group(0).replace(mm.group(1), 'width=' + w)

new_blocks = []
for b in blocks:
    if r'\begin{tabular}' in b:
        new_blocks.append(FIGRE.sub(fig_resized, b))   # 表内图按格定宽，随表走
        continue
    segs = []
    last = 0
    for mm in FIGRE.finditer(b):
        segs.append(('t', b[last:mm.start()]))
        segs.append(('f', mm))
        last = mm.end()
    segs.append(('t', b[last:]))
    if len(segs) > 1:
        n_reflow[0] += 1
    for kind, x in segs:
        if kind == 't':
            if x.strip():
                new_blocks.append(x.strip())
        else:
            name = x.group(3).split('/')[-1]
            w = FIG_OUT.get(name)
            assert w, f'12: {name} 未分档，拒排（题号列恒空无法保证）'
            fig_registry.append((name, w, '独立7mm起排'))
            tok = x.group(0).replace(x.group(1), 'width=' + w)
            new_blocks.append(r'\penalty10000\noindent\hspace*{7mm}'
                              r'\makebox[\dimexpr\linewidth-7mm\relax][c]{' + tok + r'}\par\penalty10000')
blocks = new_blocks
log('12. 图内容感知分档（86mm 禁用），正文 6 张逐张（另有表内 3 张见 5-4/5-6）：' +
    '；'.join(f'{n}→{w}({k})' for n, w, k in fig_registry) +
    '；正文图一律独立成块：\\noindent\\hspace*{7mm}＋\\makebox[linewidth−7mm] 栏内居中＋\\penalty10000 前后绑定'
    f'（题号列恒空：图从题号右缘起排；行内→独立改置 {n_reflow[0]} 段——行内图行首落位不定、x0 无法断言）；' +
    '判定依据：' + '，'.join(f'{k}：{v}' for k, v in FIG_NOTE.items()))

# ---- 13. 逻辑绑定：选项/①链/尾句段前惩罚点 ----
n_opt = n_tail = 0
for bi, b in enumerate(blocks):
    s = b.strip()
    if s.startswith(('A．', '①')):
        blocks[bi] = r'\penalty10000 \noindent ' + b
        n_opt += 1
    elif s.startswith(('故答案为', '故选')):
        blocks[bi] = r'\penalty10000' + b
        n_tail += 1
log(f'13. 逻辑绑定：选项/①段段前 \\penalty10000＋\\noindent ×{n_opt}（题干与选项不跨栏断；选项顶格对齐全品）；'
    f'「故答案为/故选」尾句段前 \\penalty10000 ×{n_tail}（不离题块成孤儿）；'
    '（multicol 下禁用含 \\break 的 \\Needspace：页级断点会跳过第二栏产生空栏页 p5，'
    '\\zutit 单变量实验实证删后 9→8 页）；模板层另设 \\clubpenalty=\\widowpenalty=10000、'
    'xeCJK CheckSingle（防孤字行）、\\zhishi/\\zutit/\\timu 前置 \\glueguard{4/6/4}'
    '（无 \\break 的软断点防孤悬，best effort）')

# ---- 14. 表格放置策略（v2 实测修正：multicol 环境下 table[!t] 浮动会被无限推迟、全篇丢失，
#           故 5 张正文表全部改随行居中；各表高度 60~115mm 均小于栏高 257mm，放不下时
#           LaTeX 自动在表前断栏移入下一栏顶，无溢出风险） ----
n_inline = 0
for bi, b in enumerate(blocks):
    if r'\begin{tabular}' not in b:
        continue
    if '节名' in b:
        continue  # 章首导航表：multicols 外通栏、无题号语境，7mm 规则不适用（登记豁免）
    blocks[bi] = r'\noindent\hspace*{7mm}' + b.strip() + r'\par'
    n_inline += 1
log(f'14. 表格放置策略：5 张正文表随行 7mm 起排 ×{n_inline}（\\noindent\\hspace*{{7mm}}：题号列恒空，'
    '表从题号右缘起排；列宽已收缩至合计 ≤78.9mm，78.9＋7=85.9 ≤ 栏宽 86.25mm，逐表算术见 5-N 日志；'
    'v1/v2 初稿的 table[!t] 浮动在 multicol 下被推迟丢失，实测废弃；'
    'T0 章首导航表 multicols 外通栏、无题号语境，不适用并登记豁免）')

# ---- 15. 拆分输出 ----
body_final = '\n\n'.join(blocks)
first_tab = re.search(r'\\begin\{tabular\}.*?\\end\{tabular\}', body_final, re.S)
chapter = body_final[:first_tab.end()].strip()      # 章首导航表（通栏，不浮动）
rest = body_final[first_tab.end():]
head_blocks = head_pre + ['\\vspace{4pt}', '\\noindent', chapter, '\\vspace{14pt}'] + head_post
open(BASE + r'\chapterhead_v2.tex', 'w', encoding='utf-8').write('\n'.join(head_blocks) + '\n')
open(BASE + r'\body_v2.tex', 'w', encoding='utf-8').write(rest.strip() + '\n')
log(f'15. 拆分输出：chapterhead_v2.tex（章标题＋全件统计＋导航表＋节/小节标题＋本节统计，全通栏）、'
    f'body_v2.tex（正文 {len(rest)} 字符，multicols 内双栏）')

open(BASE + r'\postproc_v2_log.txt', 'w', encoding='utf-8').write('\n'.join(LOG))
print('\n'.join(LOG))
