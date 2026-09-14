# -*- coding: utf-8 -*-
"""一次性：05 片版面微调复位＋G4/G5 书写位 7mm→6mm
（false 档末栏＝G23/G24 题干＋书写位＋tailfill 合计超版心 2.32pt，tailfill 被压扁致「笔记与错题整理」
 与其下沿 hairline 叠印；末栏可控旋钮只有 G 组书写位，收 2mm 释放 11.3pt。
  同时复位先前两处试探性改动：预习 liubai 7mm→9mm（回母版制）、E19/E20 书写位 8mm→10mm。）
"""
import io
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BS, CR, LF = chr(92), chr(13), chr(10)
P = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/main.tex'
raw = open(P, encoding='utf-8', newline='').read()
lines = raw.split(LF)


def setline(n, expect, new):
    cur = lines[n - 1].rstrip(CR)
    assert cur == expect, f'第{n}行非预期：{cur!r} ≠ {expect!r}'
    lines[n - 1] = new + (CR if lines[n - 1].endswith(CR) else '')
    print(f'第{n}行：{expect} → {new}')


X = lambda v: BS + 'xiexwei{' + v + '}'
setline(78, BS + 'liubai[7mm]{此处书写}', BS + 'liubai[9mm]{此处书写}')
setline(334, X('8mm'), X('10mm'))
setline(346, X('8mm'), X('10mm'))
setline(401, X('7mm'), X('6mm'))
setline(410, X('7mm'), X('6mm'))
open(P, 'w', encoding='utf-8', newline='').write(LF.join(lines))
print('done')
