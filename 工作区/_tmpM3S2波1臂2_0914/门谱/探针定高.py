# -*- coding: utf-8 -*-
"""定高探针：把 false 壳的 \\input{main.tex} 换成临时副本（tailfill 加/去定高），
隔离验证「\\tailfill[高度] 在 pure 档是否生效」。跑完自动删临时件。
"""
import io
import os
import re
import subprocess

BS, LF = chr(92), chr(10)
D = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/'
X = 'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex'
body = io.open(D + 'main.tex', encoding='utf-8').read()
shell = io.open(D + 'main-false.tex', encoding='utf-8').read()

for h in ('', '[1pt]', '[26mm]'):
    i = body.index(BS + 'tailfill')
    j = i + len(BS + 'tailfill')
    io.open(D + 'zz-probe.tex', 'w', encoding='utf-8', newline='').write(body[:j] + h + body[j:])
    sh = shell.replace(BS + 'input{main.tex}', BS + 'input{zz-probe.tex}')
    assert sh != shell
    io.open(D + 'zz-probe-shell.tex', 'w', encoding='utf-8', newline='').write(sh)
    for f in os.listdir(D):
        if f.startswith('zz-probe') and f.endswith(('.log', '.aux', '.pdf')):
            os.remove(D + f)
    for _ in range(2):
        subprocess.run([X, '-interaction=nonstopmode', 'zz-probe-shell.tex'], cwd=D, capture_output=True)
    lg = io.open(D + 'zz-probe-shell.log', encoding='utf-8', errors='replace').read()
    print(repr(h or '无参'), 'ovf=', re.findall(r'Overfull .vbox .([0-9.]+)pt', lg),
          'pages=', re.findall(r'Output written on \S+ \((\d+) pages', lg),
          'anskey=', lg.count('M3-ANSKEY'), flush=True)
