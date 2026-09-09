# -*- coding: utf-8 -*-
"""统计 body.tex 中数学组接缝形。"""
import re

s = open(r'C:\提示词\工作区\字替对照-0909\variantF\body.tex', encoding='utf-8').read()
pat_join = '\\' + ')' + '\\' + '('          # \)\\
pat_paren = '\\' + ')' + '('                # \)(
pat_space = '\\' + ') \\' + '('             # \) \(
print('math-math \\\\)\\\\( :', s.count(pat_join))
print('math-paren \\\\)( :', s.count(pat_paren))
print('math-space-math \\\\) \\\\( :', s.count(pat_space))
for m in re.finditer(re.escape(pat_join), s):
    i = m.start()
    print('JOIN:', repr(s[max(0, i-30):i+30]))
