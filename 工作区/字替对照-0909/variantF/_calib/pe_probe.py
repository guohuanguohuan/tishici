# P-E 探针 v2：竖线优先定位表格 → 横线 → 逐格净空
import os
import pymupdf
import numpy as np
from PIL import Image

BASE = r'C:\提示词\工作区\字替对照-0909\variantF'
CAL = os.path.join(BASE, '_calib')
PXMM = 360 / 25.4

doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
for i in range(3):
    pix = doc[i].get_pixmap(dpi=360)
    pix.save(os.path.join(CAL, f'_F_p{i+1}.png'))
print('rendered 360dpi pages 1-3')

def cluster(idx, gap=3):
    out, cur = [], [idx[0]]
    for v in idx[1:]:
        if v - cur[-1] <= gap:
            cur.append(v)
        else:
            out.append(int(np.mean(cur))); cur = [v]
    out.append(int(np.mean(cur)))
    return out

def max_run(v):
    d = np.diff(np.concatenate(([0], v.astype(np.int8), [0])))
    s = np.where(d == 1)[0]; e = np.where(d == -1)[0]
    return 0 if len(s) == 0 else int((e - s).max())

def measure(path):
    a = np.asarray(Image.open(path).convert('L'))
    H, W = a.shape
    dark = a < 160
    run = np.array([max_run(dark[:, x]) for x in range(W)])
    vx = np.where((run > 15*PXMM) & (run < 80*PXMM))[0]
    if len(vx) < 2:
        print(f'{os.path.basename(path)}: 无表竖线')
        return
    vb = cluster(vx)
    # 相邻竖线对 → 表区（列距 8~45mm）
    tables = []
    used = set()
    for i in range(len(vb) - 1):
        if i in used:
            continue
        grp = [vb[i]]
        j = i
        while j + 1 < len(vb) and vb[j + 1] - vb[j] < 45 * PXMM:
            j += 1; grp.append(vb[j]); used.add(j)
        used.add(i)
        if len(grp) >= 3:
            tables.append(grp)
    for ti, grp in enumerate(tables):
        x0, x1 = grp[0], grp[-1]
        cov = dark[:, x0+4:x1-4].sum(axis=1) / (x1 - x0 - 8)
        hy = np.where(cov > 0.9)[0]
        if len(hy) < 3:
            continue
        hb = cluster(hy)
        # 只留连续表体（行高 < 60mm 的段）
        segs, cur = [], [hb[0]]
        for y in hb[1:]:
            if y - cur[-1] < 60 * PXMM:
                cur.append(y)
            else:
                segs.append(cur); cur = [y]
        segs.append(cur)
        seg = max(segs, key=len)
        if len(seg) < 3:
            continue
        print(f'== {os.path.basename(path)} 表{ti+1}: x=[{x0},{x1}] 行高(mm)=' +
              str([round((seg[k+1]-seg[k])/PXMM, 2) for k in range(len(seg)-1)]))
        for ri in range(len(seg) - 1):
            yy0, yy1 = seg[ri] + 4, seg[ri + 1] - 4
            if yy1 - yy0 < 8:
                continue
            cells = []
            for ci in range(len(grp) - 1):
                xx0, xx1 = grp[ci] + 4, grp[ci + 1] - 4
                cell = dark[yy0:yy1, xx0:xx1]
                if cell.sum() < 20:
                    cells.append('(空)'); continue
                ys, xs = np.where(cell)
                padL, padR = xs.min()/PXMM, (xx1-xx0-xs.max())/PXMM
                padT, padB = ys.min()/PXMM, (yy1-yy0-ys.max())/PXMM
                tag = 'C' if abs(padL-padR) < 1.0 else ('L' if padL < padR else 'R')
                ink = cell.any(axis=1); yy = np.where(ink)[0]
                nb, p = 1, yy[0]
                for v in yy[1:]:
                    if v - p > 8: nb += 1
                    p = v
                cells.append(f'L{padL:.2f}/R{padR:.2f}/T{padT:.2f}/B{padB:.2f}({tag},{nb}行)')
            print(f'  r{ri}: ' + ' | '.join(cells))

for n in (1, 2, 3):
    measure(os.path.join(CAL, f'_F_p{n}.png'))
