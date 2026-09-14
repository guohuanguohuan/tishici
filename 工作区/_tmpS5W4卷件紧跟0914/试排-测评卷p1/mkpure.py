# -*- coding: utf-8 -*-
"""mkpure.py — 双壳生成器：main.tex → main-pure.tex（唯一差＝[pure] 包选项，S4 断点件 §① 制）。"""
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, 'main.tex'), encoding='utf-8').read()
OLD = '\\usepackage{qp-m3}'
NEW = '\\usepackage[pure]{qp-m3}'
assert src.count(OLD) == 1, 'main.tex 包选项行数异常'
io.open(os.path.join(HERE, 'main-pure.tex'), 'w', encoding='utf-8', newline='\n').write(
    src.replace(OLD, NEW))
print('mkpure OK：main-pure.tex 生成（唯一差＝[pure]）')
