# -*- coding: utf-8 -*-
"""扫内容高（诊断：把片内若干 \\xiexwei 同减 delta mm），用后必撤。
用法: python 扫内容高.py <delta> [lines=115,124,...]
"""
import io
import os
import re
import subprocess
import sys

BS, LF = chr(92), chr(10)
D = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/'
X = 'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex'
delta = int(sys.argv[1])
LINES = [int(v) for v in sys.argv[2].split(',')]
base = io.open(D + 'main.tex', encoding='utf-8', newline='').read()
lines = base.split(LF)
for n in LINES:
    m = re.match('^\\s*' + BS + r'xiexwei\{(\d+)mm\}\s*$', lines[n - 1])
    assert m, (n, lines[n - 1])
    newv = int(m.group(1)) + delta
    assert newv >= 3, newv
    lines[n - 1] = lines[n - 1].replace('{' + m.group(1) + 'mm}', '{%dmm}' % newv)
io.open(D + 'zz-probe.tex', 'w', encoding='utf-8', newline='').write(LF.join(lines))
shell = io.open(D + 'main-false.tex', encoding='utf-8').read().replace(
    BS + 'input{main.tex}', BS + 'input{zz-probe.tex}')
assert shell != io.open(D + 'main-false.tex', encoding='utf-8').read()
io.open(D + 'zz-probe-shell.tex', 'w', encoding='utf-8', newline='').write(shell)
for f in os.listdir(D):
    if f.startswith('zz-probe') and f.endswith(('.log', '.aux', '.pdf')):
        os.remove(D + f)
for _ in range(2):
    subprocess.run([X, '-interaction=nonstopmode', 'zz-probe-shell.tex'], cwd=D, capture_output=True)
lg = io.open(D + 'zz-probe-shell.log', encoding='utf-8', errors='replace').read()
print('delta', delta, LINES, 'ovf=', re.findall(r'Overfull .vbox .([0-9.]+)pt', lg),
      'pages=', re.findall(r'Output written on \S+ \((\d+) pages', lg), flush=True)
