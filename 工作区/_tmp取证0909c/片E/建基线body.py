# -*- coding: utf-8 -*-
"""重建基线 body.tex：把切分余段并回 minipage（改前对照用）。"""
import re

SRC = r'C:\提示词\工作区\_tmp取证0909c\片E\body_final_split.tex'
DST = r'C:\提示词\工作区\_tmp取证0909c\片E\body_baseline.tex'
BLOCK = re.compile(r'\\(bindp|bindopt|tjdnr|liB|ansline|jiexi|xiaojie|zsd|zhenti|vbox|huaxing)')

s = open(SRC, encoding='utf-8').read()
els = s.split('\n\n')
out, i, n = [], 0, 0
while i < len(els):
    e = els[i]
    m = re.search(r'image(\d)\.png', e)
    if '\\begin{minipage}[t]' in e and m and m.group(1) in ('4', '5') and i + 1 < len(els):
        nxt = els[i + 1]
        if not BLOCK.match(nxt):
            e = e.replace(r'\end{minipage}', nxt + r'\end{minipage}', 1)
            i += 1
            n += 1
    out.append(e)
    i += 1
open(DST, 'w', encoding='utf-8').write('\n\n'.join(out))
print('merged', n, 'split rows ->', DST)
