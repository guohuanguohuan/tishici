from PIL import Image
import numpy as np, json
im = Image.open(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png").convert("L")
a = np.array(im).astype(float); ink = 1.0 - a/255.0

# A1C1 线参数（measure3 拟合）：y = -0.27050x + 281.897
m1, k1 = -0.27050, 281.897
# AE 线：x = -0.3908y + 370.5125（初步），截距误差大 → 重拟合（用未合并 dash，鲁棒）
dash_AE = [(125.8,627.2),(139.4,592.2),(152.9,557.1),(166.4,522.2),(179.9,487.3),
           (193.4,452.2),(207.0,417.3),(220.5,382.3),(233.9,347.3),(247.5,312.5)]
cy = np.array([p[1] for p in dash_AE]); cx = np.array([p[0] for p in dash_AE])
for it in range(4):
    A = np.vstack([cy, np.ones_like(cy)]).T
    m,k = np.linalg.lstsq(A,cx,rcond=None)[0]
    r = cx-(m*cy+k); keep = np.abs(r) < max(0.6, np.abs(r).max()-0.01)
    if keep.all(): break
    cy, cx = cy[keep], cx[keep]
print("AE robust fit: x = %.5f*y + %.4f  (n=%d, maxres=%.3f)" % (m,k,len(cy),np.abs(r).max()))
# AE 与 A1C1 交点
A1 = np.array([108.61,253.0]); C1 = np.array([683.0,96.0])
# y = m1 x + k1 ; x = m y + k  → y = m1(m y + k)+k1 → y(1-m1 m) = m1 k + k1
yE = (m1*k + k1)/(1-m1*m); xE = m*yE + k
print("E (两线交点) = (%.2f, %.2f)" % (xE,yE))
T = (xE-A1[0])/(C1[0]-A1[0]); print("E 参数 t (A1→C1, 按 x) = %.4f" % T)

# 圆点：上边界弧拟合（列向首个 ink>0.5 的 y，减 0.5 作为边界）
pts=[]
for x in range(281, 299):
    col = ink[185:215, x]
    idx = np.nonzero(col>0.5)[0]
    if len(idx)==0: continue
    ytop = 185+idx[0]-0.5
    yexp = m1*x+k1
    if ytop < yexp-3.0:      # 只用圆弧明显高于线的列
        pts.append((x, ytop))
P = np.array(pts, float)
print("弧上边界点:", [(int(x),round(y,1)) for x,y in pts])
# 最小二乘圆（代数拟合）
X,Y = P[:,0],P[:,1]
Amat = np.vstack([X,Y,np.ones_like(X)]).T
sol,res,*_ = np.linalg.lstsq(Amat, X**2+Y**2, rcond=None)
cx0, cy0 = sol[0]/2, sol[1]/2; r0 = np.sqrt(sol[2]+cx0**2+cy0**2)
print("circle fit: c=(%.2f, %.2f) r=%.2f" % (cx0,cy0,r0))
# 与 A1C1 线的交点（圆心投影到线）
# 线: y = m1 x + k1 → m1 x - y + k1 = 0 ; 投影
d = (m1*cx0 - cy0 + k1)/(m1**2+1)
px_, py_ = cx0 - m1*d, cy0 + d
print("圆心在线上的投影 = (%.2f, %.2f), 圆心到线距 = %.2f" % (px_,py_, abs(d)*np.sqrt(m1**2+1)))
json.dump(dict(AE=[float(m),float(k)], E=[float(xE),float(yE)], E_t=float(T),
               dot=[float(cx0),float(cy0),float(r0)],
               dot_on_line=[float(px_),float(py_)], n_arc=len(pts)),
          open("dot.json","w"), indent=1)
