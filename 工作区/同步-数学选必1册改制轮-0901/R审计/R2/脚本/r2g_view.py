# -*- coding: utf-8 -*-
"""R2——命中处视觉定性：渲染去图前后对比PNG＋显影bbox细节＋相交文字span提取。"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz, numpy as np

W = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\PDF'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\输出'
DPI = 150; SCALE = DPI / 72.0; INK = 220

HITS = {  # code: [(page, ytop_pt, ybot_pt)]
 'X1': [(1, 369.6, 369.6)],
 'C':  [(27, 501.6, 501.6), (48, 597.1, 597.1), (53, 42.7, 506.9), (65, 229.0, 229.0)],
 'B':  [(23, 15.4, 23.5), (53, 42.7, 187.7), (61, 575.0, 575.0), (71, 413.3, 413.3), (76, 661.4, 661.4)],
}

def ink(page):
    pm = page.get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
    return np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width) < INK

for code, plist in HITS.items():
    doc = fitz.open(os.path.join(W, code + '.pdf'))
    for (pno1, yt, yb) in plist:
        pno = pno1 - 1
        page = doc[pno]
        rects = [fitz.Rect(it['bbox']) for it in page.get_image_info()
                 if not fitz.Rect(it['bbox']).is_empty and fitz.Rect(it['bbox']).width > 1]
        a1 = ink(page)
        for bb in rects:
            page.add_redact_annot(fitz.Rect(bb.x0-1, bb.y0-1, bb.x1+1, bb.y1+1) & page.rect)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE,
                              text=fitz.PDF_REDACT_TEXT_NONE,
                              graphics=0)
        a2 = ink(page)
        diff = a2 & ~a1
        ys, xs = np.nonzero(diff) if diff.any() else (np.array([]), np.array([]))
        if len(ys):
            n = len(ys)
            # 显影像素群：取主连通带的bbox（简化：全部像素的bbox＋分簇by行）
            y0, y1 = ys.min()/SCALE, ys.max()/SCALE
            x0, x1 = xs.min()/SCALE, xs.max()/SCALE
            rows = np.unique(ys)
        else:
            n = 0; y0=y1=x0=x1=0; rows=[]
        # 相交文字span
        spans = []
        for blk in doc[pno].get_text('dict')['blocks']:  # 注意page已redact，文字保留
            if blk['type'] != 0: continue
            for ln in blk['lines']:
                for sp in ln['spans']:
                    r = fitz.Rect(sp['bbox'])
                    if r.y0 < 40: band = 'H'
                    elif r.y1 > 775: band = 'F'
                    else: band = 'B'
                    for bb in rects:
                        if r.intersects(bb) and band in ('H','F') or (r & bb).get_area() > 15:
                            spans.append((sp['text'][:20], round(r.y0,1), round(r.y1,1), band, round((r & bb).get_area(),1)))
                            break
        print('%s p%d: 显影%dpx bbox=[%.1f,%.1f]x[%.1f,%.1f] 行数=%d 相交页眉页脚span=%s' % (
            code, pno1, n, x0, x1, y0, y1, len(rows), [s for s in spans if s[3] in ('H','F')][:4]))
        # 对比PNG：显影区±25pt
        clip = fitz.Rect(max(0,x0-25), max(0,y0-25), min(page.rect.x1,x1+25), min(page.rect.y1,y1+25))
        if clip.width < 60: clip.x1 = clip.x0 + 300
        if clip.height < 40: clip.y1 = clip.y0 + 80
        pm1 = doc[pno].get_pixmap(dpi=110, clip=clip)  # 已是去图态
        pm1.save(os.path.join(OUT, 'v_%s_p%d_after.png' % (code, pno1)))
        doc2 = fitz.open(os.path.join(W, code + '.pdf'))
        pm0 = doc2[pno].get_pixmap(dpi=110, clip=clip)
        pm0.save(os.path.join(OUT, 'v_%s_p%d_before.png' % (code, pno1)))
        doc2.close()
    doc.close()
print('DONE')
