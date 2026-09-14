# -*- coding: utf-8 -*-
"""实验：05 片 G23/G24 书写位高度扫描 → false 档 Overfull 读数（用后必复位）。
用法: python 实验05尾栏.py <值如6mm|7mm|...|RESTORE>
RESTORE＝从 ../main-05-实验前.tex 回写。
"""
import io
import re
import shutil
import subprocess
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BS, LF, CR = chr(92), chr(10), chr(13)
HERE = __file__.rsplit(chr(92), 1)[0].rsplit('/', 1)[0]
import os
HERE = os.path.dirname(os.path.abspath(__file__))
PROC = os.path.dirname(HERE)
P = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/main.tex'
BAK = os.path.join(PROC, 'main-05-实验前.tex')

val = sys.argv[1]
if val == 'RESTORE':
    shutil.copyfile(BAK, P)
    print('RESTORED')
    sys.exit(0)

raw = open(P, encoding='utf-8', newline='').read()
lines = raw.split(LF)
pat = re.compile(BS + BS + r'xiexwei\{\d+mm\}')
X = BS + 'xiexwei{' + val + '}'
for n in (401, 410):
    cur = lines[n - 1].rstrip(CR)
    assert pat.fullmatch(cur), (n, cur)
    lines[n - 1] = X + (CR if lines[n - 1].endswith(CR) else '')
open(P, 'w', encoding='utf-8', newline='').write(LF.join(lines))

cwd = os.path.dirname(P)
for _ in range(2):
    subprocess.run(['xelatex', '-interaction=nonstopmode', 'main-false.tex'],
                   cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
log = open(os.path.join(cwd, 'main-false.log'), encoding='utf-8', errors='replace').read()
ov = re.findall(r'Overfull \\vbox \(([0-9.]+)pt too high\)', log)
print(f'值={val} Overfull={len(ov)} 明细={ov} err={len(re.findall(chr(94)+chr(33)+" ", log))} under={log.count("Underfull")}')
