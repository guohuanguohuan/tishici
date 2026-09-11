# -*- coding: utf-8 -*-
import io, re
t = io.open(r'C:\提示词\工作区\字替对照-0909\variantF\body.tex', encoding='utf-8').read()
lines = t.split('\n')
BS = chr(92)
pat_head = re.compile(r'\\(?:zhidian|zsd2|knowpoint|tiaomu|tiaomuz|tiaomutail|liA|liB|zhenti)')
for i, l in enumerate(lines, 1):
    nk = l.count(BS + 'kongbai{}')
    if nk or pat_head.search(l):
        print(i, 'kb=%d' % nk, l.strip()[:100])
