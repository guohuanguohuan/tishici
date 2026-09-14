# -*- coding: utf-8 -*-
r"""sweep_xiexwei.py — 衔接节尾题 \xiexwei 取值扫描：双档编译读数对照（过程件，非交付物）。"""
import io
import os
import re
import subprocess
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BISECT = os.path.dirname(os.path.abspath(__file__)) + '/../bisect'
BISECT = os.path.normpath(BISECT)
SRC = r"C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/衔接节"
base = io.open(os.path.join(BISECT, 'V0', 'main.tex'), encoding='utf-8').read()
k = base.index(r'\liB{练习\textbf{27}}')
m = base.index(r'\xiexwei{12mm}', k)
head, tail = base[:m], base[m + len(r'\xiexwei{12mm}'):]

CASES = {'X0': None, 'X2': '2mm', 'X4': '4mm', 'X6': '6mm',
         'X8': '8mm', 'X14': '14mm', 'X18': '18mm'}

for name, val in CASES.items():
    d = os.path.join(BISECT, name)
    os.makedirs(d, exist_ok=True)
    s = head + (r'\xiexwei{%s}' % val if val else '') + tail
    io.open(os.path.join(d, 'main.tex'), 'w', encoding='utf-8').write(s)
    for f in ('main-true.tex', 'main-false.tex', 'qp-m3.sty'):
        with open(os.path.join(SRC, f), 'rb') as fi, open(os.path.join(d, f), 'wb') as fo:
            fo.write(fi.read())
    row = []
    for mode in ('true', 'false'):
        for _ in range(2):
            subprocess.run(['xelatex', '-interaction=nonstopmode', 'main-%s.tex' % mode],
                           cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log = io.open(os.path.join(d, 'main-%s.log' % mode), encoding='utf-8',
                      errors='replace').read()
        pg = re.search(r'Output written on main-%s.pdf \((\d+) pages' % mode, log)
        row.append('%s: err=%d over=%d under=%d miss=%d ans=%d pg=%s' % (
            mode, len(re.findall(r'^! ', log, re.M)), len(re.findall('Overfull', log)),
            len(re.findall('Underfull', log)), len(re.findall('Missing character', log)),
            len(re.findall(r'^M3-ANSKEY: ', log, re.M)), pg.group(1) if pg else '?'))
    print(name, val, ' | '.join(row), flush=True)
