# -*- coding: utf-8 -*-
"""槽档普查.py — 逐题统计选项行槽宽档位（SLOT 终档实录核对用，只读）。"""
import io
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件'
for d in ('课时06-两条直线的位置关系', '课时07-圆的方程'):
    print('==', d, '==')
    t = open(os.path.join(BASE, d, 'main.tex'), encoding='utf-8').read()
    for ln in t.splitlines():
        m = re.search(r'\\tihao\{(\d+)\}', ln)
        if m:
            cur = m.group(1)
        if 'makebox' in ln:
            n = len(re.findall(r'makebox', ln))
            w = re.search(r'(0\.\d+)\\linewidth', ln)
            print(f'题{cur}: {n}列×{w.group(1)}linewidth' if w else f'题{cur}: {n}列×?')
        elif '\\duoxuan' in ln:
            print(f'题{cur}: 多选 lxopt 单列')
