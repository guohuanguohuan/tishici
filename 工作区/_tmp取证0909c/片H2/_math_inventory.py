# -*- coding: utf-8 -*-
"""清点 body.tex 中行内数学($...$)出现处与其内容特征（分式/减号/上下标）。"""
import re
import collections

s = open(r'C:/提示词/工作区/字替对照-0909/variantF/body.tex', encoding='utf-8').read()
segs = re.findall(r'\$([^$]*)\$', s)
print('inline math segments:', len(segs))
c = collections.Counter(x.strip() for x in segs)
for k, v in c.most_common(80):
    print(v, repr(k))
print('--- 含 frac/dfrac 的行 ---')
for i, line in enumerate(s.splitlines(), 1):
    if 'frac' in line or 'dfrac' in line:
        print(i, line.strip()[:160])
