# -*- coding: utf-8 -*-
"""定位全品 p04 说明行 ×/√：连通域扫描（14.176px/mm）。"""
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = r'C:\提示词\工作区\全品结构提取\数学选必一\导学案页图\p04.png'
HX = 2977/210  # px per mm
im = Image.open(SRC).convert('L')
a = np.array(im) < 128
print('page px', im.size, 'px/mm', round(HX,3))
lab, n = ndimage.label(a)
objs = ndimage.find_objects(lab)
cands = []
for i, sl in enumerate(objs):
    if sl is None: continue
    h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
    wmm, hmm = w/HX, h/HX
    if 1.9 < wmm < 2.8 and 1.9 < hmm < 2.8:
        # 判断是否 X 形：四角有墨、中心有墨、上下中无墨
        sub = (lab[sl] == i+1)
        hh, ww = sub.shape
        def frac(r0,r1,c0,c1):
            return sub[int(r0*hh):int(r1*hh), int(c0*ww):int(c1*ww)].mean()
        if frac(0.1,0.4,0.1,0.4)>0.5 and frac(0.1,0.4,0.6,0.9)>0.5 and frac(0.6,0.9,0.1,0.4)>0.5 and frac(0.6,0.9,0.6,0.9)>0.5 and frac(0.4,0.6,0.4,0.6)>0.3:
            cands.append((sl[1].start, sl[0].start, w, h, wmm, hmm))
print(f'× 候选 {len(cands)}:')
for c in cands:
    print(f'  x={c[0]} y={c[1]} {c[2]}x{c[3]}px = {c[4]:.2f}x{c[5]:.2f}mm')
