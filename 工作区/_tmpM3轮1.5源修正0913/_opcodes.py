# -*- coding: utf-8 -*-
"""修前/修后文字流逐字符 opcode 枚举（备份件 vs 现件）"""
import sys, difflib
sys.path.insert(0, '工具')
from dxml import Document, qn
W, M = qn('w:t'), qn('m:t')

def stream(p):
    d = Document(p)
    return ''.join((n.text or '') for n in d.element.body.iter() if n.tag in (W, M))

for tag, cur in (('D', sys.argv[1]), ('S', sys.argv[2])):
    old = stream(cur + '.bak_轮15源修正0913')
    new = stream(cur)
    print('==== %s  文字流 %d → %d（差 %+d）' % (tag, len(old), len(new), len(new) - len(old)))
    for op in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if op[0] == 'equal':
            continue
        t, i1, i2, j1, j2 = op
        print('  %-7s 旧[%d:%d] 新[%d:%d] len %d→%d  旧=%r 新=%r' % (
            t, i1, i2, j1, j2, i2 - i1, j2 - j1, old[i1:i2], new[j1:j2]))
