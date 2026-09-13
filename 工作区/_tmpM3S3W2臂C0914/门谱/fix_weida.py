# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时14-2.6.2双曲线性质/main.tex'
BS = chr(92)
s = open(p, encoding='utf-8').read()
old = '（ii）韦达分子分母化简' + BS + '(4k^{2}+3+4k^{2}+k^{2}-3=9k^{2}' + BS + ')、'
new = ('（ii）韦达分子分母化简：' + BS + 'par' + BS + 'noindent '
       + BS + '(4k^{2}+3+4k^{2}+k^{2}-3=9k^{2}' + BS + ')、')
assert old in s, '目标串未找到'
assert new not in s
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('化简后断段 ok')
