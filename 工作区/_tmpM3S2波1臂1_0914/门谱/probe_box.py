# -*- coding: utf-8 -*-
r"""probe_box.py — 括线块与 true 档 Overfull \vbox 的因果矩阵（过程件，非交付物）。"""
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

OPEN = '{' + '\\ansblockgrayfalse'
CLOSE = '\\end{ansblock}' + '}'


def unrule(s):
    """拆掉全部括线包裹（还原为灰底）。"""
    out = []
    i = 0
    while True:
        j = s.find(OPEN + '\n', i)
        if j < 0:
            out.append(s[i:])
            break
        out.append(s[i:j])
        k = s.index(CLOSE, j) + len(CLOSE)
        seg = s[j + len(OPEN) + 1:k - len(CLOSE)]
        out.append(seg)
        i = k
    return ''.join(out)


def unrule_key(s, key):
    blk = '\\begin{ansblock}[' + key + ']'
    j = s.index(OPEN + '\n' + blk)
    k = s.index(CLOSE, j) + len(CLOSE)
    return s[:j] + s[j + len(OPEN) + 1:k - len(CLOSE)] + s[k:]


allgray = unrule(base)
assert OPEN not in allgray, 'unwrap failed'
CASES = [
    ('M1_allgray', allgray),
    ('M3_gray1', unrule_key(base, '2章-练-衔接-1')),
    ('M4_gray6', unrule_key(base, '2章-练-衔接-6')),
    ('M5_gray8', unrule_key(base, '2章-练-衔接-8')),
    ('M6_gray7', unrule_key(base, '2章-练-衔接-7')),
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
    print(name.ljust(16), ' | '.join(row), flush=True)
