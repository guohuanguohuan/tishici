"""精测 v3 → geom.json（全部要素的像素坐标，子像素）"""
from PIL import Image
import numpy as np, json
from scipy import ndimage

P = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png"
im = Image.open(P).convert("L"); a = np.array(im).astype(float)
ink = 1.0 - a/255.0; b = a < 128
LAB, N = ndimage.label(b, structure=np.ones((3,3),int))

def fit_xy(pts, indep="x"):     # pts: [(x,y)] → 返回 y=m*x+k 或 x=m*y+k
    if indep=="x":
        A=np.vstack([np.array([p[0] for p in pts],float), np.ones(len(pts))]).T
        m,k = np.linalg.lstsq(A, np.array([p[1] for p in pts],float), rcond=None)[0]
    else:
        A=np.vstack([np.array([p[1] for p in pts],float), np.ones(len(pts))]).T
        m,k = np.linalg.lstsq(A, np.array([p[0] for p in pts],float), rcond=None)[0]
    return float(m), float(k)

# ---- 实线：竖直/水平（质心法，已测）
vert = {"AA1":108.61, "BB1":527.39, "CC1":683.00}
horiz= {"AB":672.00, "A1B1":253.00, "D1C1":96.00}
# ---- 斜实线（自逐行质心）
diag_pts = {
 "BC":  [(658.00,540),(628.42,570),(598.50,600),(568.64,630),(549.00,650)],
 "A1D1":[(240.50,120),(210.58,150),(181.00,180),(151.41,210),(121.53,240)],
 "B1C1":[(659.41,120),(629.50,150),(599.59,180),(570.00,210),(540.50,240)],
}
# A1C1 对角线（浅斜）：逐列质心
A1C1_pts=[]
for x in [150,190,230,300,340,380,420,460,500,540,580,620,650]:
    v = ink[115:275, x]; s=None; runs=[]
    idx=np.arange(115,275)
    for i,val in enumerate(v):
        if val>0.55 and s is None: s=i
        elif val<=0.55 and s is not None: runs.append((115+s,115+i-1)); s=None
    if s is not None: runs.append((115+s,274))
    # 取“最下方且与 A1C1 预期接近”的 run；预期 y ≈ 253.5-0.2735*(x-108.6)
    yexp = 253.0-0.2735*(x-108.61)
    cands=[r for r in runs if abs((r[0]+r[1])/2 - yexp) < 12]
    if not cands: continue
    lo,hi = min(cands, key=lambda r: abs((r[0]+r[1])/2-yexp))
    w=ink[lo:hi+1,x]; ys=np.arange(lo,hi+1)
    A1C1_pts.append((x, float((w*ys).sum()/w.sum())))
# ---- 虚线：从连通域取 dash 质心，分组
dash=[]; labels=[]
for i in range(1,N+1):
    ys,xs = np.nonzero(LAB==i)
    area=len(xs)
    if area==0 or area>400: continue
    x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    if x0>=95 and x1<=700 and y0>=80 and y1<=690 and (x0<250 or y0>250):  # 排除标签区
        dash.append((float(xs.mean()), float(ys.mean()), x0,x1,y0,y1,area,i))
# 归组
grpAD=[]; grpAE=[]; grpV=[]; grpH=[]
for d in dash:
    cx,cy,x0,x1,y0,y1,area,i = d
    if abs(cx-264.5)<8 and y1-y0>12 and x1-x0<9: grpV.append(d)
    elif abs(cy-514.5)<8 and x1-x0>12 and y1-y0<9: grpH.append(d)
    else:
        dx,dy = cx-108.61, cy-672.0
        if dy==0: continue
        slope = dx/dy
        if abs(slope-(-0.9936))<0.06: grpAD.append(d)
        elif abs(slope-(-0.3862))<0.06: grpAE.append(d)
        else: print("未归类 dash:", d)
def fit_dashes(g):
    cx=np.array([d[0] for d in g]); cy=np.array([d[1] for d in g])
    A=np.vstack([cy, np.ones_like(cy)]).T
    m,k=np.linalg.lstsq(A,cx,rcond=None)[0]
    res = cx - (m*cy+k)
    return float(m), float(k), float(np.abs(res).max()), len(g)
AD = fit_dashes(grpAD); AE = fit_dashes(grpAE)
Vx = np.mean([d[0] for d in grpV]); Vy = np.mean([d[1] for d in grpH])
print("dash groups:", len(grpAD), len(grpAE), len(grpV), len(grpH))
print("AD line: x=%.4f y + %.4f (maxres %.2f, n=%d)" % AD)
print("AE line: x=%.4f y + %.4f (maxres %.2f, n=%d)" % AE)
print("vertical dashed x = %.2f ; horizontal dashed y = %.2f" % (Vx,Vy))

def ix(l1, l2):   # l=(m,k) 形式 x=m*y+k 或 y=m*x+k
    m1,k1,kind1 = l1; m2,k2,kind2 = l2
    if kind1=="xy" and kind2=="xy":   # y=m1x+k1, y=m2x+k2
        x=(k2-k1)/(m1-m2); return (x, m1*x+k1)
    # 一般式：把 y=m*x+k 统一成 a*x+b*y+c=0
    def gen(l):
        m,k,kind=l
        return (-m,1,-k) if kind=="xy" else (1,-m,-k)
    a1,b1,c1 = gen(l1); a2,b2,c2 = gen(l2)
    D = a1*b2-a2*b1
    return ((b1*c2-b2*c1)/D, (c1*a2-c2*a1)/D)

mBC,kBC = fit_xy(diag_pts["BC"], "x"); LBC=(mBC,kBC,"xy")
mA1D1,kA1D1 = fit_xy(diag_pts["A1D1"], "x"); LA1D1=(mA1D1,kA1D1,"xy")
mB1C1,kB1C1 = fit_xy(diag_pts["B1C1"], "x"); LB1C1=(mB1C1,kB1C1,"xy")
mA1C1,kA1C1 = fit_xy(A1C1_pts, "x"); LA1C1=(mA1C1,kA1C1,"xy")
LAD=(AD[0],AD[1],"yx"); LAE=(AE[0],AE[1],"yx")
print("BC: y=%.5f x + %.3f" % (mBC,kBC), "A1D1: y=%.5f x + %.3f" % (mA1D1,kA1D1),
      "B1C1: y=%.5f x + %.3f" % (mB1C1,kB1C1), "A1C1: y=%.5f x+%.3f" % (mA1C1,kA1C1))

A=(108.61,672.0); B=(527.39,672.0); A1=(108.61,253.0); B1=(527.39,253.0)
C = ix(LBC, (0.0,683.0,"yx"))     # x=683
C2= ix(LBC, (0.0,Vy,"yx"))
C1=(683.0,96.0)
D1= ix(LA1D1, (0.0,96.0,"yx"))
D = ix(LA1D1, (0.0,Vy,"yx"))
Dv= ix((0.0,Vx,"yx"), (0.0,96.0,"yx"))
E = ix(LA1C1, LAE)
print("A",A,"B",B,"A1",A1,"B1",B1)
print("C(BC∩x=683)", tuple(round(v,2) for v in C), " C(BC∩y=%.2f)"%Vy, tuple(round(v,2) for v in C2))
print("C1",C1,"D1",tuple(round(v,2) for v in D1),"D",tuple(round(v,2) for v in D))
print("vertical∩A1D1:", tuple(round(v,2) for v in Dv))
print("E = A1C1 ∩ AE =", tuple(round(v,2) for v in E))
frac = (E[0]-A1[0])/(C1[0]-A1[0])
print("E 占 A1C1 比例 (按 x): %.4f" % frac)
# 交点一致性核对
def on_line(P, l, tol=1.5):
    a_,b_,c_ = ((-l[0],1,-l[1]) if l[2]=="xy" else (1,-l[0],-l[1]))
    return abs(a_*P[0]+b_*P[1]+c_)/np.hypot(a_,b_)
print("A1 到 A1C1 距离 %.2f, C1 到 A1C1 距离 %.2f" % (on_line(A1,LA1C1), on_line(C1,LA1C1)))
print("A 到 AE 距离 %.2f" % on_line(A,LAE))
print("A 到 AD 距离 %.2f" % on_line(A,LAD))
print("B 到 BC 距离 %.2f, C 到 BC %.2f" % (on_line(B,LBC), on_line(C,LBC)))
print("B1 到 B1C1 %.2f, C1 到 B1C1 %.2f" % (on_line(B1,LB1C1), on_line(C1,LB1C1)))
print("A1 到 A1D1 %.2f, D1 到 A1D1 %.2f" % (on_line(A1,LA1D1), on_line(D1,LA1D1)))

# ---- 圆点（E 处实心点）：拟合
sub = b[188:222, 278:302]
ys,xs = np.nonzero(sub); ys=ys+188; xs=xs+278
# 取位于 A1C1 线上方/外部、且不在虚线 dash 上的像素：用“离 A1C1 线 > 3.2px”筛
pts=[]
for x,y in zip(xs,ys):
    a_,b_,c_=(-mA1C1,1,-kA1C1)
    dist = abs(a_*x+b_*y+c_)/np.hypot(a_,b_)
    if dist>3.6:
        pts.append((x,y))
P_ = np.array(pts,float)
# 最小二乘圆拟合
X=P_[:,0]; Y=P_[:,1]
Amat = np.vstack([X, Y, np.ones_like(X)]).T
bb = X**2+Y**2
sol,*_ = np.linalg.lstsq(Amat, bb, rcond=None)
cx, cy = sol[0]/2, sol[1]/2
r = np.sqrt(sol[2]+cx**2+cy**2)
print("dot fit: center=(%.2f,%.2f) r=%.2f  n=%d" % (cx,cy,r,len(pts)))
print("dot 中心到 A1C1 距离 %.2f" % on_line((cx,cy), LA1C1))
print("E(line) 与 dot 中心差: %.2f, %.2f" % (E[0]-cx, E[1]-cy))

# ---- 标签 bbox
labs = {}
for i in range(1,N+1):
    ys,xs=np.nonzero(LAB==i)
    if len(xs)<150: continue
    x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    labs[i]=(int(x0),int(x1),int(y0),int(y1),int(len(xs)))
names={1:"D1_D",2:"C1_C",6:"E",9:"A1_A",11:"B1_B",24:"D",26:"C",46:"A",47:"B",
       3:"D1_1",4:"C1_1",10:"A1_1",13:"B1_1"}
print("labels:")
lab_out={}
for i,nm in names.items():
    x0,x1,y0,y1,ar = labs[i]
    lab_out[nm]=dict(x0=int(x0),x1=int(x1),y0=int(y0),y1=int(y1),h=int(y1-y0+1),w=int(x1-x0+1),
                     cx=float((x0+x1)/2), cy=float((y0+y1)/2))
    print("  %-5s x[%d,%d] y[%d,%d] w=%d h=%d c=(%.1f,%.1f)" % (nm,x0,x1,y0,y1,x1-x0+1,y1-y0+1,(x0+x1)/2,(y0+y1)/2))

json.dump(dict(
  vert=vert, horiz=horiz,
  lines=dict(BC=[mBC,kBC], A1D1=[mA1D1,kA1D1], B1C1=[mB1C1,kB1C1], A1C1=[mA1C1,kA1C1],
             AD=[AD[0],AD[1]], AE=[AE[0],AE[1]]),
  dash_vertical_x=Vx, dash_horizontal_y=Vy,
  V=dict(A=A,B=B,A1=A1,B1=B1,C=(round(C[0],2),round(C[1],2)),C1=C1,D=(round(D[0],2),round(D[1],2)),D1=(round(D1[0],2),round(D1[1],2))),
  E=[round(E[0],2),round(E[1],2)], E_frac=frac,
  dot=[round(cx,2),round(cy,2),round(r,2)],
  labels=lab_out), open("geom.json","w"), ensure_ascii=False, indent=1)
print("→ geom.json")
