# -*- coding: utf-8 -*-
r"""门-回流.py — M3 S2 课时01 母版·回流门（零强制跳页）。

断言面：main.tex 剔注释后，以下强制版面原子零出现：
  \newpage \clearpage \pagebreak \vbox \vtop \ketangboxed \columnbreak \eject
（\vbox 系 M2「右栏全空」病灶根因；规格书 v2 §四.二.10② 撤强制跳页。）
用法: python 门-回流.py     退出码: 0＝全过；1＝有红。
"""
import io
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时01-坐标法'
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
