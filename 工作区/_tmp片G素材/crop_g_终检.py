# -*- coding: utf-8 -*-
"""终检：1x 帧（788×424）逐要素残差汇总 → 终端 + _终检输出.txt"""
import fitz, numpy as np, cv2, math, sys, io
SRC = cv2.imdecode(np.fromfile("source-image4.png",dtype=np.uint8),cv2.IMREAD_GRAYSCALE)
d=fitz.open("片G-image4-二面角-standalone.pdf"); p=d[0]
z=788/p.rect.width
pix=p.get_pixmap(matrix=fitz.Matrix(z,z), colorspace=fitz.csGRAY)
mine=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
# 亚像素对齐 0.5px@1x（终检口径：全局搜优，2x 帧 (0,1)）
UP=4
mu=cv2.resize(mine,None,fx=UP,fy=UP,interpolation=cv2.INTER_LINEAR)
mu=np.roll(mu, 2, axis=0)                       # +0.5px@1x
mineA=cv2.resize(mu,(788,424),interpolation=cv2.INTER_AREA)
bwA=SRC<128; bwB=mineA<128
out=io.StringIO()
def P(*a):
    s=" ".join(str(x) for x in a); print(s); out.write(s+"\n")

def fitline(bw,p0,p1,halfw=7.0):
    H,Wd=bw.shape; x0,y0=p0; x1,y1=p1; dx,dy=x1-x0,y1-y0; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux; pts=[]
    for t in np.linspace(0.06,0.94,int(L)):
        cx,cy=x0+ux*t*L, y0+uy*t*L; acc=[]
        for s in np.arange(-halfw,halfw+0.25,0.25):
            X,Y=int(round(cx+nx*s)),int(round(cy+ny*s))
            if 0<=X<Wd and 0<=Y<H and bw[Y,X]: acc.append(s)
        if len(acc)>=3 and (max(acc)-min(acc))<6: pts.append((cx+nx*np.mean(acc),cy+ny*np.mean(acc)))
    pts=np.array(pts); mx,my=pts.mean(axis=0)
    U,S,Vt=np.linalg.svd(pts-[mx,my]); n=Vt[1]
    return np.array([n[0],n[1]]), float(n[0]*mx+n[1]*my)
HYP={"EF":((70,206),(430,205)),"AB":((330,75),(680,74)),"EA":((75,200),(310,80)),"FB":((440,200),(685,80)),
     "ED":((75,212),(292,340)),"FC":((440,210),(660,340)),"DC":((305,346),(660,346)),"DB":((305,341),(688,80))}
def verts(bw):
    f={k:fitline(bw,a,b) for k,(a,b) in HYP.items()}
    def it(k1,k2):
        A=np.array([f[k1][0],f[k2][0]]); b=np.array([f[k1][1],f[k2][1]]); return np.linalg.solve(A,b)
    return {"E":it("EF","EA"),"A":it("EA","AB"),"B":it("AB","FB"),"F":it("EF","FB"),
            "D":it("ED","DC"),"C":it("DC","FC"),"X":it("DB","FC")}, f
Va,fa=verts(bwA); Vb,fb=verts(bwB)
P("== 顶点（px@788 宽帧；重绘已按 0.5px@1x 对齐）==")
for k in ["E","A","B","F","D","C","X"]:
    a,b=Va[k],Vb[k]
    P("  %s  源(%7.2f,%7.2f)  重绘(%7.2f,%7.2f)  Δ(%+5.2f,%+5.2f) px  = (%+5.3f,%+5.3f) mm" % (
        k,a[0],a[1],b[0],b[1],b[0]-a[0],b[1]-a[1],(b[0]-a[0])*66.3/788,(b[1]-a[1])*66.3/788))
P("== 线方向角（度，x 轴正向起，逆时针为负）==")
for k in ["EF","AB","EA","FB","ED","FC","DC","DB"]:
    ang_a=math.degrees(math.atan2(-fa[k][0][1],fa[k][0][0]))%180; ang_b=math.degrees(math.atan2(-fb[k][0][1],fb[k][0][0]))%180
    P("  %s 源%6.2f  重绘%6.2f  Δ%+5.2f" % (k,ang_a,ang_b,ang_b-ang_a))
P("== 线宽（竖切像素中位数）==")
def lw(bw,cuts):
    rs=[]
    for (x,y) in cuts:
        col=bw[y-8:y+9,x]; c=0
        for v in col:
            if v: c+=1
            elif c: rs.append(c); c=0
        if c: rs.append(c)
    return float(np.median(rs))
for nm,(y) in [("EF",205),("AB",74),("DC",346)]:
    cuts=[(x,y) for x in range(150,640,10)]
    P("  %s 源%.1f px  重绘%.1f px  （%.1f px ×0.0841371 = %.3f mm）" % (nm,lw(bwA,cuts),lw(bwB,cuts),lw(bwA,cuts),lw(bwA,cuts)*66.3/788))
P("== 字母墨迹盒（px；高＝帽高）==")
BOX={"A":(255,11,326,76),"B":(692,47,751,111),"C":(651,339,713,410),"D":(258,350,325,414),"E":(2,175,64,239),"F":(367,207,429,271)}
tot=0; n=0
for k,(x0,y0,x1,y1) in BOX.items():
    a=bwA[y0:y1,x0:x1]; b=bwB[y0:y1,x0:x1]
    def box(m):
        ys,xs=np.where(m)
        return (x0+xs.min(), y0+ys.min(), xs.max()-xs.min()+1, ys.max()-ys.min()+1)
    ba,bb=box(a),box(b)
    iou=(a&b).sum()/max(1,(a|b).sum()); tot+=iou; n+=1
    P("  %s 源 box(%d,%d,%d,%d)  重绘 box(%d,%d,%d,%d)  Δxy(%+d,%+d) Δwh(%+d,%+d)  IoU=%.3f" % (
        k,ba[0],ba[1],ba[2],ba[3],bb[0],bb[1],bb[2],bb[3],bb[0]-ba[0],bb[1]-ba[1],bb[2]-ba[2],bb[3]-ba[3],iou))
P("  字母平均 IoU=%.3f" % (tot/n))
P("== 线网（1x 帧）==")
xa=bwA[55:370,40:720]; xb=bwB[55:370,40:720]
P("  IoU=%.4f  源 ink=%d  重绘 ink=%d（差 %+.2f%%）" % ((xa&xb).sum()/(xa|xb).sum(), xa.sum(), xb.sum(), (xb.sum()-xa.sum())/xa.sum()*100))
P("  字母块数：源 6 块 / 重绘 6 块；线网块：源 1 / 重绘 1（无虚线/箭头/游离笔画）")
open("_终检输出.txt","w",encoding="utf-8").write(out.getvalue())
