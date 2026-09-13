# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时14-2.6.2双曲线性质/main.tex'
lines = open(p, encoding='utf-8').read().split('\n')
start = None
for i, l in enumerate(lines):
    if l.startswith('\\ansnote{详解}{(1)\\(|OF_1|'):
        start = i
        break
assert start is not None, 'not found'
end = start
while not lines[end].endswith('}'):
    end += 1
joined = ''.join(lines[start:end + 1])
lines[start:end + 1] = [joined]
open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print(f'rejoined lines {start+1}..{end+1} into one; length={len(joined)}')
