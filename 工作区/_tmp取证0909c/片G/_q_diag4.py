# -*- coding: utf-8 -*-
r"""临时探针4：六图邻域文本行全列（判断标签/正文可分性）。"""
import sys
sys.path.insert(0, r'C:/提示词/工作区/_tmp取证0909c/片G')
import pymupdf
from 片G实测 import PT, MARGIN, COLW, COLSEP, MID, SRC, MAP, diag_items, cluster, merge_rows

doc = pymupdf.open(r'C:/提示词/工作区/字替对照-0909/variantF/main.pdf')
allc = []
for pno, page in enumerate(doc, 1):
    for r, nl in merge_rows(cluster(diag_items(page.get_drawings()), 8 / 25.4 * PT)):
        if r.width / PT >= 15 and r.height / PT >= 10 and nl >= 3:
            allc.append((pno, r, nl))
allc.sort(key=lambda z: (z[0], z[1].y0))
for i, (pno, rc, nl) in enumerate(allc):
    tag, sn, wbox, frag = MAP[i]
    col = 1 if rc.x0 < MID else 2
    cl = MARGIN if col == 1 else MARGIN + COLW + COLSEP
    page = doc[pno - 1]
    print('\n=== [%d] %s p%d c%d 簇 x[%.2f,%.2f] y[%.2f,%.2f] ===' % (
        i, tag, pno, col, rc.x0 / PT, rc.x1 / PT, rc.y0 / PT, rc.y1 / PT))
    lo, hi = rc.y0 - 14 * PT, rc.y1 + 14 * PT
    rows = []
    for b in page.get_text('dict')['blocks']:
        for ln in b.get('lines', []):
            r = pymupdf.Rect(ln['bbox'])
            t = ''.join(sp['text'] for sp in ln['spans'])
            if not t.strip():
                continue
            cx = (r.x0 + r.x1) / 2
            if not (cl - 2 <= cx <= cl + COLW + 2):
                continue
            if r.y1 < lo or r.y0 > hi:
                continue
            sz = max(sp['size'] for sp in ln['spans'])
            rows.append((r.y0, r.y1, r.x0, r.x1, r.width, sz, t))
    for y0, y1, x0, x1, w, sz, t in sorted(rows):
        rel = ''
        if y1 < rc.y0:
            rel = 'ABOVE'
        elif y0 > rc.y1:
            rel = 'BELOW'
        else:
            rel = 'OVERLAP-CLUSTER'
        print('   y[%7.2f,%7.2f] x[%7.2f,%7.2f] w%6.2f sz%5.2f %-16s |%s|' % (
            y0 / PT, y1 / PT, x0 / PT, x1 / PT, w / PT, sz, rel, t[:34]))
