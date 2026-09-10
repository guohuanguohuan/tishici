# -*- coding: utf-8 -*-
"""片H2 脚本档探针：\DeclareMathSizes 路线（脚本比例 0.54）。"""
import os
import shutil
import subprocess

VF = r'C:/提示词/工作区/字替对照-0909/variantF'
OUT = r'C:/提示词/工作区/_tmp取证0909c/片H2/探针'


def build(tag, preamble_extra):
    src = open(f'{OUT}/probe_t5.tex', encoding='utf-8').read()
    src = src.replace('\\let\\frac\\dfrac', '')
    src = src.replace('\\setmathfont{texgyretermes-math.otf}[Scale=1.08,ScriptPercentScaleDown=54,ScriptScriptPercentScaleDown=45]',
                      '\\setmathfont{texgyretermes-math.otf}[Scale=1.08]')
    src = src.replace('\\begin{document}', preamble_extra + '\n\\begin{document}')
    stem = f'_h2probe_{tag}'
    open(os.path.join(VF, stem + '.tex'), 'w', encoding='utf-8').write(src)
    r = subprocess.run(['xelatex', '-interaction=nonstopmode', stem + '.tex'],
                       cwd=VF, capture_output=True, text=True, encoding='utf-8', errors='replace')
    log = r.stdout + r.stderr
    open(f'{OUT}/probe_{tag}.xlog', 'w', encoding='utf-8').write(log)
    for ext in ('pdf', 'log', 'aux'):
        p = os.path.join(VF, f'{stem}.{ext}')
        if os.path.exists(p):
            shutil.copy(p, os.path.join(OUT, f'probe_{tag}.{ext}'))
    open(f'{OUT}/probe_{tag}.tex', 'w', encoding='utf-8').write(src)
    for ext in ('tex', 'pdf', 'log', 'aux'):
        p = os.path.join(VF, f'{stem}.{ext}')
        if os.path.exists(p):
            os.remove(p)
    errs = [l for l in log.splitlines() if l.startswith('!')]
    print(tag, 'rc', r.returncode, 'errors', len(errs), errs[:3])


if __name__ == '__main__':
    build('t13', r'\DeclareMathSizes{10.09}{10.09}{5.45}{4.54}' + '\n' + r'\normalsize')
    build('t14', r'\DeclareMathSizes{10}{10}{3}{3}' + '\n' + r'\normalsize')
    build('t15', r'\DeclareMathSizes{10.09}{10.09}{5.45}{4.54}' + '\n' + r'\normalsize' + '\n' + r'\let\frac\dfrac')
