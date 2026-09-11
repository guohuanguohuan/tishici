# -*- coding: utf-8 -*-
"""绕图回流0910 判据探针：body.tex 中 image1/image2 side 段的前缀/下邻元素结构。"""
import io
import re

b = io.open(r'C:\提示词\工作区\字替对照-0909\variantF\body.tex', encoding='utf-8').read()
els = b.split('\n\n')
print('elements', len(els))
for i, e in enumerate(els):
    m = re.search(r'media/media/(image\d)\.png', e)
    if not (m and '\\begin{minipage}[t]' in e):
        continue
    pre = re.search(r'\\raggedright (.*?)\\end\{minipage\}', e, re.S)
    pre = pre.group(1) if pre else '(?)'
    print('===', m.group(1), 'elem', i, '前缀字符数', len(pre))
    print('   头:', pre[:70].replace('\n', ' '))
    print('   尾:', pre[-70:].replace('\n', ' '))
    print('   下一元素:', (els[i + 1][:70] if i + 1 < len(els) else '(end)').replace('\n', ' '))
