# -*- coding: utf-8 -*-
"""下册 分节 seat 序 dump（seat 断言适配用）。只读。"""
import io
import re
import sys
from collections import OrderedDict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'C:/提示词/工作区/M3-第2章量产0913/成卷/拓展册/下册/main.tex'
t = open(p, encoding='utf-8').read()
keys = re.findall(r'\\begin\{ansblock\}\[([^\]]+)\]', t)
seats = re.findall(r'\\ansitem\{([^{}]{1,12})\}\{', t)
print(len(keys), len(seats))
g = OrderedDict()
for k, s in zip(keys, seats):
    g.setdefault(re.search(r'课时\d+[A-Za-z]*', k).group(0), []).append(s)
for grp, ss in g.items():
    print(grp, ss)
