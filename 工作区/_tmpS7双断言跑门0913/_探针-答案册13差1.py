# -*- coding: utf-8 -*-
"""答案册 ⑬ 差1 定位探针：按（ 是否处于行内数学 \(...\) 内分类源侧计数。"""
import re

src = '\n'.join(
    ln for ln in (
        open(r'C:\提示词\工作区\M2-第1章量产0911\成卷\答案册\body.tex', encoding='utf-8').read()
        + open(r'C:\提示词\工作区\M2-第1章量产0911\成卷\答案册\main.tex', encoding='utf-8').read()
    ).split('\n')
    if not ln.lstrip().startswith('%'))

mask = bytearray(len(src))
inline_math = re.compile(r'\\\((?:[^\\]|\\.)*?\\\)')
for m in inline_math.finditer(src):
    for i in range(m.start(), m.end()):
        mask[i] = 1
# 数学环境 \[...\] 与 equation 粗标
for m in re.finditer(r'\\\[(?:[^\\]|\\.)*?\\\]', src, re.S):
    for i in range(m.start(), m.end()):
        mask[i] = 1

inn, out = 0, 0
spots = []
for m in re.finditer('（', src):
    if mask[m.start()]:
        inn += 1
        spots.append(src[max(0, m.start() - 30):m.start() + 12].replace('\n', '⏎'))
    else:
        out += 1
print('数学区内（:', inn, ' 区外（:', out, ' （pdf 实测 212）')
for s in spots:
    print(' 区内:', '…' + s + '…')
