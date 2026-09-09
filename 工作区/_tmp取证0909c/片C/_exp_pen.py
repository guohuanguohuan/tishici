# -*- coding: utf-8 -*-
"""片C 实验：qp-layout.tex 惩罚参数开关（Y2=pen10000 / Y3=恢复100）。"""
import sys

p = r'C:\提示词\工作区\字替对照-0909\variantF\qp-layout.tex'
s = open(p, encoding='utf-8').read()
mode = sys.argv[1]
if mode == 'on':
    assert s.count('\\binoppenalty=100\n') == 1, 'binoppenalty 未找到'
    s = s.replace('\\binoppenalty=100\n', '\\binoppenalty=10000\n')
    s = s.replace('\\relpenalty=100\n', '\\relpenalty=10000\n')
elif mode == 'off':
    s = s.replace('\\binoppenalty=10000\n', '\\binoppenalty=100\n')
    s = s.replace('\\relpenalty=10000\n', '\\relpenalty=100\n')
open(p, 'w', encoding='utf-8').write(s)
import re
print(mode, re.findall(r'binoppenalty=\d+', s), re.findall(r'relpenalty=\d+', s),
      'thickmuskip:', re.findall(r'thickmuskip=.*', s))
