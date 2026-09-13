# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = r'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时14-2.6.2双曲线性质/main.tex'
lines = open(PATH, encoding='utf-8').read().split('\n')
start = None
for i, l in enumerate(lines):
    if l.startswith('\\ansnote{详解}{(1)\\(|OF_1|'):
        start = i
        break
assert start is not None, 'ansnote start not found'
end = start
while not lines[end].endswith('}'):
    end += 1
fixed = 0
for k in range(start + 1, end + 1):
    if not lines[k].startswith('\\par\\noindent '):
        lines[k] = '\\par\\noindent ' + lines[k]
        fixed += 1
open(PATH, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print(f'ansnote block lines {start+1}..{end+1}, re-prefixed {fixed}')
