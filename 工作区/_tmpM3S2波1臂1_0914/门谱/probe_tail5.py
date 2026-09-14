# -*- coding: utf-8 -*-
r"""probe_tail5.py — 第五轮：尾区 \xiexwei 全局位移 δ 扫描（过程件，非交付物）。

occ 12..18 = 行 283/293/302/313/322/331/364（练习19…练习27 的书写位）。
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


def shifted(delta, idxs):
    tgt = {i - 1: VAL[i - 1] + delta for i in idxs}
    if min(tgt.values()) < 4:
        return None
    ctr = [-1]

    def rep(m):
        ctr[0] += 1
        return '\\xiexwei{%dmm}' % tgt.get(ctr[0], int(m.group(1)))
    return re.sub(r'\\xiexwei\{(\d+)mm\}', rep, base)


IDXS = list(range(12, 19))
for delta in (-8, -6, -4, -2, 2, 4, 6, 8, 10, 12):
    src = shifted(delta, IDXS)
    if src is None:
        print('d%+d skip(过小)' % delta)
        continue
    name = 'S5_d%+d' % delta
    d = os.path.join(BISECT, name)
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, 'main.tex'), 'w', encoding='utf-8').write(src)
    for f in ('main-true.tex', 'qp-m3.sty'):
        with open(os.path.join(SRC, f), 'rb') as fi, open(os.path.join(d, f), 'wb') as fo:
            fo.write(fi.read())
    subprocess.run(['xelatex', '-interaction=nonstopmode', 'main-true.tex'],
                   cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = io.open(os.path.join(d, 'main-true.log'), encoding='utf-8', errors='replace').read()
    pg = re.search(r'Output written on main-true\.pdf \((\d+) pages', log)
    print('d%+3d' % delta, 'vals', [VAL[i - 1] + delta for i in IDXS],
          'e%d o%d u%d a%d p%s' % (
              len(re.findall(r'^! ', log, re.M)), len(re.findall('Overfull', log)),
              len(re.findall('Underfull', log)),
              len(re.findall(r'^M3-ANSKEY: ', log, re.M)),
              pg.group(1) if pg else '?'),
          re.findall(r'Overfull \\vbox \(([\d.]+)pt', log), flush=True)
