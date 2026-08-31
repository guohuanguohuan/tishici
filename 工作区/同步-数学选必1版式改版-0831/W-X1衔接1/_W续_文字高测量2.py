# -*- coding: utf-8 -*-
# 测量v2：自适应二值化（Otsu）＋放宽高度上限，输出每图簇高分布＋按当前显示宽的视觉pt换算
import os, json
import numpy as np
from PIL import Image
from scipy import ndimage
from collections import Counter

MED = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-X1衔接1\media检查'
# 当前显示宽cm（图扫描.tsv）＋段序号
disp = {}
for line in open(r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-X1衔接1\图扫描.tsv', encoding='utf-8-sig'):
    parts = line.rstrip('\n').split('\t')
    if parts[0] in ('序号',): continue
    try: int(parts[0])
    except: continue
    disp[parts[10]] = (parts[1], float(parts[5]), float(parts[6]))  # 段序号,宽cm,高cm

out = {}
files = sorted([f for f in os.listdir(MED) if f.startswith('image') and f.endswith('.png') and '检视' not in f and '拼图' not in f],
               key=lambda x: int(''.join(ch for ch in x if ch.isdigit())))
for fn in files:
    img = Image.open(os.path.join(MED, fn)).convert('RGBA')
    # 白底alpha合成（透明底图防误判黑底）
    bg = Image.new('RGBA', img.size, (255,255,255,255))
    img = Image.alpha_composite(bg, img).convert('L')
    a = np.array(img)
    H, W = a.shape
    # Otsu自适应阈值
    hist, _ = np.histogram(a, bins=256, range=(0,256))
    total = a.size
    sum_all = np.dot(np.arange(256), hist)
    sumB = 0.0; wB = 0; best_t = 128; best_var = -1
    for t in range(256):
        wB += hist[t]
        if wB == 0: continue
        wF = total - wB
        if wF == 0: break
        sumB += t * hist[t]
        mB = sumB / wB; mF = (sum_all - sumB) / wF
        var = wB * wF * (mB - mF) ** 2
        if var > best_var: best_var = var; best_t = t
    th = min(best_t, 200)
    dark = a < th
    if dark.mean() > 0.5:  # 反色（白字黑底）
        dark = ~dark
    lab, n = ndimage.label(dark)
    objs = ndimage.find_objects(lab)
    cands = []
    for i, sl in enumerate(objs, 1):
        if sl is None: continue
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        area = (lab[sl] == i).sum()
        if 3 <= h <= 130 and 2 <= w <= 130:
            ar = max(h, w) / max(1, min(h, w))
            dens = area / (h * w)
            if ar <= 5.0 and dens >= 0.15:
                cands.append((h, w, sl[0].start, sl[1].start))
    hs = sorted(c[0] for c in cands)
    # 文字高估计：取高度直方图中≤40px部分的最小聚集高度（计数≥3）
    est = None
    cnt = Counter(h for h in hs if h <= 45)
    for h in sorted(cnt):
        if cnt[h] >= 3: est = h; break
    if est is None and hs: est = hs[0]
    seg, wcm, hcm = disp.get(fn, ('?', 0, 0))
    pt_per_px = (wcm / W) * 28.3465 if W else 0
    cur_pt = round(est * pt_per_px, 2) if est else None
    # 9pt目标宽 = 9 / (est*28.3465/W) = 9*W/(est*28.3465)
    w_target = round(9 * W / (est * 28.3465), 2) if est else None
    out[fn] = {'size': [W, H], 'seg': seg, 'wcm': wcm, 'hcm': hcm, 'cand_n': len(cands),
               'min_txt_px_est': est, 'cur_min_pt': cur_pt, 'w_target_9pt': w_target,
               'dpi150_w': round(W / 59.06, 2)}

print(json.dumps(out, ensure_ascii=False))
