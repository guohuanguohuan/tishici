# -*- coding: utf-8 -*-
import fitz, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = fitz.open('C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时04-点斜式与斜截式/main-true.pdf')
print('pages', len(doc))
for pno, page in enumerate(doc, 1):
    rules = []
    for dd in page.get_drawings():
        r = dd['rect']
        if dd['fill'] is None and dd['color'] and all(abs(c-0.478)<0.01 for c in dd['color']) and r.width > 100:
            rules.append((round(r.x0,1), round(r.y0,1), round(r.x1,1), round(r.y1,1)))
    grays = [ (round(d['rect'].y0,1), round(d['rect'].y1,1)) for d in page.get_drawings() if d['fill'] and all(abs(c-0.941)<0.01 for c in d['fill']) and d['rect'].width>100 and d['rect'].height>20]
    txt = page.get_text()
    first = txt.strip().split('\n')[0][:40]
    last = txt.strip().split('\n')[-1][:40]
    print(f'p{pno}: rules={rules}')
    print(f'    grays={len(grays)} first="{first}" last="{last}"')
doc.close()
