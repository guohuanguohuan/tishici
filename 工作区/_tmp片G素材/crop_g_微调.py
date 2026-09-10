# -*- coding: utf-8 -*-
"""逐字母亚像素微调搜索（在 2x 帧上以 1px 步进＝0.5px@1x）"""
import fitz, numpy as np, cv2
SRC = cv2.imdecode(np.fromfile("source-image4.png",dtype=np.uint8),cv2.IMREAD_GRAYSCALE)
d=fitz.open("片G-image4-二面角-standalone.pdf"); p=d[0]; z=1576/p.rect.width
pix=p.get_pixmap(matrix=fitz.Matrix(z,z), colorspace=fitz.csGRAY)
mine=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
src2=cv2.resize(SRC,(1576,848),interpolation=cv2.INTER_NEAREST)
ms = src2<128
base = np.load("_align.npy")*2.0
REG = {"线网":(40,55,720,370),"A":(255,11,326,76),"B":(692,47,751,111),"C":(651,339,713,410),
       "D":(258,350,325,414),"E":(2,175,64,239),"F":(367,207,429,271)}
print("区块   基准dx,dy   最优dx,dy(2x)     最优IoU  基准IoU   修正量@1x(mm)")
for k,(x0,y0,x1,y1) in REG.items():
    a=ms[y0*2:y1*2, x0*2:x1*2]
    best=None
    for ddx in np.arange(-4,4.5,1.0):
        for ddy in np.arange(-4,4.5,1.0):
            M=np.float32([[1,0,base[0]+ddx],[0,1,base[1]+ddy]])
            mm_=cv2.warpAffine(mine,M,(1576,848),flags=cv2.INTER_LINEAR,borderValue=255)<128
            b=mm_[y0*2:y1*2, x0*2:x1*2]
            iou=(a&b).sum()/max(1,(a|b).sum())
            if best is None or iou>best[0]: best=(iou,base[0]+ddx,base[1]+ddy)
    # 基准 IoU
    M=np.float32([[1,0,base[0]],[0,1,base[1]]])
    mmb=cv2.warpAffine(mine,M,(1576,848),flags=cv2.INTER_LINEAR,borderValue=255)<128
    iou0=(a&mmb[y0*2:y1*2,x0*2:x1*2]).sum()/max(1,(a|mmb[y0*2:y1*2,x0*2:x1*2]).sum())
    ddx, ddy = best[1]-base[0], best[2]-base[1]
    print("  %-4s (%.2f,%.2f)  (%+.0f,%+.0f)@2x  %.4f   %.4f   Δx=%+.2fmm Δy=%+.2fmm" % (
        k, base[0],base[1], ddx,ddy, best[0], iou0, -ddx*0.0841371/2, ddy*0.0841371/2))
