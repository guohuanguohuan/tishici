# -*- coding: utf-8 -*-
import cv2, numpy as np, json

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image4.png"
buf = np.fromfile(SRC, dtype=np.uint8)
img = cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE)
print("shape", img.shape)
bw = (img < 128).astype(np.uint8)
print("ink px", int(bw.sum()))
n, lab, stats, cent = cv2.connectedComponentsWithStats(bw, connectivity=8)
comps = []
for i in range(1, n):
    x, y, w, h, area = stats[i]
    comps.append(dict(id=i, x=int(x), y=int(y), w=int(w), h=int(h), area=int(area),
                      cx=round(float(cent[i][0]),1), cy=round(float(cent[i][1]),1)))
comps.sort(key=lambda c: -c["area"])
for c in comps:
    print(f"id={c['id']:3d} box=({c['x']:4d},{c['y']:4d},w{c['w']:3d},h{c['h']:3d}) area={c['area']:6d} c=({c['cx']},{c['cy']})")
np.save("_bw.npy", bw)
