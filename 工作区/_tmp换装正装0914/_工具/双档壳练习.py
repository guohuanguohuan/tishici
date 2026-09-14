# -*- coding: utf-8 -*-
"""双档壳生成：每件 main-true.tex（\mthreepure=0）＋ main-pure.tex（=1），仿试迁 0913 壳。
模板用 _PIECE_ 占位＋replace 注名（禁 % 格式化：壳面注释含字面 %）。"""
import io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
TREE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'M2练习本')
HEAD_T = ('% ============================================================\n'
          '% _PIECE_ 换装正装波2·练习本·含详解印本（\\showans true＝默认档）→ main-true.pdf\n'
          '% 编译：xelatex main-true.tex（两遍）\n'
          '% ============================================================\n'
          '\\def\\mthreepure{0}\n'
          '\\input{main.tex}\n')
HEAD_P = ('% ============================================================\n'
          '% _PIECE_ 换装正装波2·练习本·纯题版（\\mthreepure=1 → qp-m3 [pure] 等效）→ main-pure.pdf\n'
          '% 编译：xelatex main-pure.tex（两遍）\n'
          '% ============================================================\n'
          '\\def\\mthreepure{1}\n'
          '\\input{main.tex}\n')
for piece in sorted(os.listdir(TREE)):
    d = os.path.join(TREE, piece)
    if not os.path.isdir(d):
        continue
    for name, head in (('main-true.tex', HEAD_T), ('main-pure.tex', HEAD_P)):
        with io.open(os.path.join(d, name), 'w', encoding='utf-8', newline='\n') as f:
            f.write(head.replace('_PIECE_', piece))
    print('[壳]', piece)
