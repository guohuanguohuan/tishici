# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时14-2.6.2双曲线性质/main.tex'
BS = chr(92)
mode = sys.argv[1]
s = open(p, encoding='utf-8').read()
if mode == 'on':
    assert BS + 'overfullrule' not in s
    anchor = BS + 'begin{document}'
    s = s.replace(anchor, anchor + '\n' + BS + 'overfullrule=5pt%', 1)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print('overfullrule on')
else:
    s = s.replace('\n' + BS + 'overfullrule=5pt%', '', 1)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print('overfullrule off')
