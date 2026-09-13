# -*- coding: utf-8 -*-
"""dump_zsd.py — 抽取导学件14/15 例/变式的 节别×知识点 标签，供练习件 tieside 预排对表。零写入（stdout only）。"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/'
PAT = re.compile(
    r'\\tjdnr\{([一二三四五六])\}\{([^}]*)\}\{例\\textbf\{(\d+)\}\}\{([^}]*)\}'
    r'|\\liB\{变式\\textbf\{(\d+)\}\}\{([^}]*)\}')

for ks in ('课时14-2.6.2双曲线性质', '课时15-2.7.1抛物线方程'):
    print('====', ks)
    src = open(BASE + ks + '/main.tex', encoding='utf-8').read()
    for m in PAT.finditer(src):
        if m.group(1):
            print(f'例{m.group(3)}｜节{m.group(1)}·{m.group(2)}｜{m.group(4)}')
        else:
            print(f'  变{m.group(5)}｜{m.group(6)}')
