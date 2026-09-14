# -*- coding: utf-8 -*-
"""扫 \tailfill[高度] 在 false 档的 ovf/页数读数（诊断件，跑完即弃）。"""
import io
import os
import re
import subprocess
import sys

BS = chr(92)
X = 'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex'
D = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/'
base = io.open(D + 'main.tex', encoding='utf-8').read()
io.open(D + 'sh-t2.tex', 'w', encoding='utf-8', newline='').write(
    BS + 'def' + BS + 'mthreepure{1}' + chr(10) + BS + 'input{main-t2}' + chr(10))
for h in ('0pt', '1mm', '3mm', '26mm'):
    i = base.index(BS + 'tailfill')
    j = i + len(BS + 'tailfill')
    io.open(D + 'main-t2.tex', 'w', encoding='utf-8', newline='').write(base[:j] + '[' + h + ']' + base[j:])
    for f in ('sh-t2.log', 'sh-t2.aux', 'sh-t2.pdf'):
        if os.path.exists(D + f):
            os.remove(D + f)
    for _ in range(2):
        subprocess.run([X, '-interaction=nonstopmode', 'sh-t2.tex'], cwd=D, capture_output=True)
    lg = io.open(D + 'sh-t2.log', encoding='utf-8', errors='replace').read()
    print(h, 'ovf=', len(re.findall(r'Overfull .vbox', lg)),
          re.findall(r'Output written on \S+ \((\d+) pages', lg),
          re.findall(r'Overfull .vbox .([0-9.]+)pt', lg)[:2], flush=True)
