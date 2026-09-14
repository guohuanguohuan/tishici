# -*- coding: utf-8 -*-
r"""probe_tail.py — 衔接节 true 档 Overfull \vbox 定位矩阵（过程件，非交付物）。

每个用例：从 V0/main.tex（=交付件快照）派生，双档各两编，报 err/over/under/miss/ans/pg。
"""
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
base = io.open(os.path.join(BISECT, 'V0', 'main.tex'), encoding='utf-8').read()

I16 = base.index(r'\begin{ansblock}[2章-练-衔接-16]')
J16 = base.index(r'\end{ansblock}', I16) + len(r'\end{ansblock}')
K27 = base.index(r'\liB{练习\textbf{27}}')
MX = base.index(r'\xiexwei{12mm}', K27)
MTAIL = base.index(r'\tailfill')


def ruled(s):
    return s[:I16] + '{' + '\\ansblockgrayfalse\n' + s[I16:J16] + '\n\\end{ansblock}\n}' + s[J16:]


def noxiex(s):
    return s[:MX] + s[MX + len(r'\xiexwei{12mm}'):]


def notail(s):
    return s.replace('\\tailfill', '', 1)


def vfill_before_tail(s):
    return s[:MTAIL] + '\\vfill\n' + s[MTAIL:]


def mc_overshoot(s, v):
    return s.replace('\\begin{document}', '\\begin{document}\n\\multicolovershoot=%s\n' % v, 1)


def mc_undershoot(s, v):
    return s.replace('\\begin{document}', '\\begin{document}\n\\multicolundershoot=%s\n' % v, 1)


CASES = [
    ('B1_lastRuled', ruled(base)),
    ('B2_noxiex', noxiex(base)),
    ('B3_noxiex_notail', notail(noxiex(base))),
    ('B4_ruled_notail', notail(ruled(base))),
    ('B5_vfill_before_tail', vfill_before_tail(base)),
    ('B6_ruled_vfill', vfill_before_tail(ruled(base))),
    ('B7_overshoot20', mc_overshoot(base, '20pt')),
    ('B8_undershoot40', mc_undershoot(base, '40pt')),
]

for name, src in CASES:
    d = os.path.join(BISECT, name)
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, 'main.tex'), 'w', encoding='utf-8').write(src)
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
        pg = re.search(r'Output written on main-%s\.pdf \((\d+) pages' % mode, log)
        of = re.findall(r'Overfull \\vbox \(([\d.]+)pt', log)
        row.append('%s: e%d o%d u%d m%d a%d p%s %s' % (
            mode, len(re.findall(r'^! ', log, re.M)), len(re.findall('Overfull', log)),
            len(re.findall('Underfull', log)), len(re.findall('Missing character', log)),
            len(re.findall(r'^M3-ANSKEY: ', log, re.M)), pg.group(1) if pg else '?', of))
    print(name.ljust(22), ' | '.join(row), flush=True)
