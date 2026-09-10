# -*- coding: utf-8 -*-
import numpy as np, math, json
bw = np.load("_bw.npy").astype(bool)
H,W = bw.shape

# hypothesis: infinite lines defined by 2 approx points (px,py)
HYP = {
 "EF": ((70,206),(430,205)),
 "AB": ((330,75),(680,74)),
 "EA": ((75,200),(310,80)),
 "FB": ((440,200),(685,80)),
 "ED": ((75,212),(292,340)),
 "FC": ((440,210),(660,340)),
 "DC": ((305,346),(660,346)),
 "DB": ((305,341),(688,80)),
}
def refine(p0, p1, halfw=7.0, tmin=0.06, tmax=0.94):
    """sample along line, perpendicular centroid -> LSQ fit (a,b,c) with ax+by=c (a^2+b^2=1)"""
    x0,y0 = p0; x1,y1 = p1
    dx,dy = x1-x0, y1-y0; L = math.hypot(dx,dy); ux,uy = dx/L, dy/L
    nx,ny = -uy, ux
    pts=[]
    for t in np.linspace(tmin,tmax,int(L)):
        cx,cy = x0+ux*t*L, y0+uy*t*L
        acc=[]; wsum=0
        for s in np.arange(-halfw, halfw+0.25, 0.25):
            X,Y = int(round(cx+nx*s)), int(round(cy+ny*s))
            if 0<=X<W and 0<=Y<H and bw[Y,X]:
                acc.append(s); wsum+=1
        if len(acc)>=3 and (max(acc)-min(acc))<6:
            pts.append((cx+nx*np.mean(acc), cy+ny*np.mean(acc)))
    pts=np.array(pts)
    # LSQ total least squares
    mx,my = pts.mean(axis=0)
    U,S,Vt = np.linalg.svd(pts-[mx,my])
    d = Vt[0]; n = Vt[1]
    c = n[0]*mx + n[1]*my
    return dict(n=(n[0],n[1]), c=c, dir=(d[0],d[1]), npts=len(pts),
                p0=(float(pts[0][0]),float(pts[0][1])), p1=(float(pts[-1][0]),float(pts[-1][1])))
fit={}
for k,(p0,p1) in HYP.items():
    fit[k]=refine(p0,p1)
    f=fit[k]
    print(f"{k}: n=({f['n'][0]:+.5f},{f['n'][1]:+.5f}) c={f['c']:8.3f} dir=({f['dir'][0]:+.5f},{f['dir'][1]:+.5f}) npts={f['npts']} ends={np.round(f['p0'],1)}..{np.round(f['p1'],1)}")

def inter(k1,k2):
    n1,c1 = fit[k1]["n"], fit[k1]["c"]; n2,c2 = fit[k2]["n"], fit[k2]["c"]
    A = np.array([n1,n2]); b=np.array([c1,c2])
    return tuple(np.linalg.solve(A,b))
print("\n== vertex intersections (px) ==")
V = {}
V["E"] = inter("EF","EA"); V["A"] = inter("EA","AB"); V["B_ab_fb"] = inter("AB","FB")
V["B_ab_db"] = inter("AB","DB"); V["F"] = inter("EF","FB"); V["D_ed_dc"] = inter("ED","DC")
V["D_db_dc"] = inter("DB","DC"); V["C"] = inter("DC","FC"); V["F_fc_ef"] = inter("EF","FC")
V["X_DB_FC"] = inter("DB","FC")
for k,v in V.items(): print(f"  {k:10s} = ({v[0]:8.2f},{v[1]:8.2f})")
json.dump({k:{'n':v['n'],'c':v['c'],'dir':v['dir']} for k,v in fit.items()}, open("_fit.json","w"), indent=1)
np.save("_verts.npy", np.array([V[k] for k in ["E","A","B_ab_fb","F","D_ed_dc","C"]]))
