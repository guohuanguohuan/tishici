# -*- coding: utf-8 -*-
"""源 vs 重绘：亚像素全局对齐（线网区互相关）＋逐要素残差"""
import fitz, numpy as np, cv2, math
SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image4.png"
PDF = "片G-image4-二面角-standalone.pdf"
def src_gray():
    return cv2.imdecode(np.fromfile(SRC, dtype=np.uint8), cv2.IMREAD_GRAYSCALE).astype(np.float32)
def pdf_gray(w=788):
    d=fitz.open(PDF); p=d[0]; z=w/p.rect.width
    pix=p.get_pixmap(matrix=fitz.Matrix(z,z), colorspace=fitz.csGRAY)
    return np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width).astype(np.float32)

A = 255-src_gray(); B = 255-pdf_gray()
UP = 4
def up(x): return cv2.resize(x, None, fx=UP, fy=UP, interpolation=cv2.INTER_LINEAR)
Au, Bu = up(A), up(B)
# 线网区（去字母）：源线网 box(64,73,631,277) -> 留裕量
x0,y0,x1,y1 = 40, 55, 720, 370
At = Au[y0*UP:y1*UP, x0*UP:x1*UP]
best=None
for dy in range(-3*UP, 3*UP+1):
    for dx in range(-3*UP, 3*UP+1):
        Bs = np.roll(np.roll(Bu, dy, axis=0), dx, axis=1)
        Bt = Bs[y0*UP:y1*UP, x0*UP:x1*UP]
        num = float((At*Bt).sum()); den = math.sqrt(float((At*At).sum())*float((Bt*Bt).sum()))
        sc = num/den
        if best is None or sc>best[0]: best=(sc,dx,dy)
sc,dx,dy = best
print("全局最优对齐（线网互相关，UP=%d）: dx=%.3f px, dy=%.3f px, NWCC=%.5f" % (UP, dx/UP, dy/UP, sc))
# 残差图（对齐后）
Bs = np.roll(np.roll(Bu, dy, axis=0), dx, axis=1)
diff = np.abs(At-Bt).mean() if False else np.abs(At-Bs[y0*UP:y1*UP, x0*UP:x1*UP]).mean()
print("对齐后线网区平均绝对差 =", round(diff,3), "/255")
# 阈值化残差：线宽 4px -> 对齐误差 1px 会整体显影；看有多少像素差>128
Ba = (255-Au)<128; Bb = (255-Bs)<128
ov = (Ba[y0*UP:y1*UP, x0*UP:x1*UP] & Bb[y0*UP:y1*UP, x0*UP:x1*UP]).sum()
ua = Ba[y0*UP:y1*UP, x0*UP:x1*UP].sum(); ub = Bb[y0*UP:y1*UP, x0*UP:x1*UP].sum()
print("线网区 ink 像素（UP^2）：源=%d 重绘=%d 交集=%d  IoU=%.4f" % (ua, ub, ov, ov/float(ua+ub-ov)))
np.save("_align.npy", np.array([dx/UP, dy/UP]))
# 逐要素：对齐后各连通域（含字母）
def comps(mask):
    n,lab,st,ce = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    out=[]
    for i in range(1,n):
        x,y,w,h,a = st[i]
        if a < 200: continue
        out.append((x,y,w,h,a))
    return sorted(out, key=lambda t:-t[4])
Ma = (A<128); Mb = (Bs<128)
print("\n对齐后连通域（px，788 宽帧）：")
ca, cb = comps(Ma), comps(Mb)
for i in range(max(len(ca),len(cb))):
    a = ca[i] if i<len(ca) else None; b = cb[i] if i<len(cb) else None
    if a and b:
        print("  源 box%-22s | 重绘 box%-22s | Δ(%+d,%+d) Δwh(%+d,%+d)" % (str(a[:4]),str(b[:4]),b[0]-a[0],b[1]-a[1],b[2]-a[2],b[3]-a[3]))
    else:
        print("  源 box%-22s | 重绘 box%-22s" % (str(a and a[:4]), str(b and b[:4])))
