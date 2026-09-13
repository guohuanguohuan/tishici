# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时14-2.6.2双曲线性质/main.tex'
BS = chr(92)
s = open(p, encoding='utf-8').read()
old = (BS + 'left[3(x_2^{2}-1)(x_1+1)^{2}' + BS + 'right]/' + BS
       + 'left[3(x_1^{2}-1)(x_2-1)^{2}' + BS + 'right]')
new = (BS + 'dfrac{' + BS + 'left[3(x_2^{2}-1)(x_1+1)^{2}' + BS + 'right]}{'
       + BS + 'left[3(x_1^{2}-1)(x_2-1)^{2}' + BS + 'right]}')
assert old in s, '目标分式未找到'
assert new not in s
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('链首分式改叠式 ok')
