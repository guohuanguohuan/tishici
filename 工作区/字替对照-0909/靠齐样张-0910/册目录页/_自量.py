# -*- coding: utf-8 -*-
# 自量渲染 png 的行带位置，对表扫描页目标值。一次性校准脚本。
import sys
from PIL import Image
import numpy as np

P = sys.argv[1] if len(sys.argv) > 1 else "png/page1.png"
im = Image.open(P).convert("L")
a = np.array(im)
H, W = a.shape
PXMM = W / 210.0
print(f"{P} {W}x{H} px/mm={PXMM:.3f}")
rc = (a < 120)[:, int(W*0.10):int(W*0.98)].sum(axis=1)
y = 0; prev = None
while y < H:
    if rc[y] > 2:
        s = y
        while y < H and rc[y] > 2:
            y += 1
        xs = np.where((a[s:y, :] < 120).any(axis=0))[0]
        pk = f" pitch={(s-prev)/PXMM:.2f}mm" if prev else ""
        prev = s
        print(f"  y{s:>4}-{y:>4} h={(y-s):>3}px={(y-s)/PXMM:.2f}mm x[{xs.min()}-{xs.max()}] T={s/PXMM:.2f}mm L={xs.min()/PXMM:.2f} R={xs.max()/PXMM:.2f}{pk}")
    else:
        y += 1
