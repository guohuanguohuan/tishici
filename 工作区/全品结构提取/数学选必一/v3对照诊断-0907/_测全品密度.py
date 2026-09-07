# -*- coding: utf-8 -*-
# v3诊断轮·全品页图像素实测 v2（修正换算 + 定区块测量）
import numpy as np
from PIL import Image

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\导学案页图\\"
V2MM = 297.0/4176   # 纵向 px→mm
X0, X1, Y0, Y1 = 246, 2727, 255, 3860
MID = 1487

def bands(img, x0, x1, y0, y1, thr=170, minrun=3):
    a = np.asarray(img.convert("L"))[y0:y1, x0:x1]
    dark = (a < thr).sum(axis=1)
    rows = dark > 2
    bs = []; s=None
    for i, v in enumerate(rows):
        if v and s is None: s=i
        if not v and s is not None:
            if i-s >= minrun: bs.append((s+y0, i+y0))
            s=None
    if s is not None: bs.append((s+y0, y1))
    return bs

def seg_report(name, pno, y0, y1, x0=None, x1=None):
    im = Image.open(BASE+pno+".png")
    b = bands(im, x0 or X0, x1 or X1, y0, y1)
    if not b: print(f" {name}: 无墨迹"); return
    print(f" {name} [{pno}] y{y0}-{y1}: 高={(y1-y0)*V2MM:.1f}mm 带数={len(b)}")
    gaps = [(b2[0]-b1[1], b1[1]) for b1, b2 in zip(b, b[1:])]
    big = [(g, yy) for g, yy in gaps if g > 18]
    print(f"   带内大空隙(>18px): {[(f'{g*V2MM:.1f}mm', f'y{yy}') for g,yy in big[:10]]}")

print("== A. 版心整体行密度（续页代表 p05/p08）==")
for pno in ["p05", "p08"]:
    im = Image.open(BASE+pno+".png")
    b = bands(im, X0, X1, Y0, Y1)
    text = [x for x in b if x[1]-x[0] > 12]
    tops=[x[0] for x in text]
    pit=[(t2-t1) for t1,t2 in zip(tops,tops[1:]) if 30<t2-t1<170]
    print(f" {pno}: 文本带={len(text)} pitch中位={np.median(pit)*V2MM:.2f}mm(n={len(pit)}) p75={np.percentile(pit,75)*V2MM:.2f}mm")

print("== B. 学习目标块（p08 课时首页：标签顶→花形块顶）==")
seg_report("学习目标块整体", "p08", 380, 800)
print("== C. 诊断分析块 p08（y2450-2830 判断题区）==")
seg_report("诊断分析6题", "p08", 2450, 2900)
print("== D. 例2→变式→素养小结 p09 左栏（y600-2200）==")
seg_report("探究点二全块", "p09", 600, 2300, 250, 1430)
print("== E. 表格行高 p14 三列表（y1560-2100 左栏）==")
seg_report("三列挖空表", "p14", 1560, 2110, 250, 1430)
print("== F. 花形行整行 p08（课前预习 y770-880）==")
seg_report("花形行课前预习", "p08", 770, 900)
print("== G. 课堂评价题间距 p07 右栏（花形行下 y450-2600）==")
seg_report("课堂评价5题", "p07", 470, 2650, 1530, 2730)
