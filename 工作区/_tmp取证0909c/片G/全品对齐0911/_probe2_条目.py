# -*- coding: utf-8 -*-
import io, re
t = io.open(r'C:\提示词\工作区\字替对照-0909\variantF\body.tex', encoding='utf-8').read()
lines = t.split('\n')
# 打印知识点段（行 5-110）中条目行与其中 kongbai 计数＋上下文
for i in range(0, 110):
    l = lines[i]
    if ('tiaomu' in l or 'kongbai' in l) and i < 95:
        print('L%d kb=%d :: %s' % (i + 1, l.count(r'\kongbai{}'), l[:230]))
        print()
