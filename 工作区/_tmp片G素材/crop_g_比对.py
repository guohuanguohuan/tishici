# -*- coding: utf-8 -*-
"""源位图 vs 重绘PDF：同尺（788px 宽）逐要素几何比对"""
import fitz, numpy as np, math, cv2, json

SRC = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image4.png"
PDF = "片G-image4-二面角-standalone.pdf"
W = 788

def src_gray():
    return cv2.imdecode(np.fromfile(SRC, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
def pdf_gray(target_w=W):
    d = fitz.open(PDF); p = d[0]
    z = target_w / p.rect.width
    pix = p.get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    return a

def comps(bw):
    n, lab, st, ce = cv2.connectedComponentsWithStats(bw.astype(np.uint8), connectivity=8)
    out=[]
    for i in range(1,n):
        x,y,w,h,a = st[i]
        out.append(dict(box=(int(x),int(y),int(w),int(h)), area=int(a), cx=float(ce[i][0]), cy=float(ce[i][1])))
    out.sort(key=lambda c:-c["area"])
    return out

def fitline(bw, p0, p1, halfw=7.0):
    H,Wd = bw.shape; x0,y0=p0; x1,y1=p1
    dx,dy = x1-x0, y1-y0; L=math.hypot(dx,dy); ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    pts=[]
    for t in np.linspace(0.06,0.94,int(L)):
        cx,cy = x0+ux*t*L, y0+uy*t*L
        acc=[]
        for s in np.arange(-halfw,halfw+0.25,0.25):
            X,Y=int(round(cx+nx*s)),int(round(cy+ny*s))
            if 0<=X<Wd and 0<=Y<H and bw[Y,X]: acc.append(s)
        if len(acc)>=3 and (max(acc)-min(acc))<6:
            pts.append((cx+nx*np.mean(acc), cy+ny*np.mean(acc)))
    pts=np.array(pts); mx,my=pts.mean(axis=0)
    U,S,Vt=np.linalg.svd(pts-[mx,my]); n=Vt[1]
    return np.array([n[0],n[1]]), float(n[0]*mx+n[1]*my)

HYP = {"EF":((70,206),(430,205)),"AB":((330,75),(680,74)),"EA":((75,200),(310,80)),
       "FB":((440,200),(685,80)),"ED":((75,212),(292,340)),"FC":((440,210),(660,340)),
       "DC":((305,346),(660,346)),"DB":((305,341),(688,80))}
def vertices(bw):
    fit={k:fitline(bw,a,b) for k,(a,b) in HYP.items()}
    def inter(k1,k2):
        A=np.array([fit[k1][0],fit[k2][0]]); b=np.array([fit[k1][1],fit[k2][1]])
        return np.linalg.solve(A,b)
    V={}
    V["E"]=inter("EF","EA"); V["A"]=inter("EA","AB")
    V["B1"]=inter("AB","FB"); V["B2"]=inter("AB","DB")
    V["F1"]=inter("EF","FB"); V["F2"]=inter("EF","FC")
    V["D1"]=inter("ED","DC"); V["D2"]=inter("DB","DC")
    V["C"]=inter("DC","FC"); V["X"]=inter("DB","FC")
    return V, fit

def linewidth(bw):
    """EF/AB/DC 竖切实测（水平线），斜线横切换算"""
    res={}
    for name,(y,) in {"EF":(205,),"AB":(74,),"DC":(346,)}.items():
        rs=[]
        for x in range(120,600,20):
            col=bw[y-8:y+9, x]; c=0
            for v in col:
                if v: c+=1
                elif c: rs.append(c); c=0
            if c: rs.append(c)
        res[name]=float(np.median(rs)) if rs else None
    return res

sa = src_gray(); sb = pdf_gray(W)
print(f"src {sa.shape}   redraw {sb.shape}")
bwa = sa<128; bwb = sb<128
ca, cb = comps(bwa), comps(bwb)
print("\n=== 连通域（线网＋字母块）===")
print(f"{'源':>28} | {'重绘':>28}")
for i in range(max(len(ca),len(cb))):
    A = ca[i] if i<len(ca) else None; B = cb[i] if i<len(cb) else None
    fa = f"box{A['box']} area{A['area']}" if A else ""
    fb = f"box{B['box']} area{B['area']}" if B else ""
    print(f"{fa:>28} | {fb:>28}")

Va,_ = vertices(bwa); Vb,_ = vertices(bwb)
print("\n=== 顶点（px@788 宽；Δ＝重绘−源）===")
keymap = {"E":"E","A":"A","B1":"B","F1":"F","D1":"D","C":"C","X":"X","B2":"B(db)","F2":"F(fc)","D2":"D(db)"}
for k in ["E","A","B1","B2","F1","F2","D1","D2","C","X"]:
    a=Va[k]; b=Vb[k]
    print(f"  {keymap[k]:8s} 源({a[0]:7.2f},{a[1]:7.2f})  重绘({b[0]:7.2f},{b[1]:7.2f})  Δ({b[0]-a[0]:+6.2f},{b[1]-a[1]:+6.2f})")
print("\n=== 线宽（像素，@788 宽）===")
print("  源  ", linewidth(bwa))
print("  重绘", linewidth(bwb))
json.dump(dict(src_verts={k:list(map(float,v)) for k,v in Va.items()},
               redraw_verts={k:list(map(float,v)) for k,v in Vb.items()}), open("_比对结果.json","w"), indent=1)
