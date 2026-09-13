# -*- coding: utf-8 -*-
import io
import os
import re
import sys

from fontTools.ttLib import TTFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库'
tnr = TTFont('C:/Windows/Fonts/times.ttf').getBestCmap()
song = TTFont('C:/Users/28120/AppData/Local/Microsoft/Windows/Fonts/FZShuSong-Z01S.ttf').getBestCmap()
nsc = TTFont('C:/提示词/工作区/字替对照-0909/variantF/fonts/NSC-w500.ttf').getBestCmap()
allchars = {}
for fn in ['课时18-2.8②压轴综合二-答案侧.md', '课时19-章末总结与复习-答案侧.md']:
    txt = open(os.path.join(BASE, fn), encoding='utf-8').read()
    for m in re.finditer(r'^值：(.*)$', txt, re.M):
        for c in m.group(1):
            if ord(c) >= 128 and not (0x4E00 <= ord(c) <= 0x9FFF) \
                    and c not in '，。；：（）、？！「」『』""''·～—':
                allchars.setdefault(c, []).append(fn[:8])
for c, fns in sorted(allchars.items()):
    print(f'U+{ord(c):04X} {c!r} x{len(fns)} TNR:{"Y" if ord(c) in tnr else "N"} '
          f'Song:{"Y" if ord(c) in song else "N"} NSC:{"Y" if ord(c) in nsc else "N"}')
