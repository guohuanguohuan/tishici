# -*- coding: utf-8 -*-
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BS = chr(92)
BAD = set('_#&$~^{}' + BS)
import os
BASE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库'
for fn in [os.path.join(BASE, '课时18-2.8②压轴综合二-答案侧.md'),
           os.path.join(BASE, '课时19-章末总结与复习-答案侧.md')]:
    txt = open(fn, encoding='utf-8').read()
    for m in re.finditer(r'^%[ \t]*ans:(\S+)\s*\n值：(.*)$', txt, re.M):
        k, v = m.group(1), m.group(2)
        hits = sorted({c for c in v if c in BAD})
        if hits:
            print(fn, k, '→', hits, '|', v[:60])
print('scan done')
