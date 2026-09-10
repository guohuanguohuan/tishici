# -*- coding: utf-8 -*-
import cv2, numpy as np, itertools, math
bw = np.load("_bw.npy")
# keep only the big line component
n, lab, stats, cent = cv2.connectedComponentsWithStats(bw, connectivity=8)
big = 1 + int(np.argmax([stats[i][4] for i in range(1, n)]))
lines_img = ((lab == big).astype(np.uint8)) * 255

ls = cv2.HoughLinesP(lines_img, 1, np.pi/720, threshold=60, minLineLength=90, maxLineGap=4)
segs = [tuple(int(v) for v in l[0]) for l in ls]
print("raw segs:", len(segs))

def ang(s):
    return math.degrees(math.atan2(s[3]-s[1], s[2]-s[0])) % 180
# cluster by (angle, offset) signature
clusters = []
for s in segs:
    a = ang(s); L = math.hypot(s[2]-s[0], s[3]-s[1])
    placed = False
    for c in clusters:
        da = min(abs(a-c["a"]), 180-abs(a-c["a"]))
        if da < 1.2:
            # distance from s midpoint to cluster line
            x0,y0,x1,y1 = c["rep"]; th = math.radians(c["a"])
            mx,my = (s[0]+s[2])/2,(s[1]+s[3])/2
            d = abs(-math.sin(th)*(mx-x0)+math.cos(th)*(my-y0))
            if d < 3.5:
                c["segs"].append((s,L)); c["a"]=np.mean([c["a"],a]); placed=True; break
    if not placed:
        clusters.append(dict(a=a, rep=s, segs=[(s,L)]))
clusters.sort(key=lambda c: -sum(L for _,L in c["segs"]))
print(f"\n{len(clusters)} clusters")
for i,c in enumerate(clusters):
    N=sum(L for _,L in c["segs"])
    print(f"C{i}: ang={c['a']:7.2f} len={N:7.0f} nseg={len(c['segs'])}")
    for s,L in sorted(c["segs"], key=lambda t:-t[1])[:3]:
        print(f"      ({s[0]:4d},{s[1]:4d})-({s[2]:4d},{s[3]:4d}) L={L:6.1f}")
np.save("_linesmask.npy", lines_img)
