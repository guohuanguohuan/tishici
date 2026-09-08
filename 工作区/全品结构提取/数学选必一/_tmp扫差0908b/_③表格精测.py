# -*- coding: utf-8 -*-
# ③片: 表格行高/格内净空 精测v2 (修复y偏移; 表线x跨度过滤挖空线; 单行格净空分布)
import numpy as np, glob, os
from PIL import Image

BASE = r"C:/提示词/工作区/全品结构提取/数学选必一"
MMX, MMY = 210/2977, 297/4176
THR = 128

def load(p):
    return np.asarray(Image.open(p).convert("L")) < THR

def hruns(row, minlen):
    d = np.diff(np.concatenate(([0], row.astype(int), [0])))
    st = np.where(d == 1)[0]; en = np.where(d == -1)[0]
    return [(s, e) for s, e in zip(st, en) if e-s >= minlen]

def find_tables(a, x0, x1):
    Y0, Y1 = 260, 3860
    sub = a[Y0:Y1, x0:x1]
    ys = {}
    for y in range(sub.shape[0]):
        rs = hruns(sub[y], 500)
        if rs:
            s, e = max(rs, key=lambda r: r[1]-r[0])
            ys[y] = (s+x0, e+x0)
    if not ys: return []
    lines, cur = [], []
    for y in sorted(ys):
        if cur and y-cur[-1] > 4:
            lines.append(cur); cur = []
        cur.append(y)
    lines.append(cur)
    lines = [(int(np.mean(g))+Y0, min(ys[y][0] for y in g), max(ys[y][1] for y in g)) for g in lines]
    tabs, used = [], [False]*len(lines)
    for i in range(len(lines)):
        if used[i]: continue
        grp = [i]
        for j in range(i+1, len(lines)):
            if lines[j][0]-lines[grp[-1]][0] <= 700: grp.append(j)
            else: break
        if len(grp) >= 4:
            for j in grp: used[j] = True
            tabs.append([lines[j] for j in grp])
    return tabs

def vcols(a, y0, y1, x0, x1):
    sub = a[y0:y1, x0:x1]
    frac = sub.mean(axis=0)
    cols = np.where(frac >= 0.7)[0]
    out = []
    if len(cols):
        st = cols[0]; prev = cols[0]
        for c in cols[1:]:
            if c-prev > 6:
                out.append((st+x0, prev+x0)); st = c
            prev = c
        out.append((st+x0, prev+x0))
    return out

def text_bands(a, y0, y1, x0, x1, vlines):
    mask = np.ones(x1-x0, bool)
    for vx0, vx1 in vlines:
        lo = max(vx0-x0-7, 0); hi = min(vx1-x0+8, x1-x0)
        if hi > lo: mask[lo:hi] = False
    sub = a[y0:y1, x0:x1][:, mask]
    prof = sub.sum(axis=1)
    bands, inb = [], False
    for i, v in enumerate(prof):
        if v > 0 and not inb: st = i; inb = True
        elif v == 0 and inb:
            bands.append((st+y0, i+y0)); inb = False
    if inb: bands.append((st+y0, y1))
    return bands

# ============ 全品侧 ============
print("="*10, "全品")
cells_single = []  # (page,row,cell文本带高,顶净空,底净空)
for book, cols in [("导学案页图", [(246, 1440), (1540, 2730)]), ("练习册页图", [(179, 1370), (1610, 2660)])]:
    for p in sorted(glob.glob(os.path.join(BASE, book, "p*.png"))):
        a = load(p)
        for ci, (x0, x1) in enumerate(cols):
            for t in find_tables(a, x0, x1):
                tx0, tx1 = min(l[1] for l in t), max(l[2] for l in t)
                w = tx1-tx0
                # 真表线: x跨度>=0.85表宽
                t = [l for l in t if l[2]-l[1] >= 0.85*w]
                if len(t) < 3: continue
                print("表 %s %s栏 y%d-%d (%d线) x%d-%d 宽%.1fmm" % (os.path.basename(p), "左" if ci==0 else "右", t[0][0], t[-1][0], len(t), tx0, tx1, w*MMX))
                vl_all = vcols(a, t[0][0]+8, t[-1][0]-8, tx0, tx1)
                print("  列分界: %s" % ["%d(%.1fmm)" % (v0, (v1-v0)*MMX) for v0, v1 in vl_all])
                for k in range(len(t)-1):
                    pitch = (t[k+1][0]-t[k][0])*MMY
                    bands = text_bands(a, t[k][0]+6, t[k+1][0]-6, tx0, tx1, vl_all)
                    bs = "; ".join("高%.2f 顶距%.2f 底距%.2f" % ((b1-b0)*MMY, (b0-t[k][0])*MMY, (t[k+1][0]-b1)*MMY) for b0, b1 in bands)
                    print("  行%d 行高%.2fmm 墨带[%s]" % (k+1, pitch, bs))
                    if len(bands) == 1:
                        b0, b1 = bands[0]
                        if (b1-b0)*MMY <= 5.5:
                            cells_single.append((os.path.basename(p), k+1, (b1-b0)*MMY, (b0-t[k][0])*MMY, (t[k+1][0]-b1)*MMY))
                print()

print("="*10, "单行格净空样本(行内唯一墨带<=5.5mm)")
import statistics
tops = [c[3] for c in cells_single]; bots = [c[4] for c in cells_single]; hs = [c[2] for c in cells_single]
print("n=%d 墨带高中位%.2fmm 顶净空中位%.2f(区间%.2f-%.2f) 底净空中位%.2f(区间%.2f-%.2f) 顶+底合计中位%.2fmm" % (
    len(cells_single), statistics.median(hs), statistics.median(tops), min(tops), max(tops),
    statistics.median(bots), min(bots), max(bots), statistics.median([t+b for t, b in zip(tops, bots)])))
