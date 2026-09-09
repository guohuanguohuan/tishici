# -*- coding: utf-8 -*-
"""R1/R4/R5/P-D pass 锚串普查：在 E 定稿 body.tex 上数各 pass 目标，钉断言期望值。"""
import re
s = open('../../variantE/body.tex', encoding='utf-8').read()
lines = s.split('\n')
BS = chr(92)
pats = [
    (BS*2 + r'left\(', BS+r'left('),
    (BS*2 + r'right\)', BS+r'right)'),
    (BS*2 + r'left\|', BS+r'left|'),
    (BS*2 + r'right\|', BS+r'right|'),
    (BS*2 + r'left' + BS*2 + 'langle', BS+'left'+BS+'langle'),
    (BS*2 + r'right' + BS*2 + 'rangle', BS+'right'+BS+'rangle'),
    (BS*2 + r'left' + BS*2 + r'{', BS+'left'+BS+'{'),
    (BS*2 + r'right\.', BS+'right.'),
    (BS*2 + r'right\. ', BS+'right.+空格'),
    (r'~~', '~~'),
    ('＝', '＝'), ('＋', '＋'), ('－', '－'), ('√', '√'), ('×', '×'),
    (r'\) \(', r'\) \(（同行接合位）'),
    (r'\)\n\n\(', r'\)空行\(（跨段接合位）'),
]
print('—— 计数 ——')
for c, nm in pats:
    print(f'  {nm}: {len(re.findall(c, s))}')

def show(patt, label, n=8):
    hits = [(i+1, l) for i, l in enumerate(lines) if re.search(patt, l)]
    print(f'== {label}: {len(hits)} 行')
    for i, l in hits[:n]:
        m = re.search(patt, l)
        a = max(0, m.start()-38)
        print(f'   L{i}: …{l[a:m.end()+38]}…')

show(BS*2 + r'right\. ', 'R4②')
show(r'~~', 'R4① ~~')
show('＝', 'R5 ＝')
show('＋|－', 'R5 ＋－')
show(r'\) \(|\)\n\n\(', 'R4③ 接合位')
show(BS*2 + r'left' + BS*2 + r'{', 'R1 cases')
