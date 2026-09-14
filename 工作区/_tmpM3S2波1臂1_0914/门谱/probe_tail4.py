# -*- coding: utf-8 -*-
r"""probe_tail4.py — 第四轮：尾区 \xiexwei 增/减双向扫描（过程件，非交付物）。

假设：溢出栏是「不可断灰底块被强行塞入栏尾」所致，故**增大**前序详解位可把该块
整体推入下一栏，从而 0 溢且保持 6 页。
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
base = io.open(os.path.join(SRC, 'main.tex'), encoding='utf-8').read()  # 含 \rightskip 补丁的活件

OCC = [m.start() for m in re.finditer(r'\\xiexwei\{(\d+)mm\}', base)]
VAL = [int(m.group(1)) for m in re.finditer(r'\\xiexwei\{(\d+)mm\}', base)]
assert len(OCC) == 18, len(OCC)
print('xiexwei 序列:', VAL)


def setmm(s, idx1, newmm):
    """idx1: 1-based occurrence index; newmm: None=删除该宏"""
    occ = [m.start() for m in re.finditer(r'\\xiexwei\{(\d+)mm\}', s)]
    m = re.search(r'\\xiexwei\{(\d+)mm\}', s[occ[idx1 - 1]:])
    a = occ[idx1 - 1]
    b = a + m.group(0).__len__()
    return s[:a] + ('' if newmm is None else '\\xiexwei{%dmm}' % newmm) + s[b:]


def multi(edits):
    s = base
    for idx, mm in sorted(edits, reverse=True):
        s = setmm(s, idx, mm)
    return s


CASES = [
    ('P18_20', [(18, 20)]),
    ('P17_20', [(17, 20)]),
    ('P16_20', [(16, 20)]),
    ('P15_18', [(15, 18)]),
    ('P14_22', [(14, 22)]),
    ('P1617_20', [(16, 20), (17, 20)]),
    ('P1415_20', [(14, 20), (15, 18)]),
    ('P1418_plus6', [(14, 20), (15, 16), (16, 18), (17, 18), (18, 18)]),
    ('P1217_minus4', [(12, 10), (13, 8), (14, 10), (15, 6), (16, 8), (17, 8)]),
    ('P18_del', [(18, None)]),
]

for name, edits in CASES:
    d = os.path.join(BISECT, name)
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, 'main.tex'), 'w', encoding='utf-8').write(multi(edits))
    for f in ('main-true.tex', 'qp-m3.sty'):
        with open(os.path.join(SRC, f), 'rb') as fi, open(os.path.join(d, f), 'wb') as fo:
            fo.write(fi.read())
    for _ in range(2):
        subprocess.run(['xelatex', '-interaction=nonstopmode', 'main-true.tex'],
                       cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = io.open(os.path.join(d, 'main-true.log'), encoding='utf-8', errors='replace').read()
    pg = re.search(r'Output written on main-true\.pdf \((\d+) pages', log)
    print(name.ljust(14), 'e%d o%d u%d m%d a%d p%s' % (
        len(re.findall(r'^! ', log, re.M)), len(re.findall('Overfull', log)),
        len(re.findall('Underfull', log)), len(re.findall('Missing character', log)),
        len(re.findall(r'^M3-ANSKEY: ', log, re.M)), pg.group(1) if pg else '?'),
        re.findall(r'Overfull \\vbox \(([\d.]+)pt', log),
        re.findall(r'Underfull \\hbox \([^)]*\) in paragraph at lines (\d+--\d+)', log), flush=True)
