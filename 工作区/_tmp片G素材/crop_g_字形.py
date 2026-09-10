# -*- coding: utf-8 -*-
import cv2, numpy as np
buf = np.fromfile(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image4.png", dtype=np.uint8)
img = cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE)
boxes = {"A":(265,21,41,45),"B":(702,57,39,44),"C":(661,349,42,46),"D":(268,360,47,44),"E":(12,185,42,44),"F":(377,217,42,44)}
pad=4; Z=6
tiles=[]
for k in ["A","B","C","D","E","F"]:
    x,y,w,h = boxes[k]
    crop = img[y-pad:y+h+pad, x-pad:x+w+pad]
    big = cv2.resize(crop, None, fx=Z, fy=Z, interpolation=cv2.INTER_NEAREST)
    big = cv2.cvtColor(big, cv2.COLOR_GRAY2BGR)
    cv2.putText(big, k, (6,26), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
    tiles.append(big)
hh = max(t.shape[0] for t in tiles)
tiles=[cv2.copyMakeBorder(t,0,hh-t.shape[0],0,10,cv2.BORDER_CONSTANT,value=(200,200,200)) for t in tiles]
mont = np.hstack(tiles)
cv2.imwrite("_字形montage.png", mont)
print("montage", mont.shape)
print("\nlabel box vs vertex:")
verts = {"A":(319.68,74.50),"B":(692.00,74.50),"C":(667.32,347.38),"D":(300.40,347.38),"E":(66.80,205.50),"F":(434.40,205.50)}
for k,(x,y,w,h) in boxes.items():
    vx,vy = verts[k]
    print(f" {k}: box x[{x},{x+w}] y[{y},{y+h}] size {w}x{h} | vertex({vx:.1f},{vy:.1f}) | dx_box_center={x+w/2-vx:+.1f} dy_box_center={y+h/2-vy:+.1f}")
