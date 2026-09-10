# -*- coding: utf-8 -*-
"""减号形态探针：在 VF 内编译 probe_minus 变体（\medmuskip 三档）。"""
import os
import shutil
import subprocess

VF = r'C:/提示词/工作区/字替对照-0909/variantF'
OUT = r'C:/提示词/工作区/_tmp取证0909c/片H2/探针'
src0 = open(f'{OUT}/probe_minus.tex', encoding='utf-8').read()

for tag, medmu in (('m0', r'\medmuskip=0mu'), ('m1', r'\medmuskip=1mu'), ('m2', r'\medmuskip=2mu'),
                   ('m3', r'\medmuskip=2mu plus 1mu minus 2mu')):
    src = src0.replace('@@MEDMU@@', medmu)
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
    print(tag, 'rc', r.returncode, 'errors', len(errs))
