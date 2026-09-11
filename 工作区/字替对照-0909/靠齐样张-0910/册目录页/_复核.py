# -*- coding: utf-8 -*-
# 校准复核：两页墨顶目标对照（含浅色件：CONTENTS/方块组/点划线/点线，thr235）。
from PIL import Image
import numpy as np

BASE = ""
TG = {
 1: [("目录字", 35.48), ("章名1", 63.98), ("PART1", 69.76), ("行1(1.1)", 73.08),
     ("本章总结1", 187.64), ("章名2", 204.29), ("行2.1", 216.84), ("末行(第3课时)", 266.08)],
 2: [("行2.2.3", 26.03), ("本章总结2", 219.39), ("参考答案", 235.54)],
}
for pg in (1, 2):
    im = Image.open(f"png/page{pg}.png").convert("L")
    a = np.array(im)
    H, W = a.shape
    PXMM = W / 210.0
    dark = a < 120
    rc = dark[:, int(W*0.10):int(W*0.98)].sum(axis=1)
    bands = []
    y = 0
    while y < H:
        if rc[y] > 2:
            s = y
            while y < H and rc[y] > 2:
                y += 1
            xs = np.where(dark[s:y, :].any(axis=0))[0]
            bands.append((s/PXMM, (y-s)/PXMM, xs.min()/PXMM, xs.max()/PXMM))
        else:
            y += 1
    print(f"== page{pg} 深色行带 n={len(bands)} ==")
    for i, (name, tgt) in enumerate(TG[pg]):
        if i < len(bands):
            t, h, l, r = bands[i]
            print(f"  {name:<10} 实测T={t:7.2f} 目标={tgt:7.2f} 差={t-tgt:+5.2f}  h={h:.2f} L={l:.2f} R={r:.2f}")
    # 浅色件专项（页1）
    if pg == 1:
        light = a < 235
        # CONTENTS（x<1160px 即 <196mm 区域, y<300px）
        reg = light[80:340, 100:700]
        ys, xs = np.where(reg)
        if len(ys):
            print(f"  CONTENTS   墨T={80/5.91+0:.0f}px?? y {80+ys.min()}-{80+ys.max()} → T={(80+ys.min())/PXMM:.2f} B={(80+ys.max())/PXMM:.2f} L={(100+xs.min())/PXMM:.2f} R={(100+xs.max())/PXMM:.2f} (目标 T27.37 B46.27 L22.57 R114.49)")
        # 方块组（浅色，x 600-800px）
        reg2 = light[120:380, 580:820]
        ys2, xs2 = np.where(reg2 & (a[120:380, 580:820] > 150))
        if len(ys2):
            print(f"  方块组(浅) T={(120+ys2.min())/PXMM:.2f} B={(120+ys2.max())/PXMM:.2f} L={(580+xs2.min())/PXMM:.2f} R={(580+xs2.max())/PXMM:.2f} (目标 浅块T32.45 L118.01 / 深块T26.24 L125.49 R131.77 / 小块T40.56)")
        # 章点划线（y 410-425px, 灰 150-220）
        reg3 = a[400:435, 350:1120]
        m3 = (reg3 > 140) & (reg3 < 230)
        ys3, xs3 = np.where(m3)
        if len(ys3):
            print(f"  章点划线   T={(400+ys3.min())/PXMM:.2f} L={(350+xs3.min())/PXMM:.2f} R={(350+xs3.max())/PXMM:.2f} (目标 y70.40 L57.84 R186.58)")
        # 点线灰值采样（行1 y~440px 中段）
        seg = a[438:446, 600:900]
        m4 = seg < 230
        if m4.sum():
            print(f"  点线灰度min={seg[m4].min()} (目标~204)  点带y {(438+np.where(m4.any(axis=1))[0].min())/PXMM:.2f}-{(438+np.where(m4.any(axis=1))[0].max())/PXMM:.2f} (目标74.28-74.71)")
