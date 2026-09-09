# -*- coding: utf-8 -*-
"""片C·600dpi ink 测量：给定 PDF 矩形与基线 y，输出墨盒（pt/mm）相对基线的位置。"""
import sys
import pymupdf
from PIL import Image

BASE = r'C:\提示词\工作区\字替对照-0909\variantF'
DPI = 600
PXPT = DPI / 72.0
PTMM = 72 / 25.4

def ink_bbox(doc, pno, rect, thr=128):
    page = doc[pno - 1]
    clip = pymupdf.Rect(rect)
    pix = page.get_pixmap(dpi=DPI, clip=clip)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')
    g = im.point(lambda v: 255 if v < thr else 0)
    bb = g.getbbox()
    if bb is None:
        return None, im, clip
    # 像素→pt（图内坐标）
    x0 = clip.x0 + bb[0] / PXPT; y0 = clip.y0 + bb[1] / PXPT
    x1 = clip.x0 + bb[2] / PXPT; y1 = clip.y0 + bb[3] / PXPT
    return (x0, y0, x1, y1), im, clip

if __name__ == '__main__':
    doc = pymupdf.open(BASE + r'\main.pdf')
    # (page, rect, baseline_y, label)
    items = [
        (1, (528.04-3, 602.12-3, 538.09+3, 613.19+3), 610.80, 'p1 ×（判断块1 答案位）'),
        (1, (393.68-3, 638.48-3, 403.73+3, 649.55+3), 647.16, 'p1 ×（判断块1 解析「故×」）'),
        (2, (196.41-3, 523.89-3, 206.46+3, 534.96+3), 532.57, 'p2 √（说明行）'),
        (2, (267.11-3, 544.07-3, 277.16+3, 555.13+3), 552.74, 'p2 ×（判断块2 答案位）'),
        (2, (152.86-3, 580.43-3, 162.91+3, 591.5+3), 589.10, 'p2 ×（判断块2 解析）'),
    ]
    for pno, rect, base, lab in items:
        bb, im, clip = ink_bbox(doc, pno, rect)
        if bb is None:
            print(f'{lab}: 无墨'); continue
        w = (bb[2]-bb[0])/PTMM; h = (bb[3]-bb[1])/PTMM
        top = (base - bb[1])/PTMM; bot = (bb[3] - base)/PTMM
        print(f'{lab}: ink {w:.2f}×{h:.2f}mm  x0={bb[0]:.2f}pt 顶距基线 {top:.2f}mm 底距基线 {bot:.2f}mm 中心距基线 {(top-bot)/2:.2f}mm')
