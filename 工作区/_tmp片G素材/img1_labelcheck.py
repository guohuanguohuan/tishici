# -*- coding: utf-8 -*-
"""Iterate: compile probe (wide bbox), measure label ink vs source, print deltas."""
import subprocess, numpy as np, cv2, sys
from PIL import Image
subprocess.run(["xelatex","-interaction=nonstopmode","_probe_tikz.tex"],capture_output=True)
subprocess.run(["gswin64c","-q","-dNOPAUSE","-dBATCH","-sDEVICE=png16m","-r600","-dTextAlphaBits=4",
                "-dGraphicsAlphaBits=4","-sOutputFile=_probe_tikz.png","_probe_tikz.pdf"],capture_output=True)
im = 1.0 - np.array(Image.open('_probe_tikz.png').convert('L')).astype(float)/255.0
HR,WR = im.shape; pxR = 25.4/600.0; ORG=-3.0
n,lab,st,ce = cv2.connectedComponentsWithStats((im>0.5).astype(np.uint8),8)
ren=[]
for i in range(1,n):
    x,y,w,h,a = st[i]
    ren.append(dict(x0=ORG+x*pxR,x1=ORG+(x+w-1)*pxR,y0=(HR-y-h+1)*pxR,y1=(HR-y)*pxR,a=a))
S1=41.1/691; HS=1159
SRCL={'A1':(63,1,111,59),'C1':(606,19,663,78),'B1':(363,164,415,221),
      'A':(1,783,55,850),'C':(625,777,689,845),'B':(407,1091,466,1157)}
SRCS={'A1':(123,33,138,70),'C1':(666,51,681,88),'B1':(423,195,438,232)}
def mm(x,y): return x*S1,(HS-y)*S1
def nearest(cx,cy,amin=300,amax=40000):
    best=None
    for c in ren:
        if not (amin<=c['a']<=amax): continue
        d=((c['x0']+c['x1'])/2-cx)**2+((c['y0']+c['y1'])/2-cy)**2
        if best is None or d<best[0]: best=(d,c)
    return best[1]
print("%-4s | src x0..x1 y0..y1            | ren x0..x1 y0..y1            | dcx, dcy | w s/r  h s/r" % 'lbl')
tot=0
for who,(x0,y0,x1,y1) in SRCL.items():
    a,sy1=mm(x0,y0); b,sy0=mm(x1,y1); cx,cy=(a+b)/2,(sy0+sy1)/2
    c=nearest(cx,cy)
    dcx=(c['x0']+c['x1'])/2-cx; dcy=(c['y0']+c['y1'])/2-cy
    tot=max(tot,abs(dcx),abs(dcy))
    print("%-4s | %6.3f..%6.3f %6.3f..%6.3f | %6.3f..%6.3f %6.3f..%6.3f | %+.3f %+.3f | %.3f/%.3f %.3f/%.3f"
      % (who,a,b,sy0,sy1,c['x0'],c['x1'],c['y0'],c['y1'],dcx,dcy,b-a,c['x1']-c['x0'],sy1-sy0,c['y1']-c['y0']))
for who,(x0,y0,x1,y1) in SRCS.items():
    a,sy1=mm(x0,y0); b,sy0=mm(x1,y1); cx,cy=(a+b)/2,(sy0+sy1)/2
    c=nearest(cx,cy,amin=250,amax=30000)
    dcx=(c['x0']+c['x1'])/2-cx; dcy=(c['y0']+c['y1'])/2-cy
    tot=max(tot,abs(dcx),abs(dcy))
    print("sub %-2s| %6.3f..%6.3f %6.3f..%6.3f | %6.3f..%6.3f %6.3f..%6.3f | %+.3f %+.3f | %.3f/%.3f %.3f/%.3f"
      % (who,a,b,sy0,sy1,c['x0'],c['x1'],c['y0'],c['y1'],dcx,dcy,b-a,c['x1']-c['x0'],sy1-sy0,c['y1']-c['y0']))
print("max |delta| = %.3f mm" % tot)
