# -*- coding: utf-8 -*-
"""探针：variantF body.tex 知识点区「条目→填空数」映射（v10 改动C 分组依据）。"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
body = open(r'C:\提示词\工作区\字替对照-0909\variantF\body.tex', encoding='utf-8').read()
i0 = body.index('\\zsd{')
i1 = body.index('\\tjdnr{一}')
zone = body[i0:i1]
parts = re.split(r'\\zsd\{(.)\}\{([^}]*)\}', zone)
for gi in range(1, len(parts), 3):
    seg = parts[gi + 2]
    ents = re.split(r'\\tiaomu[zt]?\{(\d+)\}', seg)
    counts = []
    for ei in range(1, len(ents), 2):
        n, txt = ents[ei], ents[ei + 1]
        counts.append((n, txt.count('\\kongbai{}')))
    print('知识点' + parts[gi], parts[gi + 1][:16], '条目:', counts, '区kongbai:', seg.count('\\kongbai{}'))
print('区总kongbai:', zone.count('\\kongbai{}'))
# 判断行现状：逐 zhentib 题干长度
for m in re.finditer(r'\\zhentib\{([^}]*)\}\{(.*?)\}\n', body):
    print('判断', m.group(1), 'len≈', len(re.sub(r'\\[a-zA-Z]+|[{}\\^_$()a-zA-Z0-9]', '', m.group(2))))
