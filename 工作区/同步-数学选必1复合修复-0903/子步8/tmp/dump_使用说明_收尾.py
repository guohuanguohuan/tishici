# -*- coding: utf-8 -*-
"""使用说明逐段dump：文本＋run级参数（字号/加粗/底纹/缩进），供T2图例校验"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
from docx import Document
from docx.oxml.ns import qn

PATH = r'C:\提示词\高中数学\高中数学同步\人教B版选必1·使用说明.docx'
doc = Document(PATH)
rows = []
for i, p in enumerate(doc.paragraphs):
    pPr = p._p.pPr
    ind = pshd = None
    if pPr is not None:
        e = pPr.find(qn('w:ind'))
        if e is not None:
            ind = {k.split('}')[1]: v for k, v in e.attrib.items()}
        e = pPr.find(qn('w:shd'))
        if e is not None:
            pshd = e.get(qn('w:fill'))
    runs = []
    for r in p.runs:
        rpr = r._r.rPr
        b = sz = rshd = None
        if rpr is not None:
            be = rpr.find(qn('w:b'))
            b = be is not None and be.get(qn('w:val')) not in ('0', 'false')
            se = rpr.find(qn('w:sz'))
            if se is not None: sz = se.get(qn('w:val'))
            she = rpr.find(qn('w:shd'))
            if she is not None: rshd = she.get(qn('w:fill'))
        runs.append({'t': r.text, 'b': b, 'sz': sz, 'shd': rshd})
    rows.append({'i': i, 'text': p.text, 'ind': ind, 'pshd': pshd, 'runs': runs})
print('段落总数 =', len(rows))
for r in rows:
    print('---[%02d] ind=%s pshd=%s' % (r['i'], r['ind'], r['pshd']))
    print('    TEXT: %s' % r['text'][:120])
    for x in r['runs']:
        print('    RUN b=%s sz=%s shd=%s | %s' % (x['b'], x['sz'], x['shd'], x['t'][:60]))
json.dump(rows, open(r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp\dump_使用说明_收尾.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sec = doc.sections[0]
print('=== 版式: pgSz=%sx%s pgMar L%s R%s T%s B%s' % (sec.page_width, sec.page_height, sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin))
