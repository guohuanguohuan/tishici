# -*- coding: utf-8 -*-
# 扫描 body.tex 块结构（只读）
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
t = open(sys.argv[1], encoding='utf-8').read()
lines = t.split('\n')
pat = re.compile(r'^\\([a-zA-Z]+)')
for i, l in enumerate(lines, 1):
    m = pat.match(l)
    tag = m.group(1) if m else '(cont)'
    print(i, tag, '|', l[:72])
