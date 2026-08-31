# -*- coding: utf-8 -*-
"""E1复审计：PDF页脚渲染断言（件标识整串＋页码数字；跨卷首页79/48/99/135）。"""
import fitz, os

OUT = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\E1审计'
EXPECT = {
    'X1': ('第1章·衔接（共20页）', [1]),
    'I1': ('第1章·清单（共20页）', [1]),
    'B':  ('第1章·讲练（共156页）', [1]),
    'C':  ('第1章·讲练（共156页）', [79]),
    'X2': ('第2章·衔接（共4页）', [1]),
    'I2': ('第2章·清单（共40页）', [1]),
    'E':  ('第2章·讲练（共197页）', [1]),
    'F':  ('第2章·讲练（共197页）', [48]),
    'G':  ('第2章·讲练（共197页）', [99]),
    'H':  ('第2章·讲练（共197页）', [135]),
}
ok = True
for code, (ident, firsts) in EXPECT.items():
    pdf = os.path.join(OUT, 'pdf_%s.pdf' % code)
    doc = fitz.open(pdf)
    p0 = doc[0]
    # 页脚区：y>750pt
    words = [w for w in p0.get_text('words') if w[1] > 750]
    words.sort(key=lambda w: w[0])
    line = ''.join(w[4] for w in words)
    x0 = words[0][0] if words else None
    exp = '%s　第%d页' % (ident, firsts[0])
    hit = exp.replace('　', '') in line.replace('　', '').replace(' ', '')
    print(code, '| p1页脚:', repr(line[:50]), '| x0=%.1f' % x0 if x0 else '',
          '| 期望:', exp, '=>', 'PASS' if hit else 'FAIL')
    if not hit: ok = False
    doc.close()
print('ALL', 'PASS' if ok else 'FAIL')
