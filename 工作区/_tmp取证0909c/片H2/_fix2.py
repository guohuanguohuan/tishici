# -*- coding: utf-8 -*-
"""修复 qp-layout 的 dfrac 行 ＋ _variant.py 的 patch_post bug（纯字符串替换版）。"""
p = r'C:/提示词/工作区/字替对照-0909/variantF/qp-layout.tex'
s = open(p, encoding='utf-8').read()
good = chr(92) + 'let' + chr(92) + 'frac' + chr(92) + 'dfrac'      # \let\frac\dfrac
# 将所有 '%%%...\let\frac\dfrac' 收敛为注释态
lines = []
for line in s.splitlines():
    st = line.lstrip('%')
    if st.startswith(good) or st == good:
        lines.append('%' + good)
    else:
        lines.append(line)
s = '\n'.join(lines) + '\n'
if good not in s:
    s = s.replace(chr(92) + 'medmuskip=2mu', chr(92) + 'medmuskip=2mu\n%' + good, 1)
open(p, 'w', encoding='utf-8').write(s)
print([l for l in s.splitlines() if 'dfrac' in l or 'DeclareMathSizes' in l or 'medmuskip=' in l])

p2 = r'C:/提示词/工作区/_tmp取证0909c/片H2/_variant.py'
v = open(p2, encoding='utf-8').read()
v = v.replace("'H2_STRH_ENABLE = ' + strh", "'H2_STRH_ENABLE = ' + str(strh)")
open(p2, 'w', encoding='utf-8').write(v)
print('variant fixed:', 'str(strh)' in v)
