# -*- coding: utf-8 -*-
"""片C：设定 emergencystretch 值（postproc LAN_OPEN 发射 + qp-layout 序言）。用法：_exp_em.py 2em"""
import re
import sys

v = sys.argv[1]
p1 = r'C:\提示词\工作区\字替对照-0909\variantF\postproc_daoxue.py'
s = open(p1, encoding='utf-8').read()
s = re.sub(r'(\\\\begin\{multicols\}\{2\}\\n\\\\emergencystretch=)[0-9.]+(em|pt)', r'\g<1>' + v, s)
open(p1, 'w', encoding='utf-8').write(s)
p2 = r'C:\提示词\工作区\字替对照-0909\variantF\qp-layout.tex'
s2 = open(p2, encoding='utf-8').read()
s2 = re.sub(r'\\emergencystretch=[0-9.]+(em|pt)(\s+%)', r'\\emergencystretch=' + v + r'\g<2>', s2, count=1)
open(p2, 'w', encoding='utf-8').write(s2)
print('postproc:', re.findall(r'emergencystretch=[0-9.]+(?:em|pt)', s))
print('qp-layout:', re.findall(r'\\emergencystretch=[0-9.]+(?:em|pt)', s2))
