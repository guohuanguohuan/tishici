# -*- coding: utf-8 -*-
"""要素量测（同一套代码跑源图与重绘，保证可比）。
输入 764×764 灰度 ndarray（源图坐标系）；输出各要素的子像素量测值。"""
import numpy as np
from scipy import ndimage

def measure(a):
    ink = 1.0 - np.asarray(a, float)/255.0
    b = ink > 0.5
    out = {}
    def runs_along(v, i0, eps=0.55):
        r=[]; s=None
        for i,x in enumerate(v):
            if x>eps and s is None: s=i
            elif x<=eps and s is not None: r.append((i0+s,i0+i-1)); s=None
        if s is not None: r.append((i0+s,i0+len(v)-1))
        return r
    def rowc(y, xexp, half=14):
        x0=int(xexp)-half; x1=int(xexp)+half
        rs=runs_along(ink[y,x0:x1], x0)
        if not rs: return None
        lo,hi=min(rs,key=lambda r:0 if r[0]<=xexp<=r[1] else min(abs(r[0]-xexp),abs(r[1]-xexp)))
        w=ink[y,lo:hi+1]; xs=np.arange(lo,hi+1)
        return float((w*xs).sum()/w.sum()), float(w.sum())
    def colc(x, yexp, half=14):
        y0=int(yexp)-half; y1=int(yexp)+half
        rs=runs_along(ink[y0:y1,x], y0)
        if not rs: return None
        lo,hi=min(rs,key=lambda r:0 if r[0]<=yexp<=r[1] else min(abs(r[0]-yexp),abs(r[1]-yexp)))
        w=ink[lo:hi+1,x]; ys=np.arange(lo,hi+1)
        return float((w*ys).sum()/w.sum()), float(w.sum())
    def fit(pts, indep="x"):
        if indep=="x":
            A=np.vstack([np.array([p[0] for p in pts],float), np.ones(len(pts))]).T
            m,k=np.linalg.lstsq(A,np.array([p[1] for p in pts],float),rcond=None)[0]
        else:
            A=np.vstack([np.array([p[1] for p in pts],float), np.ones(len(pts))]).T
            m,k=np.linalg.lstsq(A,np.array([p[0] for p in pts],float),rcond=None)[0]
        return float(m), float(k)
    # 竖/横棱
    for nm, xg, ys in [("AA1",108.6,[300,420,540,640]),("BB1",527.4,[300,420,540,640]),("CC1",682.9,[150,250,350,450])]:
        v=[rowc(y,xg) for y in ys]
        out[nm]=dict(pos=float(np.mean([q[0] for q in v])), thick=float(np.mean([q[1] for q in v])))
    for nm, yg, xs in [("AB",671.9,[150,250,350,450]),("A1B1",253.0,[150,250,350,450]),("D1C1",96.0,[300,400,500,620])]:
        v=[colc(x,yg) for x in xs]
        out[nm]=dict(pos=float(np.mean([q[0] for q in v])), thick=float(np.mean([q[1] for q in v])))
    # 45° 斜棱：逐行质心（x 为函数）
    for nm, ylist, fx in [("BC",[540,570,600,630,650], lambda y: 527.4+(671.9-y)),
                          ("A1D1",[120,150,180,210,240], lambda y: 108.6+(253.0-y)*156/157),
                          ("B1C1",[120,150,180,210,240], lambda y: 527.4+(253.0-y)*155/157)]:
        pts=[]
        for y in ylist:
            xe=fx(y); q=rowc(y, xe, half=25)
            if q: pts.append((q[0], y))
        m,k = fit(pts)      # x = m*y + k
        out[nm]=dict(m=m, k=k, n=len(pts),
                     thick=float(np.mean([2*abs(q[1])/2/np.sqrt(2) for q in [rowc(y,fx(y)) for y in ylist] if q])))
    # A1C1 浅斜线：逐列
    pts=[]
    for x in [150,190,230,300,340,380,420,460,500,540,580,620,650]:
        ye = 253.0-0.2735*(x-108.6)
        q = colc(x, ye, half=12)
        if q: pts.append((x, q[0]))
    m,k = fit(pts)
    out["A1C1"]=dict(m=m,k=k,n=len(pts))
    # 虚线：连通域质心分组拟合
    lab,n = ndimage.label(b, structure=np.ones((3,3),int))
    sizes = ndimage.sum(b,lab,range(1,n+1)); big=int(np.argmax(sizes))+1
    dash=[]
    for i in range(1,n+1):
        if i==big: continue
        ys_,xs_=np.nonzero(lab==i)
        x0,x1,y0,y1=xs_.min(),xs_.max(),ys_.min(),ys_.max()
        if len(xs_)>400 or len(xs_)<60: continue
        if not (95<=x0 and x1<=700 and 80<=y0 and y1<=690): continue
        dash.append((float(xs_.mean()), float(ys_.mean()), int(x0),int(x1),int(y0),int(y1),len(xs_)))
    gV=[d for d in dash if abs(d[0]-264.5)<8 and (d[3]-d[2])<=8 and (d[5]-d[4])>=12]
    gH=[d for d in dash if abs(d[1]-514.5)<8 and (d[5]-d[4])<=8 and (d[3]-d[2])>=12]
    gAD=[]; gAE=[]
    for d in dash:
        if d in gV or d in gH: continue
        dy=d[1]-672.0
        if abs(dy)<1: continue
        s=(d[0]-108.61)/dy
        if abs(s+0.9936)<0.06: gAD.append(d)
        elif abs(s+0.3862)<0.06: gAE.append(d)
    out["dash_vertical_x"]=float(np.mean([d[0] for d in gV]))
    out["dash_horizontal_y"]=float(np.mean([d[1] for d in gH]))
    out["n_dash"]=dict(V=len(gV), H=len(gH), AD=len(gAD), AE=len(gAE))
    def fitd(g):
        cy=np.array([d[1] for d in g], float); cx=np.array([d[0] for d in g], float)
        for _ in range(3):                      # 剔除被合并/截断的 dash（残差>0.8px）
            A=np.vstack([cy,np.ones_like(cy)]).T
            m,k=np.linalg.lstsq(A,cx,rcond=None)[0]
            r=np.abs(cx-(m*cy+k))
            if r.max()<=0.8 or len(cy)<=3: break
            keep=r<=0.8; cy,cx=cy[keep],cx[keep]
        return float(m), float(k), float(np.abs(cx-(m*cy+k)).max())
    out["AD"]=dict(zip(("m","k","maxres"), fitd(gAD))); out["AD"]["n"]=len(gAD)
    out["AE"]=dict(zip(("m","k","maxres"), fitd(gAE))); out["AE"]["n"]=len(gAE)
    # 竖直虚线 dash on/off
    prof = ink[:, 262:268].sum(axis=1)
    rs=[r for r in runs_along(prof[100:521],100,eps=0.6)]
    out["dash_runs_V"]=rs
    ons=np.array([b_-a_+1 for a_,b_ in rs[1:-1]], float)
    offs=np.array([rs[i+1][0]-rs[i][1]-1 for i in range(len(rs)-1)], float)
    med=np.median(ons)
    ons=ons[(ons>0.6*med)&(ons<1.4*med)]          # 剔除与竖线/圆点粘连的合并段
    med2=np.median(offs)
    offs=offs[(offs>0.6*med2)&(offs<1.4*med2)]
    out["dash_on_px"]=float(np.median(ons)); out["dash_off_px"]=float(np.median(offs))
    out["dash_n"]=int(len(ons))
    # 顶点（交点）
    def inter_xy(l1, l2):
        def gen(l):
            if isinstance(l, dict) and "m" in l: return (-l["m"],1,-l["k"]) if l.get("kind","xy")=="xy" else (1,-l["m"],-l["k"])
            return l
        a1,b1,c1=gen(l1); a2,b2,c2=gen(l2)
        D=a1*b2-a2*b1
        return ((b1*c2-b2*c1)/D, (c1*a2-c2*a1)/D)
    L=out
    A=(L["AA1"]["pos"], L["AB"]["pos"]); B=(L["BB1"]["pos"], L["AB"]["pos"])
    A1=(L["AA1"]["pos"], L["A1B1"]["pos"]); B1=(L["BB1"]["pos"], L["A1B1"]["pos"])
    C=(L["CC1"]["pos"], L["BC"]["m"]*L["CC1"]["pos"]+L["BC"]["k"])
    C1=(L["CC1"]["pos"], L["D1C1"]["pos"]); D=(L["dash_vertical_x"], L["dash_horizontal_y"])
    D1=(L["dash_vertical_x"], L["D1C1"]["pos"])
    yE=(L["A1C1"]["m"]*L["AE"]["k"]+L["A1C1"]["k"])/(1-L["A1C1"]["m"]*L["AE"]["m"]); xE=L["AE"]["m"]*yE+L["AE"]["k"]
    out["V"]=dict(A=A,B=B,A1=A1,B1=B1,C=C,C1=C1,D=D,D1=D1,E=(xE,yE))
    out["E_t"]=(xE-A1[0])/(C1[0]-A1[0])
    # 点 E（实心圆）：上弧拟合
    m1,k1=L["A1C1"]["m"],L["A1C1"]["k"]
    pts=[]
    for x in range(int(xE)-9, int(xE)+10):
        col=ink[183:230,x]; idx=np.nonzero(col>0.5)[0]
        if not len(idx): continue
        yt=183+idx[0]-0.5
        if yt < m1*x+k1-3.0: pts.append((x,yt))
    P=np.array(pts,float); X,Y=P[:,0],P[:,1]
    Am=np.vstack([X,Y,np.ones_like(X)]).T
    sol,*_=np.linalg.lstsq(Am,X**2+Y**2,rcond=None)
    cx,cy=sol[0]/2,sol[1]/2; r=np.sqrt(sol[2]+cx**2+cy**2)
    out["dot"]=dict(c=(float(cx),float(cy)), r=float(r), n=len(pts))
    return out

def fmt(v, nd=2):
    if isinstance(v,(int,float,np.floating)): return ("%."+str(nd)+"f")%v
    if isinstance(v,(tuple,list)): return "("+",".join(fmt(x,nd) for x in v)+")"
    return str(v)
