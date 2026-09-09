# -*- coding: utf-8 -*-
"""片C 实验：设定 qp-layout.tex 关系号断行惩罚值。用法：_exp_penval.py 3000"""
import re
import sys

p = r'C:\提示词\工作区\字替对照-0909\variantF\qp-layout.tex'
s = open(p, encoding='utf-8').read()
v = sys.argv[1]
s = re.sub(r'\\binoppenalty=\d+', '\\\\binoppenalty=' + v, s)
s = re.sub(r'\\relpenalty=\d+', '\\\\relpenalty=' + v, s)
open(p, 'w', encoding='utf-8').write(s)
print('set penalties to', v, '->', re.findall(r'binoppenalty=\d+|relpenalty=\d+', s))
