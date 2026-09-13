# -*- coding: utf-8 -*-
"""D 族 ⑬ 双侧对照：每件 body（行（剔注后）×pdf 散（上下文。"""
import re
import pymupdf
import S7双断言跑门 as G

ITEMS = [('导学件/课时%02d' % i) for i in range(1, 11)] + ['导学件/衔接节-1.2.1前', '导学件/章末-本章总结提升']
for it in ITEMS:
    body = G.strip_comments(G.read_sources(it))
    cnt = body.count('（')
    zhen = len(re.findall(r'\\zhentib[\{\s]', G.read_sources(it)))
    doc = pymupdf.open(r'C:\提示词\工作区\M2-第1章量产0911\成卷' + '\\' + it.replace('/', '\\') + r'\main.pdf')
    full = re.sub(r'\s+', '', ''.join(p.get_text() for p in doc))
    nslot = full.count('（）')
    nfw = full.count('（')
    doc.close()
    print(f'{it}: body（{cnt} zhentib{zhen} | pdf 全角{nfw} 槽{nslot} 散{nfw - nslot}')
    if cnt != nfw - nslot:
        for ln in body.split('\n'):
            if '（' in ln:
                print('    src:', ln.strip()[:64])
        for m in re.finditer('（', full):
            if full[m.start() + 1:m.start() + 2] != '）':
                print('    pdf:', full[max(0, m.start() - 6):m.start() + 14])
