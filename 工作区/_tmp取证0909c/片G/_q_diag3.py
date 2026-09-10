# -*- coding: utf-8 -*-
r"""临时探针3：逐图打印 (a) 文本层行/跨度 (b) 600dpi 墨连通域，件内与素材并列。"""
import sys
sys.path.insert(0, r'C:/提示词/工作区/_tmp取证0909c/片G')
import pymupdf
from 片G实测 import (PT, MARGIN, COLW, COLSEP, MID, BOT, SRC, MAIN, MAP,
                    diag_items, cluster, merge_rows, ink_components)

idx = {'g6': 0, 'g1': 1, 'g2': 2, 'g3': 3, 'g4': 4, 'g5': 5}[sys.argv[1]]
tag, sn, wbox, frag = MAP[idx]

doc = pymupdf.open(MAIN)
allc = []
for pno, page in enumerate(doc, 1):
    for r, nl in merge_rows(cluster(diag_items(page.get_drawings()), 8 / 25.4 * PT)):
        if r.width / PT >= 15 and r.height / PT >= 10 and nl >= 3:
            allc.append((pno, r, nl))
allc.sort(key=lambda z: (z[0], z[1].y0))
pno, rc, nl = allc[idx]
page = doc[pno - 1]
col = 1 if rc.x0 < MID else 2
cl = MARGIN if col == 1 else MARGIN + COLW + COLSEP
print('件内 %s p%d c%d 簇 x[%.2f,%.2f] y[%.2f,%.2f]' % (
    tag, pno, col, rc.x0 / PT, rc.x1 / PT, rc.y0 / PT, rc.y1 / PT))
print('--- 文本层（同栏，y 在 簇±20mm 内）行 bbox / 宽mm / 文本 ---')
for b in page.get_text('dict')['blocks']:
    for ln in b.get('lines', []):
        r = pymupdf.Rect(ln['bbox'])
        t = ''.join(sp['text'] for sp in ln['spans'])
        if not t.strip():
            continue
        cx = (r.x0 + r.x1) / 2
        if not (cl - 2 <= cx <= cl + COLW + 2):
            continue
        if r.y0 > rc.y1 * PT + 20 * PT or r.y1 < rc.y0 * PT - 20 * PT:
            continue
        flag = 'WIDE' if r.width >= 15 * PT else 'narrow'
        print('  %-6s y[%.2f,%.2f] x[%.2f,%.2f] w%5.2f  |%s|' % (
            flag, r.y0 / PT, r.y1 / PT, r.x0 / PT, r.x1 / PT, r.width / PT, t[:40]))
        for sp in ln['spans']:
            sr = pymupdf.Rect(sp['bbox'])
            if sr.width < 15 * PT:
                continue
        if r.width < 15 * PT:
            for sp in ln['spans']:
                sr = pymupdf.Rect(sp['bbox'])
                print('        span y[%.2f,%.2f] x[%.2f,%.2f] w%5.2f sz%5.2f f=%s |%s|' % (
                    sr.y0 / PT, sr.y1 / PT, sr.x0 / PT, sr.x1 / PT, sr.width / PT, sp['size'], sp['font'][:18], sp['text'][:20]))
print('--- 墨连通域（簇外扩 16mm 带内）---')
band = pymupdf.Rect(cl + 0.2, max(6, rc.y0 / PT - 16), cl + COLW - 0.2, min(842, rc.y1 / PT + 16))
band = pymupdf.Rect(band.x0 * PT, band.y0 * PT, band.x1 * PT, band.y1 * PT)
for c in sorted(ink_components(page, band), key=lambda z: (z.y0, z.x0)):
    ins = 'IN ' if c.intersects(rc) else '   '
    print('  %s y[%.2f,%.2f] x[%.2f,%.2f] w%5.2f h%5.2f' % (
        ins, c.y0 / PT, c.y1 / PT, c.x0 / PT, c.x1 / PT, c.width / PT, c.height / PT))
d2 = pymupdf.open(SRC + sn)
p2 = d2[0]
k = wbox / (p2.rect.width / PT)
print('\n素材 %s 页 %.2f×%.2f k=%.4f' % (sn, p2.rect.width / PT, p2.rect.height / PT, k))
print('--- 素材文本层 ---')
for b in p2.get_text('dict')['blocks']:
    for ln in b.get('lines', []):
        r = pymupdf.Rect(ln['bbox'])
        t = ''.join(sp['text'] for sp in ln['spans'])
        if not t.strip():
            continue
        print('  y[%.2f,%.2f] x[%.2f,%.2f] w%5.2f h%5.2f |%s|' % (
            r.y0 / PT, r.y1 / PT, r.x0 / PT, r.x1 / PT, r.width / PT, r.height / PT, t[:30]))
print('--- 素材墨域 ---')
clip = pymupdf.Rect(p2.rect.x0 + 0.2, p2.rect.y0 + 0.2, p2.rect.x1 - 0.2, p2.rect.y1 - 0.2)
for c in sorted(ink_components(p2, clip), key=lambda z: (z.y0, z.x0)):
    print('  y[%.2f,%.2f] x[%.2f,%.2f] w%5.2f h%5.2f  →折w%5.2f h%5.2f' % (
        c.y0 / PT, c.y1 / PT, c.x0 / PT, c.x1 / PT, c.width / PT, c.height / PT, c.width * k / PT, c.height * k / PT))
