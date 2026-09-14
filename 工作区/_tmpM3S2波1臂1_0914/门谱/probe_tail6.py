# -*- coding: utf-8 -*-
r"""probe_tail6.py — 第六轮：书写位「封顶 18mm」候选组扫描（双档，过程件）。

occ 索引 1-based，对应行：10=261(16) 11=271(14) 12=283(14) 13=293(12) 14=302(14)
15=313(10) 16=322(12) 17=331(12) 18=364(12)。母版/同侪件书写位实测上限 18mm。
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
base = io.open(os.path.join(SRC, 'main.tex'), encoding='utf-8').read()
VAL = [int(m.group(1)) for m in re.finditer(r'\\xiexwei\{(\d+)mm\}', base)]
assert len(VAL) == 18


def applyv(over):
    """over: {1-based idx: mm}"""
    tgt = {i - 1: v for i, v in over.items()}

    def rep(m):
        ctr = rep.__dict__
        ctr['n'] = ctr.get('n', -1) + 1
        return '\\xiexwei{%dmm}' % tgt.get(ctr['n'], int(m.group(1)))
    rep.__dict__['n'] = -1
    return re.sub(r'\\xiexwei\{(\d+)mm\}', rep, base)


def rng(a, b, v):
    return {i: v for i in range(a, b + 1)}


ALL18_1218 = rng(12, 18, 18)
ALL18_1018 = rng(10, 18, 18)
CFG = [
    ('A_1218to18', ALL18_1218),
    ('B_1018to18', ALL18_1018),
    ('C_cap18', {12: 18, 13: 18, 14: 18, 15: 16, 16: 18, 17: 18, 18: 18}),
    ('D_1118to18', rng(11, 18, 18)),
    ('E_d6ctrl', {12: 20, 13: 18, 14: 20, 15: 16, 16: 18, 17: 18, 18: 18}),
    ('F_1218to16', rng(12, 18, 16)),
    ('G_1218to17', rng(12, 18, 17)),
    ('H_1018to17', rng(10, 18, 17)),
]

for name, over in CFG:
    d = os.path.join(BISECT, 'T6_' + name)
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, 'main.tex'), 'w', encoding='utf-8').write(applyv(over))
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
        row.append('%s e%d o%d u%d m%d a%d p%s %s' % (
            mode[0], len(re.findall(r'^! ', log, re.M)), len(re.findall('Overfull', log)),
            len(re.findall('Underfull', log)), len(re.findall('Missing character', log)),
            len(re.findall(r'^M3-ANSKEY: ', log, re.M)), pg.group(1) if pg else '?',
            re.findall(r'Overfull \\vbox \(([\d.]+)pt', log)))
    print(name.ljust(12), ' | '.join(row),
          'Δsum=%+dmm' % (sum(over.values()) - sum(VAL[i - 1] for i in over)), flush=True)
