# -*- coding: utf-8 -*-
"""探查：各练/拓节 \anshang 双位档起点键＋节行位（只读）。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/答案册/body.tex"
lines = io.open(B, encoding='utf-8').read().splitlines()
sec = None
lastpair = None
for i, l in enumerate(lines):
    m = re.search(r'\\jietitle\{([^}]*)\}', l)
    if m:
        sec = m.group(1)
        if any(t in sec for t in ('练习件', '拓展册', '测评')):
            print('L%d 节=%s' % (i + 1, sec))
    m = re.match(r'% pair:(\S+)', l.strip())
    if m:
        lastpair = m.group(1)
    if '\\setlength{\\anshang}' in l:
        print('   L%d setlength %s｜前键=%s' % (i + 1, l.strip()[:40], lastpair))
