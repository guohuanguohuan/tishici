# -*- coding: utf-8 -*-
"""收口括线.py — 为每个 {\\ansblockgrayfalse 包装块在配对 \\end{ansblock} 后补收口 }。
用法: python 收口括线.py <片目录/main.tex>
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = sys.argv[1]
BS = chr(92)
END = BS + 'end{ansblock}'
WRAP = '{' + BS + 'ansblockgrayfalse'

lines = open(PATH, encoding='utf-8').read().split('\n')
out = []
pending = 0
fixed = 0
for ln in lines:
    ls = ln.strip()
    if ls == WRAP:
        pending += 1
        out.append(ln)
        continue
    if pending > 0 and ls == END:
        out.append(ln + '}')
        pending -= 1
        fixed += 1
        continue
    out.append(ln)
assert pending == 0, f'未配平包装 {pending} 处'
open(PATH, 'w', encoding='utf-8').write('\n'.join(out))
print('closed', fixed)
