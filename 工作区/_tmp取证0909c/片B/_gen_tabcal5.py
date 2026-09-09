# -*- coding: utf-8 -*-
"""生成 _tabcal5.tex：TeX 侧 \prevgraf 行数自动选行尾胶（临时产物仅本目录）。"""
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

PRE = [r'\newcount\rowmax', r'\newcount\celllines',
       r'\def\rowreset{\global\rowmax=0 }',
       r'\def\marklines{\par\celllines=\prevgraf\relax',
       r'  \ifnum\celllines>\rowmax \global\rowmax=\celllines \fi}',
       r'\def\tabrowglue{\ifnum\rowmax>2 7.30mm\else\ifnum\rowmax>1 4.35mm\else 0.45mm\fi\fi}']


def table(E, Gh, auto=True):
    L = [r'{\setlength{\tabcolsep}{3pt}\arrayrulecolor{gray122}', r'\vspace{2.55mm}',
         r'\noindent\begin{tabular}' + colspec, r'\thickhline',
         head + ' ' + BS + '[' + Gh + ']', r'\hline']
    for i, (a, b, c) in enumerate(rows):
        tail = ' ' + BS + r'[\tabrowglue]' if auto else ' ' + BS + '[4.35mm]'
        if auto:
            a, b, c = r'\rowreset ' + a + r'\marklines', b + r'\marklines', c + r'\marklines'
        L.append(f'{a}&{b}&{c}' + (tail + ' \\hline' if i < len(rows) - 1 else tail))
    L += [r'\thickhline', r'\end{tabular}\par\addvspace{2.8mm}', '}']
    return '\n'.join(L)


out = [r'\documentclass[fontset=none]{ctexart}',
       r'\input{qp-fonts.tex}', r'\input{qp-layout.tex}', r'\input{qp-parts.tex}',
       r'\input{qp-headfoot.tex}', r'\input{qp-titles.tex}', r'\input{qp-blocks.tex}'] + PRE + [r'\begin{document}']
out.append(r'\noindent\textbf{A1 E=1.5mm auto}\par')
out.append(r'\setlength{\extrarowheight}{1.5mm}')
out.append(table('1.5mm', '0.45mm', True))
out.append(r'\par\vspace{6mm}')
out.append(r'\noindent\textbf{A2 E=1.5mm fixed435}\par')
out.append(r'\setlength{\extrarowheight}{1.5mm}')
out.append(table('1.5mm', '0.45mm', False))
out.append(r'\par\vspace{6mm}')
out.append(r'\end{document}')
open('_tabcal5.tex', 'w', encoding='utf-8').write('\n'.join(out))
print('written _tabcal5.tex')
