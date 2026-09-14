# -*- coding: utf-8 -*-
"""wrap_grayfalse.py — 课时14 判模门首轮读数 est>8 的 32 键 ansblock 加 {\ansblockgrayfalse ...} 包装。
索引定位（非正则）：每键 \begin{ansblock}[K] 恰 1 处；在其前行插 {\ansblockgrayfalse，
其块内首个 \end{ansblock} 后补 }。逐键计数断言，任一异常即中止不落盘。
"""
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DIR = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时14-2.6.2双曲线性质'
KEYS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '括线键-课时14.json'), encoding='utf-8'))

p = os.path.join(DIR, 'main.tex')
src = open(p, encoding='utf-8', newline='').read()

NL = '\r\n' if '\r\n' in src else '\n'
opens = []
for k in KEYS:
    a = '\\begin{ansblock}[' + k + ']'
    n = src.count(a)
    assert n == 1, f'{k}: begin 计数={n}'
    opens.append((src.index(a), k))
opens.sort()

# 自后向前包装，避免位移
for idx, k in reversed(opens):
    end = src.index('\\end{ansblock}', idx)
    src = src[:end] + '\\end{ansblock}}' + src[end + len('\\end{ansblock}'):]
    head = '{\\ansblockgrayfalse' + NL
    src = src[:idx] + head + src[idx:]

assert src.count('{\\ansblockgrayfalse') == len(KEYS), '包装计数不符'
assert src.count('\\ansblockgrayfalse') == len(KEYS), '宏出现总数不符'
open(p, 'w', encoding='utf-8', newline='').write(src)
print('wrapped', len(KEYS), 'keys; newline =', repr(NL))
