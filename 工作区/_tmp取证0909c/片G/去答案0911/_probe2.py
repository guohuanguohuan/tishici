# -*- coding: utf-8 -*-
import io, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')
import pymupdf
C = r'C:/提示词/工作区/字替对照-0909'
F = os.path.join(C, 'variantF')
A = os.path.join(C, '导学件答案册-v1')
PT = 72 / 25.4
MARGIN = 17.2 * PT
COLSEP = 7.6 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
TOP = 19.6 * PT
TEXTH = 842.0 - TOP - 20 * PT

doc = pymupdf.open(os.path.join(F, 'main.pdf'))
print('pages', doc.page_count)
# 1) p5 栏线侦查
pg = doc[4]
for d in pg.get_drawings():
    r = d['rect']
    if r.width <= 2.0 and r.height >= 30 and abs(r.x0 - MID) <= 6 and abs(r.x1 - MID) <= 6:
        c = d.get('color') or d.get('fill')
        print('p5 近缝线 rect', [round(v, 1) for v in r], 'h_mm=%.1f' % (r.height / PT), 'color', c)
# 对照 p4
pg4 = doc[3]
for d in pg4.get_drawings():
    r = d['rect']
    if r.width <= 2.0 and r.height >= 0.5 * TEXTH and (abs(r.x0 - MID) <= 2 or abs(r.x1 - MID) <= 2):
        print('p4 栏线 h_mm=%.1f' % (r.height / PT), d.get('color'))

# 2) ③ 残余超高定界符语境（p4/p5 的括号字符 bbox y → 找同线文本）
for pno in (4, 5):
    p = doc[pno - 1]
    for blk in p.get_text('rawdict')['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk['lines']:
            for sp in ln['spans']:
                for ch in sp['chars']:
                    if ch['c'] in '()[]{}' and (ch['bbox'][3] - ch['bbox'][1]) > 11.0:
                        y = ch['bbox'][1]
                        txt = ''.join(''.join(c2['c'] for s2 in l2['spans'] for c2 in s2['chars'])
                                      for l2 in blk['lines']
                                      if abs(l2['bbox'][1] - y) < 9)
                        print(f'p{pno} 超高{ch["c"]!r} y={y:.0f} h={ch["bbox"][3]-ch["bbox"][1]:.2f} 语境: {txt[:64]}')
                        break

# 3) ㉑c 答案册失败项的实际提取文本
ad = pymupdf.open(os.path.join(A, 'main.pdf'))
at = ''.join(pg.get_text() for pg in ad)
for i, l in enumerate(at.split('\n')):
    if '[答案]' in l:
        print('ANS', i, repr(l[:96]))
ad.close()
