# -*- coding: utf-8 -*-
"""终版 body.tex 抽查。"""
s = open(r'C:/提示词/工作区/字替对照-0909/variantF/body.tex', encoding='utf-8').read()
print('text{-} count  :', s.count(chr(92) + 'text{-}'))
print('penalty100     :', s.count(chr(92) + 'penalty100'))
print('dfrac          :', s.count(chr(92) + 'dfrac'))
print('nobreak(则?)   :', s.count('则' + chr(92) + 'nobreak' + chr(92) + '('))
for i, line in enumerate(s.splitlines(), 1):
    if chr(92) + 'text{-}' in line:
        j = line.find(chr(92) + 'text{-}')
        print(f'  L{i}: ...{line[max(0,j-30):j+40]}...')
