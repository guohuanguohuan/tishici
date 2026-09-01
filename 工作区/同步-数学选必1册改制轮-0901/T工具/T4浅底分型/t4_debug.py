# -*- coding: utf-8 -*-
"""T4 调试：找出多run文字值与未并原因"""
import sys, io, zipfile
import importlib.util
spec = importlib.util.spec_from_file_location('t5', r'C:\提示词\工具\答案值分型改标.py')
t5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t5)   # 模块内已重包 stdout 为 utf-8，不再重复包（防GC关buffer）
from lxml import etree

path = sys.argv[1]
z = zipfile.ZipFile(path)
doc = etree.fromstring(z.read('word/document.xml'))
z.close()
body = doc.find(t5.q('body'))
els = list(body)
ptexts = {i: (t5.ptext(el) if el.tag == t5.q('p') else '') for i, el in enumerate(els)}
blocks = t5.scan_blocks(els, ptexts)
warn = []
for s, e in blocks:
    for k in range(s, e):
        if els[k].tag != t5.q('p') or t5.lead_label(ptexts[k]) != '【答案】':
            continue
        p = els[k]
        pieces, chip_end, region_end = t5.parse_answer_para(p)
        for ci2 in t5.find_continuations(els, ptexts, k, e):
            for c in els[ci2]:
                if t5.tag(c) in ('oMath', 'oMathPara'):
                    pieces[-1][2].append(c)
        for ps, pe, oms in pieces:
            has_txt = pe > ps and ptexts[k][ps:pe].strip() != ''
            if not has_txt or oms:
                continue
            rs = t5.isolate_runs(p, ps, pe, warn)
            if len(rs) > 1:
                print('多run值 @para%d [%d,%d) %r runs=%d' % (k, ps, pe, ptexts[k][ps:pe], len(rs)))
                for r in rs:
                    rpr = r.find(t5.q('rPr'))
                    from lxml import etree as E
                    print('   rPr=', (E.tostring(rpr) if rpr is not None else b'')[:120])
print('warns:', warn[:5])
