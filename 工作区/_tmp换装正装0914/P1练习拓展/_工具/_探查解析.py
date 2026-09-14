# -*- coding: utf-8 -*-
"""探查 练/拓 段 ansline{解析} 位置与内容＋ansitem 值形态（只读）。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/答案册/body.tex"
b = io.open(B, encoding='utf-8').read()
lines = b.splitlines()
cur = None
for i, l in enumerate(lines):
    m = re.match(r'% pair:(\S+)', l.strip())
    if m:
        cur = m.group(1)
    m = re.match(r'\\ansline\{解析\}\{(.*)\}\s*$', l.strip())
    if m:
        v = m.group(1)
        print('L%d 前键=%s 长度=%d' % (i + 1, cur, len(v)))
        print('   内容:', v[:180])
# 值形态抽看：92/94 各 3 键
for pref, idx in (('练-课时92-', [1, 10, 15]), ('练-课时94-', [3, 16])):
    seg = b.split('\\jietitle{%s' % ('9.2' if '92' in pref else '9.4'), 1)[1]
    seg = seg.split('\\jietitle', 1)[0]
    pend = None
    for l in seg.splitlines():
        m = re.match(r'% pair:(\S+)', l.strip())
        if m:
            pend = m.group(1); continue
        m = re.match(r'\\ansitem\{(.+?)\}\{(.*)\}\s*$', l.strip())
        if m and pend:
            n = int(pend.rsplit('-', 1)[1])
            if n in idx:
                print(pend, 'label=', m.group(1), 'len=', len(m.group(2)))
                print('   ', m.group(2)[:150])
            pend = None
