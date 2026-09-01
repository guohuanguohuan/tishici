# -*- coding: utf-8 -*-
"""R1审计——全页span级图文重叠全量扫描（4个全件PDF全部页＋5页件全部页）＋页脚带覆盖判定。"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
import fitz

PDF = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\PDF'
for code in ['X1','I1','B','E','X2','I2','C','F','G','H']:
    doc = fitz.open(os.path.join(PDF, code + '.pdf'))
    n = doc.page_count
    real = []
    for pi in range(n):
        page = doc[pi]
        spans = []
        for blk in page.get_text('dict')['blocks']:
            if blk['type'] != 0: continue
            for ln in blk['lines']:
                for sp in ln['spans']:
                    if sp['text'].strip():
                        spans.append(sp)
        imgs = []
        for img in page.get_images(full=True):
            for R in page.get_image_rects(img[0]):
                imgs.append(R)
        for R in imgs:
            for sp in spans:
                inter = fitz.Rect(sp['bbox']) & R
                if not inter.is_empty and inter.get_area() > 15:
                    is_footer = sp['bbox'][1] > 780
                    real.append((pi+1, tuple(round(v,1) for v in R), round(inter.get_area(),1),
                                 'FOOTER' if is_footer else 'BODY', sp['text'][:30]))
    # 汇总按页
    from collections import Counter
    bypage = Counter(r[0] for r in real)
    foot = [r for r in real if r[3] == 'FOOTER']
    body = [r for r in real if r[3] == 'BODY']
    print('=== %s: span级重叠候选页分布=%s | FOOTER类%d处 BODY类%d处' % (code, dict(bypage), len(foot), len(body)))
    for r in body[:8]:
        print('   BODY:', r)
    doc.close()
print('DONE')
