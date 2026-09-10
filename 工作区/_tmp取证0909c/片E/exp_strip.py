# -*- coding: utf-8 -*-
"""实验：从探三块（body.tex 第 169-170 行区域）移除 \smash{\rlap{...}} 前缀，测断行是否回到旧形。
用法：python exp_strip.py strip|restore"""
import sys

P = r'C:\提示词\工作区\字替对照-0909\variantF\body.tex'
BAK = r'C:\提示词\工作区\_tmp取证0909c\片E\exp_body_new.tex'
s = open(P, encoding='utf-8').read()

if sys.argv[1] == 'strip':
    key = r'\smash{\rlap{\hspace{47.983mm}'
    i = s.find(key)
    assert i >= 0, '探三块前缀未找到'
    # 找到匹配的 }}}}（前缀结束于 image2.png}}}}）
    j = s.find('image2.png', i)
    assert j > 0
    end = s.find('}}}}', j) + 4
    s2 = s[:i] + s[end:]
    open(P, 'w', encoding='utf-8').write(s2)
    print('stripped', end - i, 'chars')
else:
    open(P, 'w', encoding='utf-8').write(open(BAK, encoding='utf-8').read())
    print('restored from', BAK)
