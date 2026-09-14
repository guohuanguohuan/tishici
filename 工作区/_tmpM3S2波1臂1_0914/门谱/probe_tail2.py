# -*- coding: utf-8 -*-
r"""probe_tail2.py — 衔接节 true 档 Overfull \vbox 第二轮定位矩阵（过程件，非交付物）。

候选：末块转括线（正确包法）、8行级三块转括线、尾区 \xiexwei 取消、组合。
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

BEG = r'\begin{ansblock}'
END = r'\end{ansblock}'


def ruled(s, key):
    i = s.index(BEG + '[' + key + ']')
    j = s.index(END, i) + len(END)
    return s[:i] + '{' + '\\ansblockgrayfalse\n' + s[i:j] + '}' + s[j:]


def noxiex_after(s, anchor):
    k = s.index(anchor)
    m = s.index(r'\xiexwei{12mm}', k)
    return s[:m] + s[m + len(r'\xiexwei{12mm}'):]


K16 = '2章-练-衔接-16'
K_T2 = '2章-导-衔接-探2'
K_T5 = '2章-导-衔接-探5'
K_G2 = '2章-导-衔接-G2'
A27 = r'\liB{练习\textbf{27}}'

CASES = [
    ('C1_lastRuled', ruled(base, K16)),
    ('C2_lastNoxiex', noxiex_after(base, A27)),
    ('C3_G2ruled', ruled(base, K_G2)),
    ('C4_T2ruled', ruled(base, K_T2)),
    ('C5_T5ruled', ruled(base, K_T5)),
    ('C6_T2T5G2ruled', ruled(ruled(ruled(base, K_T2), K_T5), K_G2)),
    ('C7_lastRuled_noxiex', noxiex_after(ruled(base, K16), A27)),
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
