# -*- coding: utf-8 -*-
# 图内最小文字像素高测量：二值化→连通域→文字簇候选（排除细线/大块）→按基线聚类分组
# 输出每图候选文字簇统计：最小簇高、10百分位高度、簇组样本
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage

MED = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-X1衔接1\media检查'
out = {}
files = sorted([f for f in os.listdir(MED) if f.startswith('image') and f.endswith('.png')],
               key=lambda x: int(''.join(ch for ch in x if ch.isdigit())))

for fn in files:
    img = Image.open(os.path.join(MED, fn)).convert('L')
    a = np.array(img)
    H, W = a.shape
    # 二值化：墨迹=暗
    dark = a < 160
    frac_dark = dark.mean()
    if frac_dark < 0.001:
        out[fn] = {'size': [W, H], 'blank': True}
        continue
    lab, n = ndimage.label(dark)
    objs = ndimage.find_objects(lab)
    cands = []
    for i, sl in enumerate(objs, 1):
        if sl is None: continue
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        area = (lab[sl] == i).sum()
        # 文字候选：尺寸小、非细线（纵横比适中）、密度适中
        if 3 <= h <= 60 and 2 <= w <= 60:
            ar = max(h, w) / max(1, min(h, w))
            dens = area / (h * w)
            if ar <= 4.5 and dens >= 0.18:
                cands.append((h, w, sl[0].start, sl[1].start, area))
    # 小文字候选高度分布（前若干最小）
    hs = sorted(c[0] for c in cands)
    # 按高度取聚集众数区间（小端）：找高度h使簇数≥3的h群
    small = [h for h in hs if h <= 30]
    stat = {
        'size': [W, H],
        'cand_n': len(cands),
        'min_h': hs[0] if hs else None,
        'p10': hs[max(0, len(hs)//10)] if hs else None,
        'p25': hs[len(hs)//4] if hs else None,
        'small_3plus': None,
    }
    # 高度值中计数≥3的最小值（防单点噪声）
    from collections import Counter
    if small:
        cnt = Counter(small)
        for h in sorted(cnt):
            if cnt[h] >= 3:
                stat['small_3plus'] = h; break
    out[fn] = stat

print(json.dumps(out, ensure_ascii=False))
