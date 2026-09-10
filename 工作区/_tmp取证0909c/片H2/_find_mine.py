# -*- coding: utf-8 -*-
"""在我方 main.pdf 中定位目标数学式（ABCD 串/分式/减号）——rawdict 双口径。"""
import sys
import fitz

PDF = r'C:/提示词/工作区/字替对照-0909/variantF/main.pdf'

doc = fitz.open(PDF)
print('pages', doc.page_count)
keys = sys.argv[1:] or ['ABCD', 'ABC-', 'A1B1', 'MINE']
for pno in range(doc.page_count):
    page = doc[pno]
    d = page.get_text('dict')
    for b in d['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            for s in l['spans']:
                txt = s['text']
                if any(k in txt for k in keys):
                    bb = [round(v, 1) for v in s['bbox']]
                    print(f'p{pno+1} size={s["size"]:.2f} font={s["font"][:28]:28} bbox={bb} text={txt[:70]!r}')
