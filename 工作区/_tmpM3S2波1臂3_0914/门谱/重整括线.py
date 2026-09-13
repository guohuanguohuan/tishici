# -*- coding: utf-8 -*-
"""重整括线.py — 剥全部 {\\ansblockgrayfalse 包装与多余收口，再对指定键干净重挂＋收口。
用法: python 重整括线.py <片目录/main.tex> <键1> <键2> ...
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = sys.argv[1]
KEYS = set(sys.argv[2:])
BS = chr(92)
WRAP = '{' + BS + 'ansblockgrayfalse'
BEG = BS + 'begin{ansblock}['
END = BS + 'end{ansblock}'
ENDC = END + '}'

lines = open(PATH, encoding='utf-8').read().split('\n')
# ① 剥包装行与已挂收口
clean = []
for ln in lines:
    if ln.strip() == WRAP:
        continue
    if ln.strip() == ENDC:
        clean.append(END)
        continue
    clean.append(ln)
# ② 重挂＋按块配对收口
out = []
cur_key = None
need_close = False
for ln in clean:
    ls = ln.strip()
    if ls.startswith(BEG) and ls.endswith(']'):
        key = ls[len(BEG):-1]
        cur_key = key
        if key in KEYS:
            out.append(WRAP)
            need_close = True
        out.append(ln)
        continue
    if ls == END and cur_key is not None:
        if need_close:
            out.append(ln + '}')
            need_close = False
        else:
            out.append(ln)
        cur_key = None
        continue
    out.append(ln)
assert not need_close, '末块未收口'
open(PATH, 'w', encoding='utf-8').write('\n'.join(out))
print('rewrapped', len(KEYS), 'blocks cleanly')
