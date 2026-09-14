# -*- coding: utf-8 -*-
"""_probe_under2.py — Overfull 消位探针第二轮（过程件）。"""
import os
import re
import subprocess

D = os.path.dirname(os.path.abspath(__file__))
XE = 'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex.exe'
SHELL = open(os.path.join(D, 'ansbook-true.tex'), encoding='utf-8').read()
body = open(os.path.join(D, 'ansbook.tex'), encoding='utf-8').read()


def go(name, b):
    open(os.path.join(D, name + '_body.tex'), 'w', encoding='utf-8', newline='\n').write(b)
    sh = SHELL.replace('\\input{ansbook.tex}', '\\input{' + name + '_body.tex}')
    open(os.path.join(D, name + '.tex'), 'w', encoding='utf-8', newline='\n').write(sh)
    subprocess.run([XE, '-interaction=nonstopmode', name + '.tex'], cwd=D,
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
    log = open(os.path.join(D, name + '.log'), encoding='utf-8', errors='replace').read()
    m = re.search(r'Overfull \vbox \(([\d.]+)pt', log)
    print(name, 'overfull=', log.count('Overfull'), 'under=', log.count('Underfull'),
          (m.group(1) + 'pt' if m else ''))


KNOB = ('\\ansblockgrayfalse\n'
        '\\multicolundershoot=14pt\n\\multicolovershoot=14pt%\n')
go('probeV', body.replace('\\ansblockgrayfalse', KNOB))                      # 双旋钮 14pt
go('probeW', body.replace('\\tailfill', '\\columnbreak\\tailfill'))          # 逃生口于尾块前
go('probeX', body.replace('\\emergencystretch=1em',
                          '\\emergencystretch=1em\\raggedbottom'))           # 栏内 raggedbottom
go('probeY', body.replace('\\begin{multicols}{2}',
                          '\\begin{multicols}{2}[10mm]'))                    # 预留末栏 10mm
