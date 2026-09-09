# P-E: 全品 p04 表1 裁片测量 —— 格内对齐形态＋净空
# 输入 _calib/_p04_table.png（360dpi, 14.1732 px/mm）；纯读
import pymupdf  # noqa: F401  (环境自检占位，不用)
from PIL import Image
import numpy as np

PXMM = 360 / 25.4
img = Image.open(r'C:\提示词\工作区\字替对照-0909\variantF\_calib\_p04_table.png').convert('L')
a = np.asarray(img)
H, W = a.shape
dark = a < 128

# --- 横线：暗像素占比 > 0.7 的行 ---
rows = np.where(dark.sum(axis=1) > 0.7 * W)[0]
# 聚类相邻行
def cluster(idx):
    out = []
    cur = [idx[0]]
    for v in idx[1:]:
        if v - cur[-1] <= 3:
            cur.append(v)
        else:
            out.append(cur); cur = [v]
    out.append(cur)
    return out
hb = [int(np.mean(c)) for c in cluster(rows)]
cols_idx = np.where(dark.sum(axis=0) > 0.7 * H)[0]
vb = [int(np.mean(c)) for c in cluster(cols_idx)]
print(f'img {W}x{H}  hlines y={hb}  vlines x={vb}')
print(f'  hline 间距(mm): {[round((hb[i+1]-hb[i])/PXMM,2) for i in range(len(hb)-1)]}')
print(f'  vline 间距(mm): {[round((vb[i+1]-vb[i])/PXMM,2) for i in range(len(vb)-1)]}')

def line_bands(mask_slice):
    """行内文字行带: 返回 [(y0,y1)]"""
    ink = mask_slice.any(axis=1)
    ys = np.where(ink)[0]
    if len(ys) == 0:
        return []
    bands = []
    s = ys[0]; p = ys[0]
    for y in ys[1:]:
        if y - p > 4:
            bands.append((s, p)); s = y
        p = y
    bands.append((s, p))
    return bands

for ri in range(len(hb) - 1):
    y0, y1 = hb[ri] + 4, hb[ri + 1] - 4   # 内缩避开框线
    if y1 - y0 < 8:
        continue
    for ci in range(len(vb) - 1):
        x0, x1 = vb[ci] + 4, vb[ci + 1] - 4
        cell = dark[y0:y1, x0:x1]
        if cell.sum() < 20:
            print(f'r{ri}c{ci}: (空)')
            continue
        ys, xs = np.where(cell)
        bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
        padL = bx0 / PXMM; padR = (x1 - x0 - bx1) / PXMM
        padT = by0 / PXMM; padB = (y1 - y0 - by1) / PXMM
        bands = line_bands(cell)
        info = []
        for (ly0, ly1) in bands:
            lx = np.where(cell[ly0:ly1 + 1].any(axis=0))[0]
            info.append(f'[L{lx.min()/PXMM:.2f} R{(x1-x0-lx.max())/PXMM:.2f}mm]')
        tag = 'CEN?' if abs(padL - padR) < 1.0 else ('L' if padL < padR else 'R')
        print(f'r{ri}c{ci}: 整块 padL={padL:.2f} padR={padR:.2f} padT={padT:.2f} padB={padB:.2f}mm ({tag}) '
              f'行带{len(bands)}: {" ".join(info)}')
