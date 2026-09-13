# -*- coding: utf-8 -*-
r"""门-回流.py — M3 S2 波1 补位臂3·回流门（零强制跳页）。
断言面：main.tex 剔注释后，强制版面原子零出现。逻辑承臂4 门谱逐字，PIECE 参数化。
用法: python 门-回流.py 15     退出码: 0＝全过；1＝有红。
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 片规 import piece

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = piece(sys.argv[1] if len(sys.argv) > 1 else '09')
PIECE = P['piece']
BAD = ['\\newpage', '\\clearpage', '\\pagebreak', '\\vbox', '\\vtop',
       '\\ketangboxed', '\\columnbreak', '\\eject']

src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
body = '\n'.join(l.split('%', 1)[0] if not l.lstrip().startswith('%') else '' for l in src.split('\n'))
reds = []
for w in BAD:
    n = body.count(w)
    tag = '绿' if n == 0 else '红'
    print(f'  [{tag}] {w} ×{n}')
    if n:
        reds.append(w)
print()
print('回流门：', '全绿（零强制跳页）' if not reds else f'红：{reds}')
sys.exit(0 if not reds else 1)
