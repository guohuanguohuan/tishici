# -*- coding: utf-8 -*-
import sys, difflib
a = open(sys.argv[1], 'rb').read().decode('utf-8')
b = open(sys.argv[2], 'rb').read().decode('utf-8')
la = a.split('\r\n') if '\r\n' in a else a.split('\n')
lb = b.split('\r\n') if '\r\n' in b else b.split('\n')
print('行数 %d → %d' % (len(la), len(lb)))
n = 0
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, la, lb, autojunk=False).get_opcodes():
    if op == 'equal':
        continue
    n += 1
    print('---- %s 旧[%d:%d] 新[%d:%d]' % (op, i1 + 1, i2, j1 + 1, j2))
    for L in la[i1:i2]:
        print('  <', L[:120])
    for L in lb[j1:j2]:
        print('  >', L[:120])
print('变更块数 =', n)
