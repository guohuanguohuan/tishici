# -*- coding: utf-8 -*-
# v4.4取证轮③片：全品页图长横线(表格线)普查 + 表格行高/格内净空测量
# 口径: 全品 2977x4176px = 210x297mm, 横14.176px/mm 纵14.057px/mm
import numpy as np, glob, os, json
from PIL import Image

BASE = r"C:/提示词/工作区/全品结构提取/数学选必一"
MMX, MMY = 210/2977, 297/4176  # mm per px
THR = 128

def load(page_path):
    im = Image.open(page_path).convert("L")
    return np.asarray(im) < THR  # True=ink

def long_runs(row):
    # 返回该行中长度>=minlen的暗run (start,end)
    out = []
    d = np.diff(np.concatenate(([0], row.astype(int), [0])))
    starts = np.where(d == 1)[0]; ends = np.where(d == -1)[0]
    for s, e in zip(starts, ends):
        if e - s >= 500:
            out.append((s, e))
    return out

def scan_page(path):
    a = load(path)
    h, w = a.shape
    rules = {}  # y -> longest run
    for y in range(h):
        rs = long_runs(a[y])
        if rs:
            s, e = max(rs, key=lambda r: r[1]-r[0])
            if e - s >= 500:
                rules[y] = (s, e)
    return a, rules

def cluster_rules(rules):
    # 聚类相邻y(<=4px)为单线, 返回 [(y_center, x0, x1, thickness)]
    ys = sorted(rules)
    if not ys:
        return []
    lines = []
    cur = [ys[0]]
    for y in ys[1:]:
        if y - cur[-1] <= 4:
            cur.append(y)
        else:
            lines.append(cur); cur = [y]
    lines.append(cur)
    out = []
    for grp in lines:
        xs0 = [rules[y][0] for y in grp]; xs1 = [rules[y][1] for y in grp]
        out.append((int(np.mean(grp)), min(xs0), max(xs1), len(grp)))
    return out

def text_extent(a, y0, y1, x0, x1, exclude_rules=6):
    # 区域内文字墨迹的y范围(排除横线本身附近±exclude_rules)
    sub = a[y0:y1, x0:x1].copy()
    prof = sub.sum(axis=1)
    ys = np.where(prof > 0)[0]
    return (ys.min()+y0, ys.max()+y0) if len(ys) else None

for book in ["导学案页图", "练习册页图"]:
    print("="*20, book)
    for p in sorted(glob.glob(os.path.join(BASE, book, "p*.png"))):
        a, rules = scan_page(p)
        lines = cluster_rules(rules)
        # 表候选: 500px窗口内>=4条线
        tables = []
        used = [False]*len(lines)
        for i, (y, x0, x1, t) in enumerate(lines):
            if used[i]: continue
            grp = [i]
            for j in range(i+1, len(lines)):
                if lines[j][0] - lines[grp[-1]][0] <= 700:
                    grp.append(j)
                else:
                    break
            if len(grp) >= 4:
                for j in grp: used[j] = True
                tables.append([lines[j] for j in grp])
        if tables:
            print(os.path.basename(p), "线%d条" % len(lines))
            for tb in tables:
                print("  表: y%d-%d (高%.2fmm) %d线 x%d-%d (宽%.1fmm)" % (
                    tb[0][0], tb[-1][0], (tb[-1][0]-tb[0][0])*MMY, len(tb),
                    min(l[1] for l in tb), max(l[2] for l in tb),
                    (max(l[2] for l in tb)-min(l[1] for l in tb))*MMX))
                x0 = min(l[1] for l in tb); x1 = max(l[2] for l in tb)
                for k in range(len(tb)-1):
                    ry0, ry1 = tb[k][0], tb[k+1][0]
                    pitch = (ry1-ry0)*MMY
                    tx = text_extent(a, ry0+7, ry1-7, x0+10, x1-10)
                    if tx:
                        top_pad = (tx[0]-ry0)*MMY
                        bot_pad = (ry1-tx[1])*MMY
                        ink_h = (tx[1]-tx[0])*MMY
                    else:
                        top_pad = bot_pad = ink_h = float("nan")
                    print("    行%d: 行高%.2fmm 文高%.2fmm 顶净空%.2f 底净空%.2f" % (k+1, pitch, ink_h, top_pad, bot_pad))
