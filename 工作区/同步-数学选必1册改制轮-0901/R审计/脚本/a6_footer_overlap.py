# -*- coding: utf-8 -*-
import fitz, sys, os
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
PDF = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\PDF'
def gray(page, rect, m=4):
    pix = page.get_pixmap(matrix=fitz.Matrix(m,m), clip=rect, colorspace=fitz.csGRAY)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
def cols(pdf, pa, pb, y0, y1, x0, x1, n=14, label=''):
    doc = fitz.open(os.path.join(PDF, pdf))
    rect = fitz.Rect(x0, y0, x1, y1)
    A = gray(doc[pa-1], rect) < 128; B = gray(doc[pb-1], rect) < 128
    print('%s p%d vs p%d（页脚带）:' % (label, pa, pb))
    W = A.shape[1]; step = W // n
    lost = 0; tot = 0
    for i in range(n):
        s = A[:, i*step:(i+1)*step]; t = B[:, i*step:(i+1)*step]
        d = int((t & ~s).sum()); lost += d; tot += int(t.sum())
        print('  x%.0f-%.0f | 有图页暗px=%5d | 无图页暗px=%5d | 字形被覆盖px=%5d' % (
            x0+i*(x1-x0)/n, x0+(i+1)*(x1-x0)/n, s.sum(), t.sum(), d))
    print('  >> 字形丢失合计=%d / 无图页字形合计=%d（%.0f%%）' % (lost, tot, 100*lost/max(tot,1)))
    doc.close()
cols('X1.pdf', 3, 2, 786, 801, 42.5, 350, label='X1 p3(有图)')
cols('I1.pdf', 4, 5, 784, 801, 268, 495, label='I1 p4(有图)')
