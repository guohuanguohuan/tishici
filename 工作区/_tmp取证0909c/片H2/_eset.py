# -*- coding: utf-8 -*-
"""片H2：emergencystretch 档位设置（postproc LAN_OPEN 字符串字面量）。用法：python _eset.py 0.75em"""
import sys

p = r'C:/提示词/工作区/字替对照-0909/variantF/postproc_daoxue.py'
s = open(p, encoding='utf-8').read()
B = chr(92) * 2 + 'emergencystretch='          # 文件内字面：\\emergencystretch=
newv = sys.argv[1]
i = s.find(B)
assert i >= 0, '未找到 \\\\emergencystretch= 字面'
j = s.find("'", i)
s2 = s[:i] + B + newv + s[j:]
open(p, 'w', encoding='utf-8').write(s2)
print('set', newv, '| line:', s2[i - 40:i + 40].replace(chr(10), '⏎'))
