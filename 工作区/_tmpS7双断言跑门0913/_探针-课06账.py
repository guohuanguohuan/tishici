# -*- coding: utf-8 -*-
"""调试课时06 ⑬ 源账。"""
import re
import S7双断言跑门 as G

raw = G.read_sources('导学件/课时06')
body = G.strip_comments(raw)
print('tex_raw 长', len(raw), ' raw（ 计数', raw.count('（'), ' body（ 计数', body.count('（'))
print('zhentib 用数', len(re.findall(r'\\zhentib[\{\s]', raw)))
lines_r = raw.split('\n')
lines_b = body.split('\n')
for i, (lr, lb) in enumerate(zip(lines_r, lines_b)):
    if '（' in lr or '（' in lb:
        tag = '双' if ('（' in lr and '（' in lb) else ('仅RAW' if '（' in lr else '仅BODY')
        print(f'L{i} {tag}: {lb.strip()[:70]!r}')
