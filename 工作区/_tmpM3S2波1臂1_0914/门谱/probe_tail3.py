# -*- coding: utf-8 -*-
r"""probe_tail3.py — 第三轮：尾块前设可断伸展胶 vs 取消末题 \xiexwei（过程件，非交付物）。"""
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

TAIL = '% ---- 尾块（\\tailfill 置 \\end{multicols} 前；无参＝内容尾随框，件侧不擅自定高） ----\n\\tailfill'
assert TAIL in base, 'tail anchor not found'


def before_tail(s, ins):
    return s.replace(TAIL, ins + '\n' + TAIL, 1)


def noxiex(s):
    k = s.index(r'\liB{练习\textbf{27}}')
    m = s.index(r'\xiexwei{12mm}', k)
    return s[:m] + s[m + len(r'\xiexwei{12mm}'):]


CASES = [
    ('D1_vfill', before_tail(base, '\\vfill')),
    ('D2_vskipstretch', before_tail(base, '\\vskip 0pt plus 20pt minus 6pt')),
    ('D3_pen0', before_tail(base, '\\par\\penalty0 \\vskip 0pt plus 12pt')),
    ('D4_noxiex_ctrl', noxiex(base)),
    ('D5_vfill_noxiex', noxiex(before_tail(base, '\\vfill'))),
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
    print(name.ljust(18), ' | '.join(row), flush=True)
