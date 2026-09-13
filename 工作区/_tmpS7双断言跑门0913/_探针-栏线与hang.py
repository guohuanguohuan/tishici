# -*- coding: utf-8 -*-
"""⑦ 栏线红项探查（课01 p4／拓下 p13）＋衔接节 hangindent 定位。"""
import os
import re
import pymupdf

ROOT = r'C:\提示词\工作区\M2-第1章量产0911\成卷'
PT = 72 / 25.4

for it, pages in [('导学件/课时01', [3, 4]), ('拓展册/下册', [12, 13])]:
    doc = pymupdf.open(os.path.join(ROOT, it, 'main.pdf'))
    print('=====', it, '页数', doc.page_count)
    for pno in pages:
        if pno > doc.page_count:
            continue
        page = doc[pno - 1]
        ph = page.rect.height
        body_lo = ph - 20 * PT
        body_hi = 19.6 * PT
        n = 0
        for d in page.get_drawings():
            r = d['rect']
            if r.width <= 1.5 and r.height > 3:
                c = d.get('color') or d.get('fill')
                n += 1
                print(f'  p{pno} 竖线 x0={r.x0 / PT:.2f}mm y[{r.y0 / PT:.1f},{r.y1 / PT:.1f}]mm '
                      f'高{(ph - 39.2 * PT - r.height) and r.height / PT:.1f}mm '
                      f'w={d.get("width")} 色={c and tuple(round(x * 255) for x in c)}')
        if n == 0:
            print(f'  p{pno} 无细长竖线 drawing')
    doc.close()

t = open(os.path.join(ROOT, '导学件', '衔接节-1.2.1前', 'main.tex'), encoding='utf-8').read()
body = '\n'.join(ln for ln in t.split('\n') if not ln.lstrip().startswith('%'))
for i, ln in enumerate(body.split('\n')):
    if '\\hangindent' in ln:
        print('衔接节 hangindent L%d:' % i, ln.strip()[:90])
