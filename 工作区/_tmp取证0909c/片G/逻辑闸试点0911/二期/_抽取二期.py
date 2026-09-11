# -*- coding: utf-8 -*-
"""逻辑闸试点0911·二期抽题器（题源＝variantF/body.tex 现盘）
口径：选择2＋填空2＋解答2，三类各取源件出现序前2，难度不挑、无随机。
做法：全部引串以「整行相等断言＋精确剥离」取得，逐字节源自源件；断言失败即报错退出，无手工转抄。
自检：①两文件题号一一对应、条数=6；②盲解版禁词0命中、判分值串⊄盲解版；③裁判版值串/解析串⊂源件。"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
SRC = os.path.join(ROOT, '工作区', '字替对照-0909', 'variantF', 'body.tex')

with open(SRC, encoding='utf-8') as f:
    src = f.read()
lines = src.split('\n')

def L(n):
    return lines[n - 1]

def expect(n, full):
    assert L(n) == full, 'L%d 与现盘不符:\n  现盘: %r\n  脚本: %r' % (n, L(n), full)

def cut(full, prefix='', suffix=''):
    assert full.startswith(prefix) and full.endswith(suffix), (prefix, suffix, full[:60])
    return full[len(prefix):len(full) - len(suffix)]

def last_arg(full):
    """花括号配平，取行内最后一个顶层 {…} 参数（题干槽位），剥净题号宏外壳与标签参。"""
    depth = 0
    start = None
    groups = []
    for i, ch in enumerate(full):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            assert depth >= 0, '花括号不配平: %r' % full[:40]
            if depth == 0:
                groups.append(full[start + 1:i])
    assert depth == 0 and groups, '花括号不配平: %r' % full[:40]
    return groups[-1]

OPT_P = r'\bindop' + 't {' + r'\fontsize{10.5pt}{19pt}\selectfont '
OPT_S = r'\par}'
BINDP = r'\bindp '

# ---------- 题1〔选择〕考点一·例1（题面 L106–114） ----------
l106 = r'\tjdnr{一}{空间向量的概念辨析}{例\textbf{1}}{简单(知识点一)}{下列说法正确的是\nobreak(\kongwei)}'
expect(106, l106)
stem1 = last_arg(l106)
l108 = r'\bindopt {\fontsize{10.5pt}{19pt}\selectfont A．若\(| \overrightarrow{a} | = | \overrightarrow{b} |\)，则\nobreak\(\overrightarrow{a} = \overrightarrow{b}\)或\(\overrightarrow{a} = - \overrightarrow{b}\)；\par}'
expect(108, l108)
o1a = cut(l108, OPT_P, OPT_S)
l110 = r'\bindopt {\fontsize{10.5pt}{19pt}\selectfont B．若\(\overrightarrow{a},\overrightarrow{b}\)为相反向量，则\nobreak\(\overrightarrow{a} + \overrightarrow{b} = \overrightarrow{0}\)；\par}'
expect(110, l110)
o1b = cut(l110, OPT_P, OPT_S)
l112 = r'\bindopt {\fontsize{10.5pt}{19pt}\selectfont C．零向量是没有方向的向量；\par}'
expect(112, l112)
o1c = cut(l112, OPT_P, OPT_S)
l114 = r'\bindopt {\fontsize{10.5pt}{19pt}\selectfont D．若\(\overrightarrow{a},\overrightarrow{b}\)是两个单位向量，则\nobreak\(\overrightarrow{a} = \overrightarrow{b}\)\par}'
expect(114, l114)
o1d = cut(l114, OPT_P, OPT_S)
l118 = r'\bindp [详解]解：若\(| \overrightarrow{a} | = | \overrightarrow{b} |\)，则它们的方向相同时是相等向量，方向相反时是相反向量，还有可能方向既不相同，也不相反，A错；'
expect(118, l118)
l120 = r'\bindp 若\(\overrightarrow{a},\overrightarrow{b}\)为相反向量，则它们的和为零向量，B对；'
expect(120, l120)
l122 = r'\bindp 零向量的方向是任意的，C错；'
expect(122, l122)
l124 = r'\bindp 两个单位向量只是模都为1，方向不一定相同，D错.故选：B.'
expect(124, l124)
val1 = '故选：B.'
assert val1 in l124

# ---------- 题2〔选择〕考点一·变式1（题面 L126–134） ----------
l126 = r'\liB{变式\textbf{1}}{简单(知识点一)}{}{下列说法错误的是\nobreak(\kongwei)}'
expect(126, l126)
stem2 = last_arg(l126)
l128 = r'\bindopt {\fontsize{10.5pt}{19pt}\selectfont A．零向量与任意向量都平行；\par}'
expect(128, l128)
o2a = cut(l128, OPT_P, OPT_S)
l130 = r'\bindopt {\fontsize{10.5pt}{19pt}\selectfont B．若\(|\overrightarrow{a}|=0\)，则\nobreak\(\overrightarrow{a}=\overrightarrow{0}\)；\par}'
expect(130, l130)
o2b = cut(l130, OPT_P, OPT_S)
l132 = r'\bindopt {\fontsize{10.5pt}{19pt}\selectfont C．若\(\overrightarrow{a}=\overrightarrow{b}\)，则\nobreak\(|\overrightarrow{a}|=|\overrightarrow{b}|\)；\par}'
expect(132, l132)
o2c = cut(l132, OPT_P, OPT_S)
l134 = r'\bindopt {\fontsize{10.5pt}{19pt}\selectfont D．若\(\overrightarrow{a}\parallel\overrightarrow{b}\)，则\nobreak\(|\overrightarrow{a}|=|\overrightarrow{b}|\)\par}'
expect(134, l134)
o2d = cut(l134, OPT_P, OPT_S)
l136 = r'\ansline{\ansul{D}}'
expect(136, l136)
val2 = l136
l138 = r'\jiexi{A规定成立；B模为0即零向量；C相等必等模；D平行不需等模(反例\(\overrightarrow{a}=2\overrightarrow{b}\))，故选D.}'
expect(138, l138)
ana2 = l138

# ---------- 题3〔填空〕考点二·例1（题面 L146；插图嵌于 L150 详解行） ----------
l146 = r'\tjdnr{二}{空间向量的线性运算}{例\textbf{1}}{简单(知识点二)}{在直三棱柱\(ABC\text{-}\penalty100 A_{1}B_{1}C_{1}\)中，若\(\overrightarrow{CA} = \overrightarrow{a},\overrightarrow{CB} = \overrightarrow{b},\overrightarrow{CC_{1}} = \overrightarrow{c},\)，则\nobreak\(\overrightarrow{A_{1}B}\)=\kongbai{}.(用\(\overrightarrow{a},\overrightarrow{b},\overrightarrow{c}\)表示)}'
expect(146, l146)
stem3 = last_arg(l146)
l150 = r'\noindent\begin{minipage}[t]{48.000mm}\raggedright [详解]连接\(CA_{1},\)则\nobreak\(\overrightarrow{A_{1}B} = \overrightarrow{CB} - \overrightarrow{CA_{1}} = \overrightarrow{CB} - \overrightarrow{CA} - \overrightarrow{CC_{1}} =\overrightarrow{b} - \overrightarrow{a} - \overrightarrow{c}\).\end{minipage}\hspace{5.342mm}\begin{minipage}[t]{28.800mm}\centering\raisebox{\dimexpr-\height+3.332mm\relax}[\dimexpr3.332mm\relax][\dimexpr\height-3.332mm\relax]{\includegraphics[width=28.800mm,alt={@@@4e3aa752498e415b9cc3d6d60f7bb3fe}]{media/media/image1.png}}\end{minipage}\par'
expect(150, l150)
det3 = l150
l152 = r'\bindp 故答案为：\(\overrightarrow{b} - \overrightarrow{a} - \overrightarrow{c}\)'
expect(152, l152)
val3 = cut(l152, BINDP)

# ---------- 题4〔填空〕考点二·变式1（题面 L154） ----------
l154 = r'\liB{变式\textbf{1}}{简单(知识点二)}{}{在平行六面体\(ABCD\text{-}\penalty100 A_1B_1C_1D_1\)中，\(\overrightarrow{AB}=\overrightarrow{a}\)，\(\overrightarrow{AD}=\overrightarrow{b}\)，\(\overrightarrow{AA_1}=\overrightarrow{c}\)，则\nobreak\(\overrightarrow{D_1B}=\)\kongbai{}.(用\(\overrightarrow{a}\)，\(\overrightarrow{b}\)，\(\overrightarrow{c}\)表示)}'
expect(154, l154)
stem4 = last_arg(l154)
l156 = r'\ansline{\ansul{\(\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\)}}'
expect(156, l156)
val4 = l156
l158 = r'\jiexi{\(\overrightarrow{D_1B}=\overrightarrow{D_1A_1}+\overrightarrow{A_1A}+\overrightarrow{AB}=-\overrightarrow{b}-\overrightarrow{c}+\overrightarrow{a}\).}'
expect(158, l158)
ana4 = l158

# ---------- 题5〔解答·判断说理〕考点四·变式1（题面 L202） ----------
l202 = r'\liB{变式\textbf{1}}{简单(知识点三)}{}{已知\(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\)，判断\(P\)，\(M\)，\(A\)，\(B\)四点是否共面，并说明理由.}'
expect(202, l202)
stem5 = last_arg(l202)
l204 = r'\ansline{\ansul{共面}(\(\overrightarrow{MP}\)可由\(\overrightarrow{MA}\)，\(\overrightarrow{MB}\)线性表示，故\(\overrightarrow{MP}\)，\(\overrightarrow{MA}\)，\(\overrightarrow{MB}\)共面，即\(P\)在平面\(MAB\)内)}'
expect(204, l204)
val5 = l204
l206 = r'\jiexi{\(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\)为\(\overrightarrow{MA}\)、\(\overrightarrow{MB}\)的线性组合，故三向量共面，\(P\)在平面\(MAB\)内.}'
expect(206, l206)
ana5 = l206

# ---------- 题6〔解答〕考点六·例1（题面 L246、图 L248） ----------
l246 = r'\tjdnr{六}{数量积求夹角与投影}{例\textbf{1}}{中档(知识点三)}{如图，在正方体\(ABCD\text{-}\penalty100 A_{1}B_{1}C_{1}D_{1}\)中，求向量\(\overrightarrow{BC_{1}}\)与\(\overrightarrow{AC}\)的夹角的大小.}'
expect(246, l246)
stem6 = last_arg(l246)
l248 = r'\bindp \par\vspace{1.9mm}\penalty10000\noindent\makebox[\linewidth][c]{\includegraphics[width=54.1mm]{media/media/image3.png}}\par\vspace{-1.0mm}\penalty10000'
expect(248, l248)
fig6 = cut(l248, BINDP)
l254 = r'\bindp [详解]解：方法1：因为\(\overrightarrow{AD_{1}} = \overrightarrow{BC_{1}}\)，所以\(\angle CAD_{1}\)的大小就等于\(\langle \overrightarrow{BC_{1}},\overrightarrow{AC} \rangle\)'
expect(254, l254)
l256 = r'\bindp 因为△\(CAD_{1}\)为等边三角形，所以\(\angle CAD_{1} = 60^{{^\circ}}\)，所以\(\overrightarrow{BC_{1}}\)与\(\overrightarrow{AC}\)的夹角的大小为\(60{^\circ}\).'
expect(256, l256)
l258 = r'\bindp 方法2．设正方体的棱长为1，\(\overrightarrow{BC_{1}} \cdot \overrightarrow{AC} = ( \overrightarrow{BC} + \overrightarrow{CC_{1}} ) \cdot ( \overrightarrow{AB} + \overrightarrow{BC} ) = ( \overrightarrow{AD} + \overrightarrow{AA_{1}} ) \cdot ( \overrightarrow{AB} + \overrightarrow{AD} )\)\allowbreak\(= \overrightarrow{AD} \cdot \overrightarrow{AB} + | \overrightarrow{AD} |^{2} + \overrightarrow{AA_{1}} \cdot \overrightarrow{AB} + \overrightarrow{AA_{1}} \cdot \overrightarrow{AD} = 0 + | \overrightarrow{AD} |^{2} + 0 + 0 = | \overrightarrow{AD} |^{2} = 1\)又因为\(| \overrightarrow{BC_{1}} | = \sqrt{2},| \overrightarrow{AC} | = \sqrt{2}\)，所以\(\cos\langle \overrightarrow{BC_{1}},\overrightarrow{AC} \rangle = \frac{\overrightarrow{BC_{1}} \cdot \overrightarrow{AC}}{| \overrightarrow{BC_{1}} | \cdot | \overrightarrow{AC} |} = \frac{1}{\sqrt{2} \times \sqrt{2}} = \frac{1}{2}\)，'
expect(258, l258)
l259 = r'因为\(\langle \overrightarrow{BC_{1}},\overrightarrow{AC} \rangle \in \lbrack 0,\pi\rbrack\)，所以\(\overrightarrow{BC_{1}}\)与\(\overrightarrow{AC}\)的夹角的大小为\(60{^\circ}\).'
expect(259, l259)
val6 = r'\(60{^\circ}\)'
assert val6 in l256 and val6 in l259

# ---------- 组装盲解版 ----------
BLIND_HEAD = r"""# 逻辑闸试点0911（二期）· 题目-盲解版

> 题源：`工作区/字替对照-0909/variantF/body.tex`（2026-09-11 现盘；逐题行号见同目录《抽取说明-二期.md》）。
> 抽样口径：选择2＋填空2＋解答2，三类各取源件出现序前2，难度不挑、无随机；〔　〕内为作答形式指称，非源件标签。
> 本件只含题面（题号＋题干＋选项/小问），逐字照抄、数学式 LaTeX 原样；一切判分信息（判分值串、策略段、演算段、提示段、方法小结段、难度/考点标签、方法标签行）已剔除；纯排版包装（选项/段落前缀宏、字号包装、段尾宏、题号宏外壳）已剥离，内容宏（\nobreak、\kongwei、\kongbai、\penalty 等）原样保留。

"""

def section(title, paras):
    out = '## ' + title + '\n\n'
    out += '\n\n'.join(paras) + '\n\n'
    return out

blind_parts = [
    section('题1〔选择〕（考点一·例1）', [stem1, o1a, o1b, o1c, o1d]),
    section('题2〔选择〕（考点一·变式1）', [stem2, o2a, o2b, o2c, o2d]),
    section('题3〔填空〕（考点二·例1）', [stem3]),
    section('题4〔填空〕（考点二·变式1）', [stem4]),
    section('题5〔解答·判断说理〕（考点四·变式1）', [stem5]),
    section('题6〔解答〕（考点六·例1）', [stem6, fig6]),
]
blind_text = BLIND_HEAD + ''.join(blind_parts)

# ---------- 组装裁判版 ----------
JUDGE_HEAD = r"""# 逻辑闸试点0911（二期）· 答案-裁判版

> 题源：`工作区/字替对照-0909/variantF/body.tex`（2026-09-11 现盘）；题号与《题目-盲解版》一一对应。
> 收录口径（沿一期）：判分值串（源件原样，含「故选：」「\ansul{…}」原包装）＋[详解]/解析段整行照抄；[分析]、[点睛]、方法小结段（①识别/②操作/③收束）未收录，原文仍在源件可查。
> 本件全部引串经提取器断言「⊂ 源件」逐字节成立，无手工转抄（见《抽取说明-二期.md》§三）。

"""

def bullet(label, s):
    return '- ' + label + '：`' + s + '`\n'

judge_parts = []
judge_parts.append('## 题1〔选择〕（考点一·例1｜题面 L106、L108–114）\n\n')
judge_parts.append(bullet('判分值串（L124 内原样）', val1))
judge_parts.append('- 演算段（整行照抄）：\n')
for n, s in [(118, l118), (120, l120), (122, l122), (124, l124)]:
    judge_parts.append('  - L%d：`%s`\n' % (n, s))
judge_parts.append('\n## 题2〔选择〕（考点一·变式1｜题面 L126、L128–134）\n\n')
judge_parts.append(bullet('判分值串（L136 整行）', val2))
judge_parts.append(bullet('解析段（L138 整行）', ana2))
judge_parts.append('\n## 题3〔填空〕（考点二·例1｜题面 L146）\n\n')
judge_parts.append(bullet('判分值串（L152 内原样，剥 \\bindp 前缀）', val3))
judge_parts.append(bullet('演算段（L150 整行照抄；行内并排插图 media/media/image1.png）', det3))
judge_parts.append('\n## 题4〔填空〕（考点二·变式1｜题面 L154）\n\n')
judge_parts.append(bullet('判分值串（L156 整行）', val4))
judge_parts.append(bullet('解析段（L158 整行）', ana4))
judge_parts.append('\n## 题5〔解答·判断说理〕（考点四·变式1｜题面 L202）\n\n')
judge_parts.append(bullet('判分值串（L204 整行）', val5))
judge_parts.append(bullet('解析段（L206 整行）', ana5))
judge_parts.append('\n## 题6〔解答〕（考点六·例1｜题面 L246、图 L248）\n\n')
judge_parts.append(bullet('判分值串（L256／L259 内原样）', val6))
judge_parts.append('- 演算段（整行照抄）：\n')
for n, s in [(254, l254), (256, l256), (258, l258), (259, l259)]:
    judge_parts.append('  - L%d：`%s`\n' % (n, s))
judge_text = JUDGE_HEAD + ''.join(judge_parts)

# ---------- 自检断言 ----------
labels_blind = ['题1', '题2', '题3', '题4', '题5', '题6']
labels_judge = ['题1', '题2', '题3', '题4', '题5', '题6']
assert blind_text.count('\n## 题') == 6 and judge_text.count('\n## 题') == 6
assert all(lbl in blind_text for lbl in labels_blind) and all(lbl in judge_text for lbl in labels_judge)

FORBID = ['答案', '分析', '详解', '点睛', '解析', '题型']
hit = [w for w in FORBID if w in blind_text]
assert not hit, '盲解版禁词命中: %r' % hit
LABELS = ['知识点', '简单', '中档', '\\tjdnr', '\\liB', '\\bindp', '\\bindopt', '\\ansul', '\\ansline', '\\jiexi']
hit2 = [w for w in LABELS if w in blind_text]
assert not hit2, '盲解版标签/宏残留: %r' % hit2

blind_strings = [stem1, o1a, o1b, o1c, o1d, stem2, o2a, o2b, o2c, o2d,
                 stem3, stem4, stem5, stem6, fig6]
for s in blind_strings:
    assert s in src, '盲解题面串不在源件: %r' % s[:40]

judge_values = [val1, val2, val3, val4, val5, val6]
judge_details = [l118, l120, l122, l124, l136, l138, l150, l152, l156, l158, l204, l206, l254, l256, l258, l259]
for s in judge_values + judge_details:
    assert s in src, '裁判版引串不在源件: %r' % s[:40]
for s in judge_values + judge_details:
    assert s not in blind_text, '裁判版引串泄漏进盲解版: %r' % s[:40]

with open(os.path.join(HERE, '题目-盲解版.md'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(blind_text)
with open(os.path.join(HERE, '答案-裁判版.md'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(judge_text)

print('OK 全部断言通过')
print('盲解版题数=6，裁判版题数=6，题号一一对应:', labels_blind == labels_judge)
print('盲解版禁词命中（答案/分析/详解/点睛/解析/题型）:', hit if hit else '0')
print('盲解题面串⊂源件: %d/%d' % (len(blind_strings), len(blind_strings)))
print('裁判版值串⊂源件: %d/%d' % (len(judge_values), len(judge_values)))
print('裁判版解析/演算串⊂源件: %d/%d' % (len(judge_details), len(judge_details)))
print('判分值串⊄盲解版: %d/%d' % (len(judge_values), len(judge_values)))
