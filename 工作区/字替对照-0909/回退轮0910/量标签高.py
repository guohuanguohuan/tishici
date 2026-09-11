# 量标签高.py —— 回退轮0910 条2：逐图反解显示宽
# 法：PIL 读位图原生像素 → 灰度二值化 → scipy.ndimage 连通域 →
#     筛「字母候选域」（紧凑块状：高∈[0.10,0.42]×图高、宽高比∈[0.18,2.4]、
#     且不与任何长线状域（笔画骨架）粘连）→ 主字母高＝候选域高度上簇（≥0.72×max）中位。
# 输出：每图 (位图宽px, 主字母高px, 反解宽W=px宽×2.65/标签高, 上限=min(84, px宽/59.06×10))
import os
import numpy as np
from PIL import Image
from scipy import ndimage

MEDIA = 'C:/提示词/工作区/字替对照-0909/variantF/media/media/'
FIGS = [('g1-prism', 'image1.png'), ('g2-cubeE', 'image2.png'), ('g3-cube6', 'image3.png'),
        ('g4-dihedral', 'image4.png'), ('g5-fold', 'image5.png'), ('g6-triple', 'sub3_B_4.png')]

for tag, fn in FIGS:
    im = Image.open(MEDIA + fn)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im)
    g = np.asarray(im.convert('L'))
    ink = g < 128
    lab, n = ndimage.label(ink)
    objs = ndimage.find_objects(lab)
    cands = []
    H, W = ink.shape
    for i, sl in enumerate(objs, 1):
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        area = int((lab[sl] == i).sum())
        cands.append((h, w, area, sl[1].start, sl[0].start))
    # 字母候选：块状、中等大小
    letters = [(h, w, a, x, y) for (h, w, a, x, y) in cands
               if 0.10 * H <= h <= 0.42 * H and 0.18 <= w / h <= 2.4 and a / (h * w) > 0.14]
    if not letters:
        print(f'{tag} {fn}: 无候选')
        continue
    hmax = max(h for h, *_ in letters)
    main = sorted(h for h, *_ in letters if h >= 0.72 * hmax)
    med = float(np.median(main))
    Wrev = W * 2.65 / med
    cap = min(84.0, W / 59.06 * 10)
    print(f'{tag} {fn}: 位图 {W}×{H}px｜字母候选 {len(letters)} 个（主簇 {len(main)}）'
          f'｜主字母高中位 {med:.1f}px（簇 {main}）｜反解宽 {Wrev:.2f}mm｜上限 {cap:.2f}mm')
    for h, w, a, x, y in sorted(letters, key=lambda z: -z[0])[:12]:
        print(f'    h={h} w={w} area={a} @({x},{y})')
