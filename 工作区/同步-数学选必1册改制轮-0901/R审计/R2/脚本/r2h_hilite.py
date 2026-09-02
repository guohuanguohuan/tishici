# -*- coding: utf-8 -*-
"""R2——显影像素红色高亮叠加图（精确可视化被图盖住的墨迹）。"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz, numpy as np

W = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\PDF'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\输出'
DPI = 150; SCALE = DPI / 72.0; INK = 220

HITS = {
 'X1': [1], 'C': [27, 48, 53, 65], 'B': [23, 53, 61, 71, 76],
}

def gray(page):
    pm = page.get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
    return np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)

for code, pages in HITS.items():
    for pno1 in pages:
        doc = fitz.open(os.path.join(W, code + '.pdf'))
        page = doc[pno1 - 1]
        rects = [fitz.Rect(it['bbox']) for it in page.get_image_info()
                 if not fitz.Rect(it['bbox']).is_empty and fitz.Rect(it['bbox']).width > 1]
        g1 = gray(page)
        for bb in rects:
            page.add_redact_annot(fitz.Rect(bb.x0-1, bb.y0-1, bb.x1+1, bb.y1+1) & page.rect)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE, text=fitz.PDF_REDACT_TEXT_NONE, graphics=0)
        g2 = gray(page)
        diff = (g2 < INK) & ~(g1 < INK)
        ys, xs = np.nonzero(diff)
        pm = page.get_pixmap(dpi=DPI)  # RGB，去图态
        arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n).copy()
        # 放大显影标记：显影像素及其±3px邻域染红
        mask = np.zeros((pm.height, pm.width), dtype=bool)
        if len(ys):
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    yy = np.clip(ys + dy, 0, pm.height - 1); xx = np.clip(xs + dx, 0, pm.width - 1)
                    mask[yy, xx] = True
        arr[mask] = [255, 0, 0]
        # 裁剪保存（全页缩到110dpi太高，裁显影区±120pt）
        if len(ys):
            y0 = max(0, int(ys.min()/SCALE - 100)); y1 = min(pm.height, int(ys.max()/SCALE + 100))
            x0 = max(0, int(xs.min()/SCALE - 80)); x1 = min(pm.width, int(xs.max()/SCALE + 220))
        else:
            y0, y1, x0, x1 = 0, 300, 0, 900
        sub = arr[y0:y1, x0:x1]
        from PIL import Image
        Image.fromarray(sub).save(os.path.join(OUT, 'h_%s_p%d.png' % (code, pno1)))
        print('saved h_%s_p%d.png region=%dx%d 显影px=%d' % (code, pno1, sub.shape[1], sub.shape[0], len(ys)))
        doc.close()
print('DONE')
