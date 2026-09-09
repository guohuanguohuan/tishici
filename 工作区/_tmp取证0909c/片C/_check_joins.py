# -*- coding: utf-8 -*-
"""终轮 body.tex 接缝核查：\\)\\( 处是否带 \allowbreak；关系号紧邻是否未加。"""
import re

s = open(r'C:\提示词\工作区\字替对照-0909\variantF\body.tex', encoding='utf-8').read()
pat_break = r'\)\\allowbreak\('
pat_plain = r'(?<!\w)\)\\\('
print('带 \\allowbreak 的接缝:', len(re.findall(pat_break, s)))
for m in re.finditer(pat_break, s):
    i = m.start()
    print('  B:', repr(s[max(0, i - 36):i + 24]))
print('不带 \\allowbreak 的接缝:')
for m in re.finditer(pat_plain, s):
    i = m.start()
    print('  P:', repr(s[max(0, i - 36):i + 24]))
