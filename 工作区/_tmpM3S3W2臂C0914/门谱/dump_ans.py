# -*- coding: utf-8 -*-
"""dump_ans.py — 抽取导学件14/15 指定 例/变式 的 ansitem/ansnote 原文，落盘对照底稿（过程件目录内）。"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/'
OUT = 'C:/提示词/工作区/_tmpM3S3W2臂C0914/门谱/导学件对照底稿.txt'

WANT = {
    '课时14-2.6.2双曲线性质': ['例1', '例3', '例9', '例11', '例16', '例18', '例24', '例26',
                               '例54', '例56', '变2', '变4', '变10', '变17', '变19', '变25'],
    '课时15-2.7.1抛物线方程': ['例1', '例3', '例7', '例13', '例15', '例19', '例23', '例31',
                               '变2', '变4', '变6', '变12', '变14', '变18', '变20', '变22'],
}

def braces(s, i):
    assert s[i] == '{'
    d, j = 0, i
    while j < len(s):
        if s[j] == '\\' and j + 1 < len(s):
            j += 2
            continue
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[i + 1:j], j
        j += 1
    raise ValueError('braces')

chunks = []
for ks, labels in WANT.items():
    src = open(BASE + ks + '/main.tex', encoding='utf-8').read()
    chunks.append('################ ' + ks)
    for lab in labels:
        num = re.search(r'(\d+)', lab).group(1)
        kind = lab[:1]
        pat = (r'\\tjdnr\{[^}]*\}\{[^}]*\}\{例\\textbf\{' + num + r'\}\}\{([^}]*)\}'
               if kind == '例' else
               r'\\liB\{变式\\textbf\{' + num + r'\}\}\{([^}]*)\}')
        m = re.search(pat, src)
        if not m:
            chunks.append(f'---- {lab}: NOT FOUND')
            continue
        tie = m.group(1)
        stem, _ = braces(src, m.end() - 1) if src[m.end() - 1] == '{' else ('', m.end())
        chunks.append(f'---- {lab}｜{tie}')
        chunks.append('题面: ' + stem)
        a = re.search(r'\\ansitem\{' + num + r'\}\{', src[m.end():])
        if a:
            pos = m.end() + a.end() - 1
            body, _ = braces(src, pos)
            chunks.append('ansitem值: ' + body)
        n = re.search(r'\\ansnote\{详解\}\{', src[m.end():])
        if n:
            pos = m.end() + n.end() - 1
            body, _ = braces(src, pos)
            chunks.append('ansnote: ' + body)
        chunks.append('')

open(OUT, 'w', encoding='utf-8').write('\n'.join(chunks))
print('→', OUT, len(chunks), 'lines')
