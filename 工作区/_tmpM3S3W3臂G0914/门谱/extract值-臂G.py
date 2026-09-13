# -*- coding: utf-8 -*-
"""extract值-臂G.py — 课时18/19 答案侧「值：」行提取（\ansitem 第二参素材，字节级）。
只读题面库答案侧；唯一写件＝本过程件目录 fragments-课时NN.txt。零 git。
"""
import io
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LIB = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库'
HERE = os.path.dirname(os.path.abspath(__file__))

for tag, fname in (('课时18', '课时18-2.8②压轴综合二-答案侧.md'),
                   ('课时19', '课时19-章末总结与复习-答案侧.md')):
    raw = open(os.path.join(LIB, fname), encoding='utf-8').read()
    pairs = re.findall(r'^%[ \t]*ans:(\S+)\s*\n值：(.*)$', raw, re.M)
    lian = [(k, v) for k, v in pairs if '-练-' in k]
    out = os.path.join(HERE, f'fragments-{tag}.txt')
    with io.open(out, 'w', encoding='utf-8', newline='') as fh:
        for k, v in lian:
            fh.write(f'{k}\t{v}\n')
    print(tag, len(lian), '练键 →', out)
sys.exit(0)
