# -*- coding: utf-8 -*-
"""并排恢复0910 诊断：g1/g2 并排带内 ⑱-2「零侵入」判据的命中行明细。"""
import re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf
import numpy as _np

BASE = r'C:\提示词\工作区\字替对照-0909\variantF'
PDF = os.path.join(BASE, 'main.pdf')
PT = 72 / 25.4
COLL = (48.8, 308.4)
COLW = 84.0 * PT
MID = (COLL[0] + COLL[1]) / 2
PAD05 = 0.5 * PT

doc = pymupdf.open(PDF)
# 找并排两图矩形（image1 691px / image2 764px）
for pno, page in enumerate(doc, 1):
    for info in page.get_image_info(xrefs=True):
        if info['width'] not in (691, 764):
            continue
        r = pymupdf.Rect(info['bbox'])
        tag = 'g1' if info['width'] == 691 else 'g2'
        cl = COLL[0] if r.x0 < (COLL[0] + COLL[1]) / 2 else COLL[1]
        infl = pymupdf.Rect(r.x0 - PAD05, r.y0 - PAD05, r.x1 + PAD05, r.y1 + PAD05)
        print(f'--- {tag} p{pno} 盒 x[{r.x0:.1f},{r.x1:.1f}] y[{r.y0:.1f},{r.y1:.1f}] 栏左{cl:.1f} 栏右{cl+COLW:.1f}')
        for b in page.get_text('dict')['blocks']:
            if b['type'] != 0:
                continue
            for L in b.get('lines', []):
                bb = pymupdf.Rect(L['bbox'])
                t = ''.join(sp['text'] for sp in L['spans'])
                if not (cl - 2 <= (bb.x0 + bb.x1) / 2 <= cl + COLW + 2):
                    continue
                if min(bb.y1, infl.y1) - max(bb.y0, infl.y0) <= 0:
                    continue
                flag = 'RECT撞' if bb.intersects(infl) else ''
                print(f'   y[{bb.y0:.1f},{bb.y1:.1f}] x[{bb.x0:.1f},{bb.x1:.1f}] {flag} | {t[:60]}')
