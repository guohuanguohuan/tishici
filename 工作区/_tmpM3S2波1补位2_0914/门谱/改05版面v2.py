# -*- coding: utf-8 -*-
"""05 片版面微调 v2：G4/G5 书写位复位 7mm（母版制），改 变式17（T8）书写位 14mm→12mm
   —— 目标：让 false 档末页左栏的断栏点提前一行，消 Overfull \vbox 2.32pt。
   注：false 档末栏 Overfull 由「左栏内容」决定，G 组书写位在右栏，先前改动无效，故复位。"""
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


setline(401, X('6mm'), X('7mm'))
setline(410, X('6mm'), X('7mm'))
setline(316, X('14mm'), X('12mm'))
open(P, 'w', encoding='utf-8', newline='').write(LF.join(lines))
print('done')
