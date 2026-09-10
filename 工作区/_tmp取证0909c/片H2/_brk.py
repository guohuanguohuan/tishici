# -*- coding: utf-8 -*-
"""片H2：串连字符后断点档开关（allowbreak / penalty100 / penalty500 / none）。实验用。"""
import sys

p = r'C:/提示词/工作区/字替对照-0909/variantF/postproc_daoxue.py'
s = open(p, encoding='utf-8').read()
B = chr(92) + 'allowbreak'
P100 = chr(92) + 'penalty100'
P500 = chr(92) + 'penalty500'
P1000 = chr(92) + 'penalty1000'
TEXTDASH = chr(92) + 'text{-}'
mode = sys.argv[1] if len(sys.argv) > 1 else 'allowbreak'
# 归一化：先把所有已知形态收敛到 'TEXTDASH + 空格'
for tok in (TEXTDASH + B + ' ', TEXTDASH + P100 + ' ', TEXTDASH + P500 + ' ', TEXTDASH + P1000 + ' '):
    s = s.replace(tok, TEXTDASH + ' ')
if mode == 'allowbreak':
    s = s.replace(TEXTDASH + ' ', TEXTDASH + B + ' ')
elif mode == 'penalty100':
    s = s.replace(TEXTDASH + ' ', TEXTDASH + P100 + ' ')
elif mode == 'penalty500':
    s = s.replace(TEXTDASH + ' ', TEXTDASH + P500 + ' ')
elif mode == 'penalty1000':
    s = s.replace(TEXTDASH + ' ', TEXTDASH + P1000 + ' ')
elif mode == 'none':
    pass
open(p, 'w', encoding='utf-8').write(s)
print('mode', mode, '| allowbreak', s.count(B), '| p100', s.count(P100), '| p500', s.count(P500), '| p1000', s.count(P1000))
