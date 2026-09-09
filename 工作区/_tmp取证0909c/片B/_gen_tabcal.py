# -*- coding: utf-8 -*-
"""生成 _tabcal.tex（表格 E/G/格内垫 标定矩阵；临时产物仅本目录）。"""
rows = [
 ('零向量', r'长度为\kongda{0}的向量叫做零向量', r'记作\kongda{0}'),
 ('单位向量', r'模等于\kongda{1}的向量', r'用\(e\)表示，\(|e|=1\)'),
 ('相反向量', r'与\(\overrightarrow{a}\)长度相同而方向\kongda{相反}的向量', r'记作\(-\overrightarrow{a}\)'),
 ('共线向量或平行向量', r'表示若干空间向量的有向线段所在的直线\kongda{互相平行}或\kongda{重合} ', r'记作\(\overrightarrow{a}\parallel\overrightarrow{b}\)'),
 ('相等向量', r'方向相同且\kongda{模相等}的向量', r'记作\(\overrightarrow{a}=\overrightarrow{b}\)'),
]
head = r'\makebox[\linewidth]{\textbf{名称}} & \makebox[\linewidth]{\textbf{定义}} & \makebox[\linewidth]{\textbf{表示}}'
colspec = (r'{!{\vline width 0.8pt}>{\fontsize{10.5pt}{13.9pt}\selectfont\centering\arraybackslash}m{16mm}'
           r'!{\vline width 0.4pt}>{\fontsize{10.5pt}{13.9pt}\selectfont}m{35mm}'
           r'!{\vline width 0.4pt}>{\fontsize{10.5pt}{13.9pt}\selectfont}m{26.7mm}!{\vline width 0.8pt}}')
BS = '\\' * 2


def table(E, G, Gh, top=None, bot=None):
    L = [r'{\setlength{\tabcolsep}{2pt}\arrayrulecolor{gray122}', r'\vspace{2.55mm}',
         r'\noindent\begin{tabular}' + colspec, r'\thickhline',
         head + ' ' + BS + '[' + Gh + ']', r'\hline']
    for i, (a, b, c) in enumerate(rows):
        tail = ' ' + BS + '[' + G + ']'
        if top or bot:
            def wrap(s):
                pre = r'\rule{0pt}{' + top + r'}' if top else ''
                suf = r'\rule[-' + bot + r']{0pt}{0pt}' if bot else ''
                return pre + s + suf
            a, b, c = wrap(a), wrap(b), wrap(c)
        L.append(f'{a}&{b}&{c}' + (tail + ' \\hline' if i < len(rows) - 1 else tail))
    L += [r'\thickhline', r'\end{tabular}\par\addvspace{2.8mm}', '}']
    return '\n'.join(L)


variants = [
    ('W1', '0.4mm', '0.45mm', '0.45mm', '5.5mm', None),
    ('W2', '0.4mm', '0.45mm', '0.45mm', '5.5mm', '2.0mm'),
    ('W3', '0.4mm', '0.45mm', '0.45mm', '5.5mm', '3.5mm'),
    ('W4', '1.5mm', '4.35mm', '0.45mm', None, None),
    ('W5', '1.65mm', '4.35mm', '0.32mm', None, None),
    ('W6', '1.5mm', '4.35mm', '0.45mm', None, None),
]
out = [r'\documentclass[fontset=none]{ctexart}',
       r'\input{qp-fonts.tex}', r'\input{qp-layout.tex}', r'\input{qp-parts.tex}',
       r'\input{qp-headfoot.tex}', r'\input{qp-titles.tex}', r'\input{qp-blocks.tex}',
       r'\begin{document}']
for name, E, G, Gh, top, bot in variants:
    out.append(r'\noindent\textbf{' + name + r' E=' + E + r' G=' + G + r' Gh=' + Gh +
               r' top=' + (top or '-') + r' bot=' + (bot or '-') + r'}\par')
    out.append(r'\setlength{\extrarowheight}{' + E + '}')
    out.append(table(E, G, Gh, top, bot))
    out.append(r'\par\vspace{6mm}')
out.append(r'\end{document}')
open('_tabcal.tex', 'w', encoding='utf-8').write('\n'.join(out))
print('written _tabcal.tex')
