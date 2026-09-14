# -*- coding: utf-8 -*-
"""_probe_under3.py — 尾块形态归因探针第三轮（过程件）。"""
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
    import fitz
    d = fitz.open(os.path.join(D, name + '.pdf'))
    n = len(d)
    last = d[n - 1].get_text()[:24].replace('\n', '|')
    d.close()
    print(name, 'overfull=', log.count('Overfull'), 'pages=', n,
          'last=', last, (m.group(1) + 'pt' if m else ''))


go('probeZ', body.replace('\\tailfill\n', ''))                 # 无尾块
go('probeT', body.replace('\\tailfill', '\\tailfill[30mm]'))   # 定高 30mm
go('probeS', body.replace('\\tailfill', '\\tailfill[8mm]'))    # 定高 8mm
