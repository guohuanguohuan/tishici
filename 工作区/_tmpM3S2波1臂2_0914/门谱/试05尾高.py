# -*- coding: utf-8 -*-
"""试探：05 片 \tailfill 改定高参（诊断 false 档末栏 Overfull 来源；用后视读数决定留撤）"""
import io
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BS, CR, LF = chr(92), chr(13), chr(10)
P = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/main.tex'
val = sys.argv[1] if len(sys.argv) > 1 else ''
raw = open(P, encoding='utf-8', newline='').read()
lines = raw.split(LF)
tgt = BS + 'tailfill'
for i, l in enumerate(lines):
    if l.rstrip(CR) == tgt or l.rstrip(CR).startswith(tgt + '['):
        lines[i] = (tgt + (f'[{val}]' if val else '')) + (CR if lines[i].endswith(CR) else '')
        print(f'第{i+1}行 tailfill → {tgt}{("["+val+"]") if val else ""}')
        break
open(P, 'w', encoding='utf-8', newline='').write(LF.join(lines))
