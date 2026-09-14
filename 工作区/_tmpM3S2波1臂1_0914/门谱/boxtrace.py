# -*- coding: utf-8 -*-
r"""boxtrace.py — 给 V0/main.tex 打 \tracingoutput 补丁并编译，导出溢出栏的盒结构（过程件）。"""
import io
import os
import re
import subprocess
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
BISECT = os.path.normpath(os.path.join(HERE, '..', 'bisect'))
SRC = r"C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/衔接节"
D = os.path.join(BISECT, 'TB')
os.makedirs(D, exist_ok=True)

base = io.open(os.path.join(BISECT, 'V0', 'main.tex'), encoding='utf-8').read()
assert '\\begin{document}\n' in base
src = base.replace('\\begin{document}\n',
                   '\\begin{document}\n\\tracingoutput=1\n\\showboxdepth=2\n\\showboxtrace=0\n', 1)
io.open(os.path.join(D, 'main.tex'), 'w', encoding='utf-8').write(src)
for f in ('main-true.tex', 'qp-m3.sty'):
    with open(os.path.join(SRC, f), 'rb') as fi, open(os.path.join(D, f), 'wb') as fo:
        fo.write(fi.read())

for _ in range(2):
    subprocess.run(['xelatex', '-interaction=nonstopmode', 'main-true.tex'],
                   cwd=D, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
log = io.open(os.path.join(D, 'main-true.log'), encoding='utf-8', errors='replace').read()
print('overfull:', re.findall(r'Overfull \\vbox \(([\d.]+)pt', log))
lines = log.split('\n')
for i, ln in enumerate(lines):
    if ln.startswith('Overfull \\vbox'):
        print('--- at log line', i + 1)
        for j in range(i, min(i + 90, len(lines))):
            print(lines[j])
        break
