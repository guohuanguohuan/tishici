# -*- coding: utf-8 -*-
"""一次性：05 片 探究点四 两题书写位 8mm→6mm（false 档末页两栏合计超版心 ~7pt 治理）"""
import io
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BS, CR, LF = chr(92), chr(13), chr(10)
P = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/main.tex'
raw = open(P, encoding='utf-8', newline='').read()
lines = raw.split(LF)
n = 0
for i in (333, 345):
    cur = lines[i].rstrip(CR)
    assert cur == BS + 'xiexwei{8mm}', f'第{i+1}行非预期：{cur!r}'
    lines[i] = BS + 'xiexwei{6mm}' + (CR if lines[i].endswith(CR) else '')
    n += 1
open(P, 'w', encoding='utf-8', newline='').write(LF.join(lines))
print('OK: 改动', n, '处（334/346 行 8mm→6mm）')
