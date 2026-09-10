# -*- coding: utf-8 -*-
"""扫 body.tex 数学段内的字母串连字符（letter-hyphen-letter）模式。"""
import re

body = open(r'C:/提示词/工作区/字替对照-0909/variantF/body.tex', encoding='utf-8').read()
segs = re.findall(r'\\\((.*?)\\\)', body, re.S)
pat = re.compile(r'[A-Za-z](?:_\{?[0-9]\}?)?\s*-\s*[A-Za-z]')
seen = {}
for x in segs:
    for mm in pat.finditer(x):
        ctx = x[max(0, mm.start() - 20):mm.end() + 20]
        seen[ctx] = seen.get(ctx, 0) + 1
for k, v in seen.items():
    print(v, repr(k))
