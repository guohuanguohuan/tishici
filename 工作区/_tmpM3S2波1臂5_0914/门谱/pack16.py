# -*- coding: utf-8 -*-
"""pack16.py — 课时16 main.tex 一次性改装：\kongbai→\kongbai{} ＋ est>8 29键 {\ansblockgrayfalse 包装}。"""
import io, sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时16-2.7.2抛物线性质'
P = PIECE + '/main.tex'
s = open(P, encoding='utf-8').read()

n0 = s.count('\\kongbai')
s = s.replace('\\kongbai', '\\kongbai{}')
print('\\kongbai 补括号:', n0, '处')

RULED = ['2章-练-课时16-03', '2章-练-课时16-12', '2章-练-课时16-14', '2章-练-课时16-15',
         '2章-练-课时16-16', '2章-拓-课时16-02', '2章-拓-课时16-04', '2章-拓-课时16-05',
         '2章-拓-课时16-06', '2章-拓-课时16-07', '2章-拓-课时16-08', '2章-拓-课时16-10',
         '2章-拓-课时16-11', '2章-拓-课时16-12', '2章-拓-课时16-13', '2章-拓-课时16-14',
         '2章-拓-课时16-15', '2章-拓-课时16-17', '2章-拓-课时16-23', '2章-拓-课时16-24',
         '2章-拓-课时16-25', '2章-拓-课时16-26', '2章-拓-课时16-27', '2章-拓-课时16-28',
         '2章-拓-课时16-29', '2章-拓-课时16-30', '2章-导-课时16-G3', '2章-导-课时16-G4',
         '2章-导-课时16-G5']

done = 0
for k in RULED:
    tag = '\\begin{ansblock}[' + k + ']'
    i = s.find(tag)
    assert i >= 0, '缺块 ' + k
    assert s[i - 1] != 'e' or not s[max(0, i - 20):i].endswith('{\\ansblockgrayfalse\n')
    if s[max(0, i - 20):i].find('\\ansblockgrayfalse') >= 0:
        continue
    s = s[:i] + '{\\ansblockgrayfalse\n' + s[i:]
    j = s.find('\\end{ansblock}', i)
    assert j >= 0, '缺块尾 ' + k
    j_end = j + len('\\end{ansblock}')
    s = s[:j_end] + '}' + s[j_end:]
    done += 1
print('括线包装:', done, '块')

open(P, 'w', encoding='utf-8', newline='').write(s)
print('写回 →', P)
