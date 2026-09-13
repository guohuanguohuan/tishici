# -*- coding: utf-8 -*-
r"""门-回流19.py — M3 S2 波1 补位臂4b·课时19·回流门（零强制跳页）＋CJK catcode 审计。
断言面：main.tex 剔注释后，强制版面原子零出现；控制词直连 CJK 零命中（母版坑①铁律）。
用法: python 门-回流19.py     退出码: 0＝全过；1＝有红。
"""
import io
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时19-章末总结与复习'
BAD = ['\\newpage', '\\clearpage', '\\pagebreak', '\\vbox', '\\vtop',
       '\\ketangboxed', '\\columnbreak', '\\eject']

src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
body = '\n'.join(l.split('%', 1)[0] if not l.lstrip().startswith('%') else '' for l in src.split('\n'))
reds = []
for w in BAD:
    n = body.count(w)
    tag = '绿' if n == 0 else '红'
    print(f'  [{tag}] {w} ×{n}')
    if n:
        reds.append(w)
hits = re.findall(r'\\[a-zA-Z]+[\u4e00-\u9fff]', body)
print(f'  [{"绿" if not hits else "红"}] CJK catcode 审计（控制词直连汉字）×{len(hits)}'
      + (f'：{sorted(set(hits))[:8]}' if hits else ''))
if hits:
    reds.append('CJK-catcode')
print()
print('回流门＋CJK 审计：', '全绿（零强制跳页·零命中）' if not reds else f'红：{reds}')
sys.exit(0 if not reds else 1)
