# -*- coding: utf-8 -*-
"""片H2：重写 postproc 6a-H2 串连字符 pass 块（给定断点形态；收尾落定）。
用法：python _rewrite_strh.py <allowbreak|penalty100|penalty500|penalty1000|none>"""
import sys

p = r'C:/提示词/工作区/字替对照-0909/variantF/postproc_daoxue.py'
s = open(p, encoding='utf-8').read()
mode = sys.argv[1] if len(sys.argv) > 1 else 'penalty100'
TK = chr(92) + 'text{-}'
BR = {'allowbreak': chr(92) + 'allowbreak', 'penalty100': chr(92) + 'penalty100',
      'penalty500': chr(92) + 'penalty500', 'penalty1000': chr(92) + 'penalty1000',
      'none': ''}[mode]
J = TK + BR + (' ' if BR else '')

block = (
'# 6a-H2. H2 片 0909c（E3 字母串内连字符短横化）：几何体/多面体名的字母串连接符——全品真迹为\n'
'#   短横紧贴（p06 例2 行「ABCDEF-A₁B₁C₁D₁E₁F₁」实测 w15×h2px、两侧隙 1/2px@14.176），我方数学\n'
'#   \'-\' 为长减 w28px＋\\medmuskip 两侧空档（实测 18/13px）——按 5 种字面逐处替换为 \\text{-}\n'
'#   （Times 连字符 w13×h4、两侧隙 4/4px，探针 m1/m2 同尺实测）。断点档 %s：\'%s\'\n'
'#   （原 \'-\' 断点由 \\binoppenalty=100 承担；片H2 实测 \\allowbreak(0) 过诱致 +1 页、none 致 1 处\n'
'#   overfull，取 penalty100 复刻基线断点强度）。运算符减号（a−b、MA−2MB 等）不动：全品运算符\n'
'#   减号同为长划（w40、隙 8-19px）。注：\\emph{ABCD}-\\emph{A\\textsubscript{1}…}（sec 源全角－\n'
'#   经 R5 转半角）系文本侧连字符，字形同源（w13），不在本 pass 内。\n'
'_strh_pat = [\n'
'    (r\'ABC - A_{1}B_{1}C_{1}\', r\'ABC%sA_{1}B_{1}C_{1}\', 1),\n'
'    (r\'ABCD-A_1B_1C_1D_1\', r\'ABCD%sA_1B_1C_1D_1\', 3),\n'
'    (r\'ABCD - A_{1}B_{1}C_{1}D_{1}\', r\'ABCD%sA_{1}B_{1}C_{1}D_{1}\', 1),\n'
'    (r\'A-EF-D\', r\'A%sEF%sD\', 1),\n'
'    (r\'B-AC-D\', r\'B%sAC%sD\', 1),\n'
']\n'
'for _pat, _sub, _n in _strh_pat:\n'
'    _c = body_text.count(_pat)\n'
'    assert _c == _n, f\'6a-H2 字母串连字符计数异常：{_pat} {_c}/{_n}（源漂移，人工复核）\'\n'
'    body_text = body_text.replace(_pat, _sub)\n'
'log(\'6a-H2. E3 字母串连字符短横化（片H2 0909c）：ABC-A₁B₁C₁×1／ABCD-A₁B₁C₁D₁×3／\'\n'
'    \'ABCD - A₁B₁C₁D₁×1／A-EF-D×1／B-AC-D×1 → \\\\text{-}（清后原字面 0；断点 %s）\')\n'
) % (mode, BR if BR else 'none', J, J, J, J, J, J, J, mode)

i = s.index('# 6a-H2.')
marker = '清后原字面 0'
j = s.index(marker, i)
j = s.index('\n', j) + 1
s = s[:i] + block + s[j:]
# 清理实验开关残留
s = s.replace('H2_STRH_ENABLE = True  # 片H2 实验开关（收尾删除）\n', '')
s = s.replace('_strh_pat = [] or [] or [] or [] or [', '_strh_pat = [')
s = s.replace('for _pat, _sub, _n in (_strh_pat if H2_STRH_ENABLE else []):',
              'for _pat, _sub, _n in _strh_pat:')
open(p, 'w', encoding='utf-8').write(s)
print('rewritten, mode =', mode)
