# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = r'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时14-2.6.2双曲线性质/main.tex'
src = open(PATH, encoding='utf-8').read()
lines = src.split('\n')
head = '\\ansnote{详解}{'
idx = None
for i, l in enumerate(lines):
    if l.startswith(head + '(1)\\(|OF_1|'):
        idx = i
        break
assert idx is not None, 'ansnote line not found'
line = lines[idx]
assert line.endswith('}')
body = line[len(head):-1]
segs = body.split('\\par\\noindent ')
newlines = []
for k, s in enumerate(segs):
    pre = head if k == 0 else ''
    newlines.append(pre + s)
newlines[-1] = newlines[-1] + '}'
lines[idx:idx + 1] = newlines
open(PATH, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('split into', len(newlines), 'source lines from line', idx + 1)
