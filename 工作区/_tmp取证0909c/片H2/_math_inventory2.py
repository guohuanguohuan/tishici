# -*- coding: utf-8 -*-
"""列出 body.tex 中所有行内数学 \(...\) 段（含 - 的、含 frac 的、含下标的），供逐处核对。"""
import re
import collections

s = open(r'C:/提示词/工作区/字替对照-0909/variantF/body.tex', encoding='utf-8').read()
segs = re.findall(r'\\\((.*?)\\\)', s, re.S)
print('inline math segments total:', len(segs))
print()
print('=== 含 - 的段 ===')
n = 0
for x in segs:
    if '-' in x:
        n += 1
        print(n, repr(x.strip()[:120]))
print()
print('=== 含 frac 的段 ===')
for x in segs:
    if 'frac' in x:
        print(repr(x.strip()[:160]))
