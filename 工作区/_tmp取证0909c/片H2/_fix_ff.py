# -*- coding: utf-8 -*-
"""修复 qp-layout.tex 被 \\f 转义破坏的 frac 行（FF 字符残留清理）。"""
p = r'C:/提示词/工作区/字替对照-0909/variantF/qp-layout.tex'
s = open(p, encoding='utf-8').read()
print('FF count:', s.count('\x0c'))
s = s.replace('\x0c', '\\f')
# 校验修复结果
import re
for line in s.splitlines():
    if 'let' in line and 'dfrac' in line:
        print('LET LINE:', repr(line))
open(p, 'w', encoding='utf-8').write(s)
print('fixed')
