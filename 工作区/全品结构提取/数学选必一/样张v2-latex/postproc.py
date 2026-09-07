# -*- coding: utf-8 -*-
"""后处理器：sec.tex（pandoc 原始输出）→ chapterhead.tex（章首通栏块）+ body.tex（双栏正文）。
变换清单（逐项登记到 postproc_log.txt）：
1. 去 U+2060 词连接符；去隐藏节名锚段（Word 中为 1pt 白字不可见）
2. 向量记号归一化：\\overset{⃑}{X} → \\overrightarrow{X}（源 OMML 重音字符在 Latin Modern 缺字形）
3. longtable→tabular（twocolumn 下 longtable 不工作）；清理 endhead/endlastfoot 机制；补 \\bottomrule
4. 表内图片 width=\\linewidth 防溢出；独立图片按原图宽度三档 30/45/86mm
5. 标题映射：\\zhangtitle（22pt 黑体居中+通栏横线）/\\jietitle（18pt）/\\xiaojietitle（15pt）/
   \\zutit（题型组 12pt 加粗+左黑竖条）/\\timu（题号悬挂 7mm+题前 6pt 距）
6. 答案行一行式合并：【答案】值　【知识点】知识点，答案值 \\ansbox 浅灰底
7. 【X】标签 \\biaoqian 黑体化；长下划线串 → \\kongbai（\\underline{\\hspace*{15mm}}）"""
import re

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v2-latex"
SRC = BASE + r"\sec.tex"
LOG = []
log = LOG.append

tex = open(SRC, encoding='utf-8').read()

# ---- 1. 词连接符 ----
n = tex.count('\u2060')
tex = tex.replace('\u2060', '')
log(f'1. 去除 U+2060 词连接符 {n} 个')

# ---- 2. 向量箭头归一化 ----
n = len(re.findall(r'\\overset\{⃑\}\{', tex))
tex = tex.replace(r'\overset{⃑}{', r'\overrightarrow{')
log(f'2. \\overset{{⃑}} {{X}} → \\overrightarrow{{X}} 归一化 {n} 处（语义等价：源为箭头重音）')

# ---- 3. longtable → tabular ----
tex = tex.replace(r'\begin{longtable}[]{@{}', r'\begin{tabular}{@{}')
tex = tex.replace(r'\end{longtable}', r'\end{tabular}')
lines = tex.split('\n')
out = []
for i, ln in enumerate(lines):
    s = ln.strip()
    if s in (r'\endhead', r'\endlastfoot'):
        continue
    if s == r'\bottomrule\noalign{}':
        continue  # 原属 endlastfoot，末尾统一补
    if s == r'\toprule\noalign{}':
        out.append(r'\toprule'); continue
    if s == r'\midrule\noalign{}':
        out.append(r'\midrule'); continue
    if s == r'{\def\LTcaptype{none} % do not increment counter':
        continue
    if s == '}' and out and out[-1].strip() == r'\end{tabular}':
        out.pop()  # 取回 \end{tabular}，补 \bottomrule 后收尾；LTcaptype 闭括号直接丢弃
        out.append(r'\bottomrule')
        out.append(r'\end{tabular}')
        continue
    out.append(ln)
tex = '\n'.join(out)
log('3. longtable→tabular 转换 6 表，规则线规范化（top/mid/bottomrule）')

# ---- 3b. 列宽归一化：pandoc 的 \real 占比是相对 docx 表宽的，双栏内按合计归一到 \linewidth ----
def norm_table(m):
    pre = m.group(1)
    fracs = re.findall(r'\* \\real\{([\d.]+)\}', pre)
    if not fracs:
        return m.group(0)
    total = sum(float(f) for f in fracs)
    if total <= 0 or abs(total - 1) < 1e-6:
        return m.group(0)
    def scale(fmv):
        val = float(fmv.group(1)) / total
        return f'* \\real{{{val:.4f}}}'
    return re.sub(r'\* \\real\{([\d.]+)\}', scale, pre)

n_norm = 0
def table_iter(m):
    global n_norm
    r = norm_table(m)
    if r != m.group(0):
        n_norm += 1
    return r

tex = re.sub(r'(\\begin\{tabular\}\{@\{}.*?)(?=\\toprule)', table_iter, tex, flags=re.S)
log(f'3b. 表格列宽归一化 {n_norm} 表（pandoc 占比按 docx 表宽计，双栏下重新归一）')

# ---- 4. 图片宽度分档 ----
# 先找 tabular 块，块内 width=\linewidth；块外按原图宽三档
def bucket(mm):
    return '30mm' if mm <= 32 else ('45mm' if mm <= 65 else '86mm')

tab_spans = [m.span() for m in re.finditer(r'\\begin\{tabular\}.*?\\end\{tabular\}', tex, re.S)]
n_in = n_out = 0
def repl_img(m):
    global n_in, n_out
    w_in = float(m.group(1)); pos = m.start()
    in_tab = any(a <= pos < b for a, b in tab_spans)
    if in_tab:
        n_in += 1
        return m.group(0).replace(f'width={m.group(1)}in,height={m.group(2)}in', r'width=\linewidth')
    mm = w_in * 25.4
    n_out += 1
    return m.group(0).replace(f'width={m.group(1)}in,height={m.group(2)}in', f'width={bucket(mm)}')
img_re = re.compile(r'\\includegraphics\[width=([\d.]+)in,height=([\d.]+)in(,[^\]]*)?\]')
tex = img_re.sub(repl_img, tex)
log(f'4. 表内图片 {n_in} 处 → width=\\linewidth；独立图片 {n_out} 处按原图宽分档 30/45/86mm')

# ---- 分块 ----
blocks = [b for b in re.split(r'\n\s*\n', tex) if b.strip()]

# ---- 5. 隐藏节名锚（与后续标题完全同文的孤立段）----
anchors = {'1.1 空间向量及其运算', '1.1.1 空间向量及其运算'}
dropped = [b for b in blocks if b.strip() in anchors]
blocks = [b for b in blocks if b.strip() not in anchors]
log(f'5. 删隐藏节名锚段 {len(dropped)} 个：{[d.strip()[:20] for d in dropped]}')

# ---- 6. 章标题 + 标题映射 ----
if blocks and re.fullmatch(r'\\textbf\{[^}]*\}', blocks[0].strip()) and '讲练件' in blocks[0]:
    inner = re.fullmatch(r'\\textbf\{([^}]*)\}', blocks[0].strip()).group(1)
    blocks[0] = r'\zhangtitle{' + inner + '}'
    log('6a. 首块 → \\zhangtitle（22pt 黑体居中＋通栏 0.4pt 横线）')

def map_headings(blocks):
    res = []
    for b in blocks:
        m = re.fullmatch(r'\\subsubsection\{\\texorpdfstring\{\\textbf\{([^}]*)\}\}\{[^}]*\}\}\\label\{[^}]*\}', b.strip(), re.S)
        if m:
            t = re.sub(r'\s+', ' ', m.group(1)).strip()
            if re.match(r'^1\.1\.\d+\s', t):
                res.append(r'\xiaojietitle{' + t + '}')
            elif re.match(r'^1\.1\s', t):
                res.append(r'\jietitle{' + t + '}')
            else:
                res.append(r'\xiaojietitle{' + t + '}')
            continue
        # 题号：整块以 \textbf{X．（难度）} 起头
        m = re.match(r'\\textbf\{(\d+\.\d+\.\d+\.\d+-\d+．（(?:简单|中档|难)）)\}(.*)$', b.strip(), re.S)
        if m:
            rest = m.group(2).replace('\n', ' ')
            res.append(r'\timu{' + m.group(1) + '}{' + rest + '}')
            continue
        # 题型组标题：整块为 \textbf{四段编号 标题}
        m = re.fullmatch(r'\\textbf\{(\d+\.\d+\.\d+\.\d+[^}]*)\}', b.strip(), re.S)
        if m and '．（' not in m.group(1):
            res.append(r'\zutit{' + m.group(1) + '}')
            continue
        res.append(b)
    return res

blocks = map_headings(blocks)
n_timu = sum('\\timu{' in b for b in blocks)
n_zutit = sum(b.startswith('\\zutit{') for b in blocks)
log(f'6. 标题映射：小节 \\xiaojietitle、节 \\jietitle、题型组 \\zutit×{n_zutit}、题号悬挂 \\timu×{n_timu}')

# ---- 7. 答案行合并 ----
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
        part = r'\noindent\biaoqian{【答案】}\ansbox{' + value + '}'
        if i < len(blocks) and is_label_alone(blocks[i], '知识点') and i + 1 < len(blocks):
            part += r'\quad\biaoqian{【知识点】}' + blocks[i + 1].strip().replace('\n', ' ')
            i += 2
        res.append(part)
        merged += 1
        continue
    res.append(b)
    i += 1
blocks = res
log(f'7. 答案行一行式合并 {merged} 处（答案值加 \\ansbox 浅灰底）')

# ---- 8. 标签黑体化 + 挖空 ----
body_text = '\n\n'.join(blocks)
n_lab = len(re.findall(r'【(?:编注|微提醒|分析|详解|点睛)】', body_text))
body_text = re.sub(r'【(编注|微提醒|分析|详解|点睛)】', r'\\biaoqian{【\1】}', body_text)
n_kong = len(re.findall(r'(?:\\_){4,}', body_text))
body_text = re.sub(r'(?:\\_){4,}', r'\\kongbai', body_text)
log(f'8. 【】标签黑体化 {n_lab} 处；长下划线挖空 → \\kongbai {n_kong} 处')

# ---- 9. 拆章首 / 正文 ----
first_tab = re.search(r'\\begin\{tabular\}.*?\\end\{tabular\}', body_text, re.S)
chapter = body_text[:first_tab.end()]
rest = body_text[first_tab.end():]
# 正文内不可分页大表格在栏首放不下会溢出压页脚，改为 table 浮动（栏顶放置）
rest = rest.replace(r'\begin{tabular}', r'\begin{table}[!t]\centering\begin{tabular}')
rest = rest.replace(r'\end{tabular}', r'\end{tabular}\end{table}')
log(f'9a. 正文表格转 table[!htbp] 浮动 ×{rest.count(chr(92) + "begin{table}")}')
# chapter 里：\zhangtitle + 统计行 + 表
mz = re.search(r'^(.*?)(\\begin\{tabular\}.*?\\end\{tabular\})', chapter, re.S)
head_pre, head_tab = mz.group(1).strip(), mz.group(2)
# 首块是 \zhangtitle{...}
mm = re.match(r'\\zhangtitle\{(.*)\}$', head_pre.split('\n\n')[0].strip(), re.S)
chap_title = mm.group(1) if mm else ''
stats = '\n\n'.join(head_pre.split('\n\n')[1:]).strip()

chap_file = r'\zhangtitle{' + chap_title + '}\n'
if stats:
    chap_file += '\\statsline{' + stats.replace('\n', ' ') + '}\n'
chap_file += '\\vspace{2pt}\n' + head_tab + '\n'
open(BASE + r'\chapterhead.tex', 'w', encoding='utf-8').write(chap_file)
open(BASE + r'\body.tex', 'w', encoding='utf-8').write(rest.strip() + '\n')
log(f'9. 拆分：chapterhead.tex（章标题「{chap_title[:26]}…」+统计行+统计表）、body.tex（正文 {len(rest)} 字符）')

open(BASE + r'\postproc_log.txt', 'w', encoding='utf-8').write('\n'.join(LOG))
print('\n'.join(LOG))
