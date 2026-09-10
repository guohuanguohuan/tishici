# -*- coding: utf-8 -*-
"""片H2 探针驱动：生成探针 tex（数学档×减号档×分式档）→ xelatex 编译 → 360dpi 渲染。
用法：python _probe_run.py <tag> "<mathline>" "<medmu>" "<fracline>"
例：  python _probe_run.py p2 "\\setmathfont{texgyretermes-math.otf}[Scale=1.08,ScriptPercentScaleDown=54,ScriptScriptPercentScaleDown=45]" "" ""
"""
import os
import subprocess
import sys

VF = r'C:/提示词/工作区/字替对照-0909/variantF'
OUT = r'C:/提示词/工作区/_tmp取证0909c/片H2/探针'

TEMPLATE = r'''\documentclass[fontset=none]{ctexart}
\input{qp-fonts.tex}
\input{qp-layout.tex}
% ---- 探针开关（生成注入） ----
@@MATH@@
@@MEDMU@@
@@FRAC@@
\begin{document}
\noindent TAG=@@TAG@@

\noindent 在平行六面体\(ABCD-A_1B_1C_1D_1\)中，点\(E\)在\(A_1C_1\)上，且\(\overrightarrow{A_1E}=\frac{1}{2}\overrightarrow{A_1C_1}\)，若\(\overrightarrow{AE}=x\overrightarrow{AA_1}\)，求\(xy+yz\)的最大值。

\noindent \(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\)，则\(P\)，\(M\)，\(A\)，\(B\)四点是否共面？已知\(MP=3MA-2MB\)的取值。

\noindent 故答案为\(x=1\)，\(y=\frac{1}{4}\)。所以\(\cos\langle \overrightarrow{AB_1},\overrightarrow{AC}\rangle=\frac{4}{\sqrt{5}\times2\sqrt{2}}=\frac{\sqrt{10}}{5}\)。

\noindent 【详解】方法2．设正方体的棱长为1，\(\overrightarrow{BC_{1}} \cdot \overrightarrow{AC} = ( \overrightarrow{BC} + \overrightarrow{CC_{1}} ) \cdot ( \overrightarrow{AB} + \overrightarrow{BC} )\)，则\(AM = \frac{1}{2}\)，\(BM = \frac{\sqrt{3}}{2}\)，\(CN = \frac{1}{2}\)。

\noindent 已知\(AB=3\)，\(AD=2\)，\(AA_1=1\)，\(| \overrightarrow{a} |\cos\langle \overrightarrow{a},\overrightarrow{b} \rangle \cdot \frac{\overrightarrow{b}}{| \overrightarrow{b} |}\)，\(\lambda=-1-\sqrt{3}\)。

\noindent 测甲\(ABCD-A_1B_1C_1D_1\)测乙

\noindent 测甲\(\frac{1}{4}\)测乙\(\frac{\sqrt{10}}{5}\)测丙\(\frac{\overrightarrow{b}}{| \overrightarrow{b} |}\)测丁

\noindent 测甲\(3\overrightarrow{MA}-2\overrightarrow{MB}\)测乙\(| \overrightarrow{a} |\cos\langle \overrightarrow{a},\overrightarrow{b} \rangle\)测丙
\end{document}
'''


def run(tag, mathline='', medmu='', fracline=''):
    import shutil
    src = (TEMPLATE.replace('@@TAG@@', tag).replace('@@MATH@@', mathline)
           .replace('@@MEDMU@@', medmu).replace('@@FRAC@@', fracline))
    # 在 VF 内编译（fonts/ 相对路径），瞬态文件 run 后移入探针目录
    stem = f'_h2probe_{tag}'
    vftex = os.path.join(VF, stem + '.tex')
    open(vftex, 'w', encoding='utf-8').write(src)
    cmd = ['xelatex', '-interaction=nonstopmode', stem + '.tex']
    r = subprocess.run(cmd, cwd=VF, capture_output=True, text=True, encoding='utf-8', errors='replace')
    log = r.stdout + r.stderr
    open(os.path.join(OUT, f'probe_{tag}.xlog'), 'w', encoding='utf-8').write(log)
    for ext in ('pdf', 'log', 'aux'):
        s_ = os.path.join(VF, f'{stem}.{ext}')
        if os.path.exists(s_):
            shutil.copy(s_, os.path.join(OUT, f'probe_{tag}.{ext}'))
    open(os.path.join(OUT, f'probe_{tag}.tex'), 'w', encoding='utf-8').write(src)
    for ext in ('tex', 'pdf', 'log', 'aux'):
        f_ = os.path.join(VF, f'{stem}.{ext}')
        if os.path.exists(f_):
            os.remove(f_)
    errs = [l for l in log.splitlines() if l.startswith('!')]
    ovf = [l for l in log.splitlines() if 'Overfull' in l]
    print(f'[{tag}] rc={r.returncode} errors={len(errs)} overfull={len(ovf)}')
    for l in errs[:5]:
        print('   ', l)
    for l in ovf[:5]:
        print('   ', l)
    return r.returncode == 0 and not errs


if __name__ == '__main__':
    a = sys.argv[1:]
    tag = a[0]
    mathline = a[1] if len(a) > 1 else ''
    medmu = a[2] if len(a) > 2 else ''
    fracline = a[3] if len(a) > 3 else ''
    run(tag, mathline, medmu, fracline)
