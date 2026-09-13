# -*- coding: utf-8 -*-
"""⑦ 栏线门原样复跑（课01）逐页定位。"""
import pymupdf
import S7双断言跑门 as G

pdfp = r'C:\提示词\工作区\M2-第1章量产0911\成卷\导学件\课时01\main.pdf'
doc = pymupdf.open(pdfp)
n_pdf = doc.page_count
cfg = G.FAM['D']
pw, ph = cfg['page']
cls, colw = G.col_lefts(cfg, pw)
MID = (min(cls) + max(cls) + colw) / 2
TOP, BOT = cfg['top'], cfg['bot']
print('n_pdf', n_pdf, 'MID', round(MID, 1), '阈(pt) 末页', round(0.22 * (ph - TOP - BOT), 1),
      '非末', round(0.5 * (ph - TOP - BOT), 1))
rule_found = {}
for pno in range(1, n_pdf + 1):
    page = doc[pno - 1]
    hit = 0
    for d in page.get_drawings():
        r = d['rect']
        if not (r.width <= 1.5 and r.height >= (0.22 if pno == n_pdf else 0.5) * (ph - TOP - BOT)):
            continue
        if abs(r.x0 - MID) > 2 and abs(r.x1 - MID) > 2:
            continue
        c = d.get('color') or d.get('fill')
        if c and G.rgb255(c) == (189, 189, 189):
            rule_found[pno] = d
            hit += 1
    print(f'p{pno} 命中{hit}')
print('rule_found', sorted(rule_found))
doc.close()
