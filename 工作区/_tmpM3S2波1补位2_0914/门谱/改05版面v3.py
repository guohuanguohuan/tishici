# -*- coding: utf-8 -*-
"""05 片版面微调 v3：T8 书写位复位 14mm；G4/G5 书写位 7mm→10mm
   —— 机理：multicols 末栏平衡取 (L+R)/2，false 档右栏含 \tailfill 的 1fill 弹性（自然高≈0），
      致右栏自然高 < 左栏 → 左栏溢出平衡高 2.32pt。加高右栏书写位使 R≥L，消 Overfull。"""
import io
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BS, CR, LF = chr(92), chr(13), chr(10)
P = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/main.tex'
raw = open(P, encoding='utf-8', newline='').read()
lines = raw.split(LF)
X = lambda v: BS + 'xiexwei{' + v + '}'


def setline(n, expect, new):
    cur = lines[n - 1].rstrip(CR)
    assert cur == expect, f'第{n}行非预期：{cur!r} ≠ {expect!r}'
    lines[n - 1] = new + (CR if lines[n - 1].endswith(CR) else '')
    print(f'第{n}行：{expect} → {new}')


setline(316, X('12mm'), X('14mm'))
setline(401, X('7mm'), X('10mm'))
setline(410, X('7mm'), X('10mm'))
open(P, 'w', encoding='utf-8', newline='').write(LF.join(lines))
print('done')
