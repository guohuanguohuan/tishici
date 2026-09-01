# -*- coding: utf-8 -*-
"""R1审计——页脚被图覆盖实压判定：redaction去图前后页脚带字形像素差（实压=去图后多出的字形像素）。"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
import fitz
import numpy as np

PDF = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\PDF'
CAND = [('X1',[3,5,8,11,12]), ('B',[21,22,47,65,67]), ('E',[2,17,23,26,31,50]),
        ('C',[1]), ('I1',[4])]
FOOT = fitz.Rect(40, 782, 540, 804)

def strip_dark(page, m=4):
    pix = page.get_pixmap(matrix=fitz.Matrix(m,m), clip=FOOT, colorspace=fitz.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    return a < 128

for code, pages in CAND:
    for pn in pages:
        doc = fitz.open(os.path.join(PDF, code + '.pdf'))
        page = doc[pn-1]
        before = strip_dark(page)
        page.add_redact_annot(FOOT)
        try:
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE,
                                  graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                                  text=fitz.PDF_REDACT_TEXT_NONE)
        except Exception as e:
            # 旧版PyMuPDF无text参数——回退（文本仍会被移除则改用图形遮挡法）
            print('%s p%d redaction API受限: %s' % (code, pn, e)); doc.close(); continue
        after = strip_dark(page)
        recovered = int((after & ~before).sum())
        vanish = int((before & ~after).sum())
        print('%s p%-3d 页脚带: 原暗px=%5d 去图后暗px=%5d | 去图后显影像素=%5d（实压字形指标）| 消失像素=%5d' % (
            code, pn, int(before.sum()), int(after.sum()), recovered, vanish))
        doc.close()
print('DONE')
