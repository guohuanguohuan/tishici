# -*- coding: utf-8 -*-
# ③片: 全品导学案19页 题图候选检测 (连通域, 排除花形/表格/章首/页眉脚)
import numpy as np, glob, os, json
from PIL import Image
from scipy import ndimage

B = r"C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/"
MMX, MMY = 210/2977, 297/4176
THR = 128

def hruns(row, minlen):
    d = np.diff(np.concatenate(([0], row.astype(int), [0])))
    st = np.where(d==1)[0]; en = np.where(d==-1)[0]
    return [(s,e) for s,e in zip(st,en) if e-s>=minlen]

results = {}
for p in sorted(glob.glob(B+"p*.png")):
    name = os.path.basename(p)
    a = np.asarray(Image.open(p).convert("L")) < THR
    # 形态闭: 连接线稿
    dil = ndimage.binary_dilation(a, structure=np.ones((7,7)))
    lab, n = ndimage.label(dil)
    cands = []
    for sl in ndimage.find_objects(lab):
        y0, y1 = sl[0].start, sl[0].stop
        x0, x1 = sl[1].start, sl[1].stop
        w, h = x1-x0, y1-y0
        if w < 150 or h < 100: continue
        if y1 < 320 or y0 > 3860: continue  # 页眉/页脚
        # 花形块: 左缘≈版心左+0~10 且 320<w<360, 80<h<110
        if 300 < w < 380 and 75 < h < 115 and (x0 < 600 or x0 > 1500) and x0 < 1560:
            pass
        # 表格区排除: 框内含>=3条长横线
        sub = a[y0:y1, x0:x1]
        nrule = 0
        for y in range(0, h, 2):
            if hruns(sub[y], int(w*0.8)): nrule += 1
        if nrule >= 4: continue
        # 花形底线/通栏线排除: 高度<12px 的纯线条
        if h < 14: continue
        # 章首装饰方块/二维码 (p04 顶部 y<560)
        if y1 < 560: continue
        cands.append((x0, y0, x1, y1, w, h))
    results[name] = cands
    print(name, len(cands))
    for x0, y0, x1, y1, w, h in cands:
        print("   x%d-%d y%d-%d  %.1fx%.1fmm" % (x0, x1, y0, y1, w*MMX, h*MMY))

json.dump({k: [list(c) for c in v] for k, v in results.items()},
          open(r"C:/提示词/工作区/全品结构提取/数学选必一/_tmp扫差0908b/_③图候选.json", "w"))
