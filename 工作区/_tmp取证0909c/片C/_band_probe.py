# -*- coding: utf-8 -*-
"""片C·括号带探针：渲染答案行条带，按列投影找墨块（区分括号/×/√）。"""
import pymupdf
from PIL import Image
import numpy as np

BASE = r'C:\提示词\工作区\字替对照-0909\variantF'
DPI = 600; PXPT = DPI/72.0; PTMM = 72/25.4
doc = pymupdf.open(BASE + r'\main.pdf')

def strip(pno, rect, label):
    page = doc[pno-1]
    clip = pymupdf.Rect(rect)
    pix = page.get_pixmap(dpi=DPI, clip=clip)
    im = Image.frombytes('RGB',(pix.width,pix.height),pix.samples).convert('L')
    a = np.array(im) < 128
    cols = a.any(axis=0)
    # 墨块分段
    segs=[]; s=None
    for i,v in enumerate(cols):
        if v and s is None: s=i
        if not v and s is not None: segs.append((s,i)); s=None
    if s is not None: segs.append((s,len(cols)))
    print(f'--- {label} rect={[round(v,1) for v in rect]}')
    for (x0,x1) in segs:
        sub = a[:, x0:x1]
        rows = sub.any(axis=1)
        r0 = int(np.argmax(rows)); r1 = len(rows)-int(np.argmax(rows[::-1]))
        px0 = clip.x0 + x0/PXPT; px1 = clip.x0 + x1/PXPT
        py0 = clip.y0 + r0/PXPT; py1 = clip.y0 + r1/PXPT
        print(f'  墨块 x[{px0:7.2f},{px1:7.2f}]pt 宽{(px1-px0)/PTMM:5.2f}mm  y[{py0:7.2f},{py1:7.2f}]pt 高{(py1-py0)/PTMM:5.2f}mm')

# p1 判断块1 (1) 答案行：× 在 x=528.04 基线 610.80；行文本 y≈602-613
strip(1, (500, 600, 560, 616), 'p1 (1)答案行 含括号带')
# p1 判断块1 (2) 答案行：× 在 393.68 基线 647.16
strip(1, (370, 636, 420, 652), 'p1 (2)答案行')
# p1 判断块1 (2) 解析「故×」行：√ 在 453.15(FZSSJW) 基线 701.71
strip(1, (440, 690, 480, 706), 'p1 (2)解析行 故×')
# p2 说明行 √ 在 196.41 基线 532.57
strip(2, (180, 521, 230, 537), 'p2 说明行 打√打×')
# p3 答案行 √ 267.11 基线 313.26 (FZSSJW 当前)
strip(3, (250, 302, 290, 318), 'p3 (1)答案行 √')
