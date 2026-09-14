# -*- coding: utf-8 -*-
"""一次性：05 片 例18（E19）书写位 10mm→8mm（false 档末页左栏 Overfull vbox 治理）"""
import io
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BS, CR, LF = chr(92), chr(13), chr(10)
P = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/main.tex'
N = 334
raw = open(P, encoding='utf-8', newline='').read()
lines = raw.split(LF)
cur = lines[N - 1].rstrip(CR)
assert cur == BS + 'xiexwei{10mm}', f'第{N}行非预期：{cur!r}'
lines[N - 1] = BS + 'xiexwei{8mm}' + (CR if lines[N - 1].endswith(CR) else '')
open(P, 'w', encoding='utf-8', newline='').write(LF.join(lines))
print('OK: 第', N, '行 10mm → 8mm')
