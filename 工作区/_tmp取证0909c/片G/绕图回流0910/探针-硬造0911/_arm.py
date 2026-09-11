# -*- coding: utf-8 -*-
"""探针脚本：把 SIDE_DEF['image1.png'] 的 split 键在 arm（临时真值＝硬造切分点）与
off（交付态 None）之间切换，逐图注释尾巴原样保留。仅探针轮使用。"""
import ast
import io
import sys

P = r'C:/提示词/工作区/字替对照-0909/variantF/postproc_daoxue.py'
S = io.open(P, encoding='utf-8').read().split('\n')
idx = next(k for k, t in enumerate(S) if t.lstrip().startswith("'image1.png': dict("))
head, sep, comment = S[idx].partition('  # ')
assert sep, S[idx][:80]
pre = head.split('split=')[0].rstrip(' ,)')          # 至 c0=3.04, 为止
mode = sys.argv[1]
# 切分点取 R2 绑定 pass 之前的原形（side_row 在 6a-F 之前执行，彼时「则」后尚无 \nobreak）
val = r"split=r'\(\overrightarrow{A_{1}B}'" if mode == 'arm' else 'split=None'
S[idx] = pre + ', ' + val + '),' + ('  # ' + comment if comment else '')
io.open(P, 'w', encoding='utf-8', newline='').write('\n'.join(S))
t = io.open(P, encoding='utf-8').read()
ast.parse(t)
print('mode=%s AST OK ->' % mode, [x for x in t.split('\n') if x.lstrip().startswith("'image1.png': dict(")][0][:140])
