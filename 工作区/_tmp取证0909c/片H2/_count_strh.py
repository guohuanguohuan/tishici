# -*- coding: utf-8 -*-
"""统计 body.tex / sec.tex 中字母串连字符字面出现数。"""
body = open(r'C:/提示词/工作区/字替对照-0909/variantF/body.tex', encoding='utf-8').read()
sec = open(r'C:/提示词/工作区/字替对照-0909/variantF/sec.tex', encoding='utf-8').read()
pats = [r'ABC - A_{1}B_{1}C_{1}', r'ABCD-A_1B_1C_1D_1', r'ABCD - A_{1}B_{1}C_{1}D_{1}',
        r'A-EF-D', r'B-AC-D']
for p in pats:
    print(f'{p!r:34} body={body.count(p)} sec={sec.count(p)}')
import re
print('--- A-EF-D 上下文（body）---')
for mm in re.finditer(r'.{0,25}A-EF-D.{0,25}', body):
    print(repr(mm.group(0)))
print('--- B-AC-D 上下文（body）---')
for mm in re.finditer(r'.{0,25}B-AC-D.{0,25}', body):
    print(repr(mm.group(0)))
