# -*- coding: utf-8 -*-
"""修复 qp-layout.tex 被 heredoc 吞掉反斜杠的 \\thickmuskip 行（tab+hickmuskip=5mu%Y1 → 正体）。"""
p = r'C:\提示词\工作区\字替对照-0909\variantF\qp-layout.tex'
s = open(p, encoding='utf-8').read()
bad = '\thickmuskip=5mu%Y1'
assert bad in s, '未找到损坏行'
good = ('% F 片C 0909 #29（数学符号间距刚性化）：unicode-math 默认 \\thickmuskip=5mu plus 5mu——\n'
        '%   关系符号（＝/∥ 等）两侧胶被 \\emergencystretch 拉伸至自然值 2.2 倍（实测正文 1.2–2.35mm，\n'
        '%   自然 5mu＝0.99mm；表格单行格恒自然）。去 plus/minus 刚性化，正文墨隙回到 5mu 自然值。\n'
        '\\thickmuskip=5mu')
s = s.replace(bad, good)
open(p, 'w', encoding='utf-8').write(s)
s2 = open(p, encoding='utf-8').read()
print('fixed:', '\\thickmuskip=5mu' in s2, '| stray tab-hick:', ('\thickmuskip' in s2))
