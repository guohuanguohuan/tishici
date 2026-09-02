# -*- coding: utf-8 -*-
"""R2——命中处结构定性：显影bbox∩（字形glyph｜矢量线drawing｜图片bbox）→ 判定被盖对象类型。"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz, numpy as np

W = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\PDF'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\输出'
DPI = 150; SCALE = DPI / 72.0; INK = 220

HITS = {
 'X1': [(1, 369.6, 369.6, 239.0, 268.3)],
 'C':  [(27, 501.6, 501.6, 42.7, 87.8), (48, 597.1, 597.1, 42.7, 101.8),
        (53, 42.7, 506.9, 153.1, 165.1), (65, 229.0, 229.0, 42.7, 89.8)],
 'B':  [(23, 15.4, 23.5, 42.7, 280.8), (53, 42.7, 187.7, 177.1, 177.1),
        (61, 575.0, 575.0, 42.7, 177.1), (71, 413.3, 413.3, 42.2, 178.1), (76, 661.4, 661.4, 42.7, 168.0)],
}

for code, plist in HITS.items():
    for (pno1, yt, yb, xt, xb) in plist:
        doc = fitz.open(os.path.join(W, code + '.pdf'))
        page = doc[pno1 - 1]
        hb = fitz.Rect(xt - 1, yt - 1, xb + 1, yb + 1)  # 显影bbox
        # 1) 字形glyph（rawdict字符bbox）
        glyphs = []
        for blk in page.get_text('rawdict')['blocks']:
            if blk['type'] != 0: continue
            for ln in blk['lines']:
                for sp in ln['spans']:
                    for ch in sp['chars']:
                        r = fitz.Rect(ch['bbox'])
                        if r.intersects(hb):
                            glyphs.append((ch['c'], round(r.y0,1), round(r.x0,1)))
        # 2) 矢量drawings
        lines = []
        for d in page.get_drawings():
            r = fitz.Rect(d['rect'])
            if r.intersects(hb) and (r & hb).get_area() > 0.5:
                lines.append((d['type'], [round(v,1) for v in d['rect']], len(d['items'])))
        # 3) 图片bbox
        imgs = []
        for it in page.get_image_info():
            r = fitz.Rect(it['bbox'])
            if r.intersects(hb):
                imgs.append([round(v,1) for v in it['bbox']])
        print('%s p%d 显影bbox=%s' % (code, pno1, [round(v,1) for v in hb]))
        print('   字形glyph∩=%s' % (glyphs[:12],))
        print('   矢量drawing∩=%s' % (lines[:6],))
        print('   图片bbox∩=%s' % (imgs[:6],))
        doc.close()
print('DONE')
