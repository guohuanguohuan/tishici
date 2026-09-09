# -*- coding: utf-8 -*-
"""片C 实验：分别设定 relpenalty / binoppenalty。用法：_exp_pen2.py <rel> <bino>"""
import re
import sys

p = r'C:\提示词\工作区\字替对照-0909\variantF\qp-layout.tex'
s = open(p, encoding='utf-8').read()
s = re.sub(r'\\relpenalty=\d+', '\\\\relpenalty=' + sys.argv[1], s)
s = re.sub(r'\\binoppenalty=\d+', '\\\\binoppenalty=' + sys.argv[2], s)
open(p, 'w', encoding='utf-8').write(s)
print('set rel/bino ->', re.findall(r'relpenalty=\d+|binoppenalty=\d+', s))
