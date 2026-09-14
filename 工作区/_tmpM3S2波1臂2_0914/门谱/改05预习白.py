# -*- coding: utf-8 -*-
"""一次性：05 片 预习 \liubai[9mm]→[7mm]（false 档末页左栏末行越界 2.32pt 治理；
   母版件预习 liubai 为版心自由度，片侧可微调，不动 sty）"""
import io
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BS, CR, LF = chr(92), chr(13), chr(10)
P = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/main.tex'
raw = open(P, encoding='utf-8', newline='').read()
lines = raw.split(LF)
hits = [i for i, l in enumerate(lines) if BS + 'liubai[9mm]' in l]
assert len(hits) == 1, f'liubai 命中数异常：{hits}'
i = hits[0]
lines[i] = lines[i].replace(BS + 'liubai[9mm]', BS + 'liubai[7mm]')
open(P, 'w', encoding='utf-8', newline='').write(LF.join(lines))
print('OK: 第', i + 1, '行 liubai 9mm → 7mm')
