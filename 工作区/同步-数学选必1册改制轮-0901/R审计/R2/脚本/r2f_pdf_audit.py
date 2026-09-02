# -*- coding: utf-8 -*-
"""R2终审计——PDF层：①页数/A4；②图底max（≤797断言）；③页眉页脚/正文零盖复算
（redaction去图差分：显影＝去图后有墨&原图无墨，150dpi像素，>30px计页位；分带：页眉<40pt/页脚>775pt）。只读原文档（redaction仅内存）。"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz, numpy as np

W = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\PDF'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\输出'
DPI = 150; SCALE = DPI / 72.0
INK = 220          # 灰度阈值：<220 为墨
TH = 30            # 显影像素>30 计页位（RF口径）

print('fitz', fitz.__doc__.split(':')[0] if fitz.__doc__ else '')
for c in ('PDF_REDACT_IMAGE_REMOVE', 'PDF_REDACT_TEXT_NONE'):
    print(c, getattr(fitz, c, 'N/A'))

def render(page):
    pm = page.get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
    a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
    return a < INK

report = {}
for code in ('X1', 'C', 'B'):
    doc = fitz.open(os.path.join(W, code + '.pdf'))
    res = {'pages': doc.page_count, 'size': [], 'img_bottom_max': 0, 'img_bottom_over797': 0,
           'img_bottom_over785': 0, 'perpage': []}
    hits = []
    for pno in range(doc.page_count):
        page = doc[pno]
        r = page.rect
        if pno < 1 or code == 'X1':
            res['size'].append((round(r.width, 1), round(r.height, 1)))
        infos = page.get_image_info()
        bmax = 0.0
        rects = []
        for it in infos:
            bb = fitz.Rect(it['bbox'])
            if bb.is_empty or bb.width < 1 or bb.height < 1: continue
            rects.append(bb)
            bmax = max(bmax, bb.y1)
        res['img_bottom_max'] = max(res['img_bottom_max'], round(bmax, 1))
        if bmax > 797: res['img_bottom_over797'] += 1
        if bmax > 785: res['img_bottom_over785'] += 1
        # ---- redaction 去图差分 ----
        if rects:
            a1 = render(page)
            for bb in rects:
                bb2 = fitz.Rect(bb.x0-1, bb.y0-1, bb.x1+1, bb.y1+1) & page.rect
                if not bb2.is_empty:
                    page.add_redact_annot(bb2)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE,
                                  text=fitz.PDF_REDACT_TEXT_NONE,
                                  graphics=fitz.PDF_REDACT_LINE_ART_NONE if hasattr(fitz, 'PDF_REDACT_LINE_ART_NONE') else 0)
            a2 = render(page)
            if a1.shape != a2.shape:
                h = min(a1.shape[0], a2.shape[0]); w = min(a1.shape[1], a2.shape[1])
                diff = a2[:h, :w] & ~a1[:h, :w]
            else:
                diff = a2 & ~a1
            n = int(diff.sum())
            if n > 0:
                ys, xs = np.nonzero(diff)
                ytop_pt = ys.min() / SCALE; ybot_pt = ys.max() / SCALE
                if ytop_pt < 40: band = '页眉带'
                elif ybot_pt > 775: band = '页脚带'
                else: band = '正文带'
                if n > TH:
                    hits.append((pno + 1, band, n, round(ytop_pt, 1), round(ybot_pt, 1)))
                    res['perpage'].append({'p': pno + 1, '带': band, '显影px': n, 'y': [round(ytop_pt,1), round(ybot_pt,1)]})
    res['被盖页位(>30px)'] = hits
    report[code] = res
    print('%s: pages=%d A4样本=%s 图底max=%s >797:%d >785:%d 被盖页位=%s' % (
        code, res['pages'], res['size'][:1], res['img_bottom_max'], res['img_bottom_over797'],
        res['img_bottom_over785'], hits))
    doc.close()

json.dump(report, open(os.path.join(OUT, 'r2f_pdf零盖复算.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('DONE')
