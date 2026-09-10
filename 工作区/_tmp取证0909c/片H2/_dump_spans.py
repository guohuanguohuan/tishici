# -*- coding: utf-8 -*-
"""导出我方 main.pdf 全部 span（页/字体/字号/bbox/文本）到 JSON，供定位。"""
import json
import fitz

PDF = r'C:/提示词/工作区/字替对照-0909/variantF/main.pdf'
OUT = r'C:/提示词/工作区/_tmp取证0909c/片H2/我方_spans.json'

doc = fitz.open(PDF)
recs = []
for pno in range(doc.page_count):
    page = doc[pno]
    d = page.get_text('dict')
    for bi, b in enumerate(d['blocks']):
        if b['type'] != 0:
            continue
        for li, l in enumerate(b['lines']):
            for s in l['spans']:
                if not s['text'].strip():
                    continue
                recs.append(dict(page=pno + 1, blk=bi, line=li, font=s['font'], size=round(s['size'], 2),
                                 bbox=[round(v, 2) for v in s['bbox']], text=s['text']))
json.dump(recs, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('spans', len(recs), '->', OUT)
# 快捷统计字体
from collections import Counter
c = Counter(r['font'] for r in recs)
for k, v in c.most_common(30):
    print(v, k)
