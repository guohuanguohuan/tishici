# -*- coding: utf-8 -*-
"""探针脚本：修复上一步被换行截断的 image1 split 行，并按 mode 参数决定
arm（临时启用真值切分点）/ off（恢复交付态 None）。只在探针轮使用。"""
import io
import sys

P = r'C:/提示词/工作区/字替对照-0909/variantF/postproc_daoxue.py'
S = io.open(P, encoding='utf-8').read().split('\n')
bad = "    'image1.png': dict(box_w=28.8, r_edge=1.90, text_w=48.000, c0=3.04, split=r'"
i = next(k for k, t in enumerate(S) if t == bad)
nxt = S[i + 1]
assert nxt.startswith("obreak\\(\\overrightarrow{A_{1}B}')"), nxt[:40]
rest = nxt.split("obreak\\(\\overrightarrow{A_{1}B}')", 1)[1]

ARM = ("    'image1.png': dict(box_w=28.8, r_edge=1.90, text_w=48.000, c0=3.04, "
       "split=r'\\nobreak\\(\\overrightarrow{A_{1}B}'") + rest
OFF = ("    'image1.png': dict(box_w=28.8, r_edge=1.90, text_w=48.000, c0=3.04, split=None") + rest
mode = sys.argv[1]
S[i] = ARM if mode == 'arm' else OFF
del S[i + 1]
io.open(P, 'w', encoding='utf-8', newline='').write('\n'.join(S))
import ast
ast.parse(io.open(P, encoding='utf-8').read())
print('repaired + mode=%s, AST OK' % mode)
