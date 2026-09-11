# -*- coding: utf-8 -*-
"""_探针-图门咬合.py —— 顶格图门（位图口径）咬合性反证探针（本探针只读件、不改件）。

改后 断言顶格.py 的 (e) 在真件上判「越栏 0／压字 0／位图×6」→ 通过。零容忍门须证明它会红：
本探针把件源码读进内存、仅两处字符串替换后 exec（BASE 指向件目录，主件字节不动）——
  T1 图矩形纵向拉长 60pt（压入下方正文行）→ 应报「压字」并判未通过；
  T2 图矩形横向右移 30pt（越出栏带右界）→ 应报「越栏」并判未通过；
  T3 删掉一件图（位图 6→5）→ 应因 n_fig!=6 判未通过。
用法：python _探针-图门咬合.py T1|T2|T3
"""
import io
import os
import sys

PIECE = r'C:/提示词/工作区/字替对照-0909/variantF/断言顶格.py'
src = io.open(PIECE, encoding='utf-8').read()
# BASE 由 __file__ 推导→改钉件目录（探针自身在取证目录，须回指件）
src = src.replace("BASE = os.path.dirname(os.path.abspath(__file__))",
                  "BASE = r'C:/提示词/工作区/字替对照-0909/variantF'")
OLD = "        r = pymupdf.Rect(info['bbox'])"
assert src.count(OLD) == 1, '锚点失配（图矩形取值行）'
mode = sys.argv[1] if len(sys.argv) > 1 else 'T1'
if mode == 'T1':
    NEW = "        r = pymupdf.Rect(info['bbox']); r.y1 += 60"
elif mode == 'T2':
    NEW = "        r = pymupdf.Rect(info['bbox']); r.x0 += 30; r.x1 += 30"
elif mode == 'T3':
    NEW = ("        if info['width'] == 691:   # 探 T3：抹去 g1-prism 一件\n"
           "            continue\n" + OLD)
else:
    raise SystemExit('mode ∈ {T1,T2,T3}')
src = src.replace(OLD, NEW)
g = {'__name__': '__probe__', '__file__': PIECE}
try:
    exec(compile(src, PIECE, 'exec'), g)
except SystemExit as e:
    print(f'[{mode}] 探针件 exit={e.code}')
    sys.exit(0)
print(f'[{mode}] 探针件未退出（异常）')
sys.exit(2)
