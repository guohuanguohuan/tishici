# -*- coding: utf-8 -*-
"""生成 _tabcal2.tex（表2 内容：单行格 共线行 E/struts 标定；临时产物仅本目录）。"""
rows = [
 ('加法', r'三角形法则／平行四边形法则(与平面向量一致) ', r'\(\overrightarrow{a}+\overrightarrow{b}=\overrightarrow{b}+\overrightarrow{a}\)'),
 ('减法', r'减向量终点指向被减向量终点', r'\((\overrightarrow{a}+\overrightarrow{b})+\overrightarrow{c}=\overrightarrow{a}+(\overrightarrow{b}+\overrightarrow{c})\)'),
 ('数乘', r'实数\(\lambda\)与向量\(\overrightarrow{a}\)的乘积仍为向量', r'\((\lambda+\mu)\overrightarrow{a}=\lambda\overrightarrow{a}+\mu\overrightarrow{a}\)'),
 ('共线', r'\(\overrightarrow{a}\parallel\overrightarrow{b}\)(\(\overrightarrow{b}\neq\overrightarrow{0}\)) ', r'\(\overrightarrow{a}=\lambda\overrightarrow{b}\)'),
]
head = r'\makebox[\linewidth]{\textbf{运算}} & \makebox[\linewidth]{\textbf{法则要点}} & \makebox[\linewidth]{\textbf{运算律举例}}'
colspec = (r'{!{\vline width 0.8pt}>{\fontsize{10.5pt}{13.9pt}\selectfont\centering\arraybackslash}m{10mm}'
           r'!{\vline width 0.4pt}>{\fontsize{10.5pt}{13.9pt}\selectfont}m{37mm}'
           r'!{\vline width 0.4pt}>{\fontsize{10.5pt}{13.9pt}\selectfont}m{28.6mm}!{\vline width 0.8pt}}')
BS = '\\' * 2


def table(E, G, Gh, last_pre='', last_G=None):
    L = [r'{\setlength{\tabcolsep}{3pt}\arrayrulecolor{gray122}', r'\vspace{2.55mm}',
         r'\noindent\begin{tabular}' + colspec, r'\thickhline',
         head + ' ' + BS + '[' + Gh + ']', r'\hline']
    n = len(rows)
    for i, (a, b, c) in enumerate(rows):
        gg = last_G if (i == n - 1 and last_G) else G
        pre = last_pre if i == n - 1 else ''
        tail = ' ' + BS + '[' + gg + ']'
        L.append(pre + f'{a}&{b}&{c}' + (tail + ' \\hline' if i < n - 1 else tail))
    L += [r'\thickhline', r'\end{tabular}\par\addvspace{2.8mm}', '}']
    return '\n'.join(L)


variants = [
    ('X1', '1.5mm', '4.35mm', '0.45mm', '', '0.45mm'),
    ('X2', '1.5mm', '4.35mm', '0.45mm', r'\noalign{\tabstrutht{4.02mm}}', '0.45mm'),
    ('X3', '0.4mm', '4.35mm', '0.45mm', '', '0.45mm'),
    ('X4', '1.5mm', '4.35mm', '0.45mm', r'\noalign{\tabstrutht{2.5mm}}', '1.2mm'),
]
out = [r'\documentclass[fontset=none]{ctexart}',
       r'\input{qp-fonts.tex}', r'\input{qp-layout.tex}', r'\input{qp-parts.tex}',
       r'\input{qp-headfoot.tex}', r'\input{qp-titles.tex}', r'\input{qp-blocks.tex}',
       r'\makeatletter',
       r'\newcommand{\tabstrutht}[1]{\global\ht\@arstrutbox=#1\relax}',
       r'\makeatother',
       r'\begin{document}']
for name, E, G, Gh, pre, lG in variants:
    out.append(r'\noindent\textbf{' + name + r' E=' + E + r' G=' + G + r' Gh=' + Gh + r' pre=' + (pre or '-') + r' lG=' + lG + r'}\par')
    out.append(r'\setlength{\extrarowheight}{' + E + '}')
    out.append(table(E, G, Gh, pre, lG))
    out.append(r'\par\vspace{6mm}')
out.append(r'\end{document}')
open('_tabcal2.tex', 'w', encoding='utf-8').write('\n'.join(out))
print('written _tabcal2.tex')
