# -*- coding: utf-8 -*-
"""探针脚本：SIDE_DEF 指定图的 split 键在 arm（临时真值＝硬造切分点）与 off（交付态 None）
之间切换，逐图注释尾巴原样保留。仅探针轮使用；探针结束必须跑 off。
用法：_arm2.py <imageN.png> <arm|off> [marker-tex]"""
import ast
import io
import sys

P = r'C:/提示词/工作区/字替对照-0909/variantF/postproc_daoxue.py'
KEY, MODE = sys.argv[1], sys.argv[2]
MARK = sys.argv[3] if len(sys.argv) > 3 else ''
S = io.open(P, encoding='utf-8').read().split('\n')
idx = next(k for k, t in enumerate(S) if t.lstrip().startswith("'%s': dict(" % KEY))
head, sep, comment = S[idx].partition('  # ')
assert sep, S[idx][:80]
pre = head.split('split=')[0].rstrip(' ,)')
val = "split=r'%s'" % MARK if MODE == 'arm' else 'split=None'
S[idx] = pre + ', ' + val + '),' + ('  # ' + comment if comment else '')
io.open(P, 'w', encoding='utf-8', newline='').write('\n'.join(S))
t = io.open(P, encoding='utf-8').read()
ast.parse(t)
print('%s mode=%s AST OK ->' % (KEY, MODE),
      [x for x in t.split('\n') if x.lstrip().startswith("'%s': dict(" % KEY)][0][:120])
