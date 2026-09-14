# -*- coding: utf-8 -*-
r"""probe_unbal.py — 末栏免平衡 / 局部 ragged 两路候选（过程件，非交付物）。

E1 \unbalancedcolumns 置 \tailfill 前（保 12mm 详解位）
E2 \multicolovershoot 置 \tailfill 前
E3 末 ansitem 局部 \rightskip（修 Underfull）× E1 组合
E4 仅 E3
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

TAILC = '% ---- 尾块（\\tailfill 置 \\end{multicols} 前；无参＝内容尾随框，件侧不擅自定高） ----'
assert TAILC in base

ANS10 = '\\ansitem{21}{x=(25+'
assert ANS10 in base


def unbal(s):
    return s.replace(TAILC, '\\unbalancedcolumns\n' + TAILC, 1)


def overshoot(s):
    return s.replace(TAILC, '\\multicolovershoot=120pt\n' + TAILC, 1)


def rightskip10(s):
    i = s.index(ANS10)
    j = s.index('\n', i)
    body = s[i:j]
    return s[:i] + '\\begingroup\\rightskip=0pt plus 1fil\\relax\n' + body + '\n\\endgroup' + s[j:]


CASES = [
    ('E1_unbal', unbal(base)),
    ('E2_overshoot', overshoot(base)),
    ('E3_unbal_rs', rightskip10(unbal(base))),
    ('E4_rs', rightskip10(base)),
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
        uf = re.findall(r'Underfull \\hbox \(([^)]*)\) in paragraph at lines (\d+)--(\d+)', log)
        row.append('%s: e%d o%d u%d m%d a%d p%s %s %s' % (
            mode, len(re.findall(r'^! ', log, re.M)), len(re.findall('Overfull', log)),
            len(re.findall('Underfull', log)), len(re.findall('Missing character', log)),
            len(re.findall(r'^M3-ANSKEY: ', log, re.M)), pg.group(1) if pg else '?', of, uf))
    print(name.ljust(16), ' | '.join(row), flush=True)
