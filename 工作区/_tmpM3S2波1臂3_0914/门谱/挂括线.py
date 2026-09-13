# -*- coding: utf-8 -*-
"""挂括线.py — 为指定键的 ansblock 补挂 {\\ansblockgrayfalse 包装（片内唯一键）。
用法: python 挂括线.py <片目录/main.tex> <键1> <键2> ...
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = sys.argv[1]
KEYS = sys.argv[2:]
BS = chr(92)
OPEN = BS + 'begin{ansblock}['
WRAP = '{' + BS + 'ansblockgrayfalse\n'

src = open(PATH, encoding='utf-8').read()
for k in KEYS:
    a = OPEN + k + ']'
    n = src.count(a)
    assert n == 1, (k, n)
    src = src.replace(a, WRAP + a)
open(PATH, 'w', encoding='utf-8').write(src)
print('wrapped', len(KEYS))
