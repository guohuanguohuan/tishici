# -*- coding: utf-8 -*-
# 测量v4：基线聚类法——同底边行上≥2个高度相近(±40%)的簇＝文字串；最小串高＝图内最小文字高
# 单字母标注（单簇高密度）兜底；输出与当前显示宽换算
import os, json
import numpy as np
from PIL import Image
from scipy import ndimage

MED = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-X1衔接1\media检查'
disp = {}
for line in open(r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-X1衔接1\图扫描.tsv', encoding='utf-8-sig'):
    parts = line.rstrip('\n').split('\t')
    if parts[0] in ('序号',): continue
    try: int(parts[0])
    except: continue
    disp[parts[10]] = (parts[1], float(parts[5]), float(parts[6]))

out = {}
files = sorted([f for f in os.listdir(MED) if f.startswith('image') and f.endswith('.png') and '检视' not in f and '拼图' not in f],
               key=lambda x: int(''.join(ch for ch in x if ch.isdigit())))
for fn in files:
    img = Image.open(os.path.join(MED, fn)).convert('RGBA')
    bg = Image.new('RGBA', img.size, (255,255,255,255))
    img = Image.alpha_composite(bg, img).convert('L')
    a = np.array(img)
    H, W = a.shape
    hist, _ = np.histogram(a, bins=256, range=(0,256))
    total = a.size; sum_all = np.dot(np.arange(256), hist); sumB=0.0; wB=0; best_t=128; best_var=-1
    for t in range(256):
        wB += hist[t]
        if wB == 0: continue
        wF = total - wB
        if wF == 0: break
        sumB += t*hist[t]
        mB = sumB/wB; mF = (sum_all-sumB)/wF
        var = wB*wF*(mB-mF)**2
        if var > best_var: best_var=var; best_t=t
    th = min(best_t, 200)
    dark = a < th
    lab, n = ndimage.label(dark)
    objs = ndimage.find_objects(lab)
    cands = []
    for i, sl in enumerate(objs, 1):
        if sl is None: continue
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        area = (lab[sl]==i).sum()
        if 6 <= h <= 130 and 2 <= w <= 130:
            ar = max(h,w)/max(1,min(h,w))
            if ar <= 5.0 and area/(h*w) >= 0.15:
                cands.append({'h':h,'w':w,'y0':sl[0].start,'y1':sl[0].stop,'x0':sl[1].start})
    # 基线聚类：按y1分桶(容差= max(3, h*0.35))
    strs = []
    used = [False]*len(cands)
    for i,c in enumerate(cands):
        if used[i]: continue
        grp = [c]; used[i]=True
        for j,d in enumerate(cands):
            if used[j]: continue
            if abs(d['y1']-c['y1']) <= max(3, min(c['h'],d['h'])*0.35):
                if 0.55 <= d['h']/c['h'] <= 1.8:
                    grp.append(d); used[j]=True
        if len(grp) >= 2:
            hh = sorted(g['h'] for g in grp)
            strs.append({'n':len(grp),'h_med':hh[len(hh)//2],'h_min':hh[0]})
    strs.sort(key=lambda s: s['h_med'])
    est = strs[0]['h_med'] if strs else None
    est_src = 'baseline-cluster' if strs else 'none'
    if est is None:
        # 单字母兜底：高密度近方形簇（如单点O标注），取最小的高度在6..40且宽高比1.2..2.5
        singles = [c for c in cands if 6<=c['h']<=40 and 0.5<=c['w']/c['h']<=1.6 and c['h']*c['w']<=1200]
        singles.sort(key=lambda c:c['h'])
        if singles:
            est = singles[0]['h']; est_src='single-glyph'
    seg, wcm, hcm = disp.get(fn, ('?',0,0))
    pt_per_px = (wcm/W)*28.3465
    cur_pt = round(est*pt_per_px,2) if est else None
    w9 = round(9*W/(est*28.3465),2) if est else None
    out[fn] = {'size':[W,H],'seg':seg,'wcm':wcm,'hcm':hcm,'est':est,'src':est_src,
               'strs_top3':strs[:3],'cur_pt':cur_pt,'w9':w9,'dpi150':round(W/59.06,2)}
print(json.dumps(out, ensure_ascii=False))
