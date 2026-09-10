# -*- coding: utf-8 -*-
"""对齐后逐字母/线网残差（1x 帧）"""
import fitz, numpy as np, cv2, math
SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image4.png"
PDF = "片G-image4-二面角-standalone.pdf"
A = 255-cv2.imdecode(np.fromfile(SRC,dtype=np.uint8),cv2.IMREAD_GRAYSCALE).astype(np.float32)
d=fitz.open(PDF); p=d[0]; z=788/p.rect.width
pix=p.get_pixmap(matrix=fitz.Matrix(z,z), colorspace=fitz.csGRAY)
B0 = 255-np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width).astype(np.float32)
UP=4
Bu = cv2.resize(B0,None,fx=UP,fy=UP,interpolation=cv2.INTER_LINEAR)
dx,dy = np.load("_align.npy")           # 0.25, 0.25 px
Bu = np.roll(np.roll(Bu, int(round(dy*UP)), axis=0), int(round(dx*UP)), axis=1)
B = cv2.resize(Bu, (788,424), interpolation=cv2.INTER_AREA)   # 回到 1x 帧，含亚像素位移
def comps(g):
    m=(255-g<128).astype(np.uint8)
    n,lab,st,ce=cv2.connectedComponentsWithStats(m,connectivity=8)
    out=[]
    for i in range(1,n):
        x,y,w,h,a=st[i]
        if a<200: continue
        out.append(dict(x=int(x),y=int(y),w=int(w),h=int(h),a=int(a),cx=float(ce[i][0]),cy=float(ce[i][1])))
    return sorted(out,key=lambda c:-c["a"])
ca, cb = comps(A), comps(B)
print("对齐后连通域（1x 帧，788×424）：")
for i in range(max(len(ca),len(cb))):
    a=ca[i] if i<len(ca) else None; b=cb[i] if i<len(cb) else None
    if a and b:
        print("  box%-20s a=%-6d | box%-20s a=%-6d | Δxy=(%+.2f,%+.2f) Δwh=(%+d,%+d)" % (
            (a['x'],a['y'],a['w'],a['h']),a['a'],(b['x'],b['y'],b['w'],b['h']),b['a'],
            b['cx']-a['cx'], b['cy']-a['cy'], b['w']-a['w'], b['h']-a['h']))
    else:
        print("  %s | %s" % (a and (a['x'],a['y'],a['w'],a['h']), b and (b['x'],b['y'],b['w'],b['h'])))
# 重叠率：逐要素
print("\n逐要素 IoU：")
for i in range(min(len(ca),len(cb))):
    a,b = ca[i],cb[i]
    m1=np.zeros((424,788),bool); m2=np.zeros((424,788),bool)
    m1[a['y']:a['y']+a['h'], a['x']:a['x']+a['w']] = (255-A[a['y']:a['y']+a['h'], a['x']:a['x']+a['w']]<128)
    m2[b['y']:b['y']+b['h'], b['x']:b['x']+b['w']] = (255-B[b['y']:b['y']+b['h'], b['x']:b['x']+b['w']]<128)
    # 用扩展到并集框
    x0=min(a['x'],b['x']); y0=min(a['y'],b['y']); x1=max(a['x']+a['w'],b['x']+b['w']); y1=max(a['y']+a['h'],b['y']+b['h'])
    p1=(255-A<128)[y0:y1,x0:x1]; p2=(255-B<128)[y0:y1,x0:x1]
    inter=(p1&p2).sum(); uni=(p1|p2).sum()
    print("  要素%d: 源a=%-6d 重绘a=%-6d IoU=%.4f  (Δ质心 %+.2f,%+.2f)" % (i,a['a'],b['a'],inter/uni, b['cx']-a['cx'], b['cy']-a['cy']))
