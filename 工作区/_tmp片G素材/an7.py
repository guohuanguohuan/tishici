from PIL import Image
import numpy as np
im = Image.open(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png").convert("L")
a = np.array(im).astype(float)
ink = 1.0 - a/255.0     # 0..1 ink density

# 1) line thickness via ink mass across a cut (subpixel), for a set of solid lines
def thickness_col(x, y0, y1):
    return ink[y0:y1, x].sum()
def thickness_row(y, x0, x1):
    return ink[y, x0:x1].sum()

print("front face verticals (A-A1) mass per row:", [round(thickness_row(y,95,125),2) for y in (300,400,500,600)])
print("B-B1 vertical mass per row:", [round(thickness_row(y,515,545),2) for y in (300,400,500,600)])
print("C-C1 vertical mass per row:", [round(thickness_row(y,670,700),2) for y in (200,300,400)])
print("bottom edge A-B mass per col:", [round(thickness_col(x,660,685),2) for x in (200,300,400,500)])
print("top-front edge A1B1 mass per col:", [round(thickness_col(x,240,265),2) for x in (200,300,400,500)])
print("top-back edge D1C1 mass per col:", [round(thickness_col(x,85,110),2) for x in (300,400,500,600)])
print("A1C1 diagonal: vertical mass (thickness*sec) :", [(x, round(thickness_col(x,120,280),2)) for x in (150,200,340,420,500,580)])
print("dashed vertical D1D mass per row (x 255..275):", [(y, round(thickness_row(y,255,275),2)) for y in (130,140,170,180,320,330,360,470,480)])
print("dashed D-C mass per col (y 505..525):", [(x, round(thickness_col(x,505,525),2)) for x in (290,300,410,420,500,560,600,640)])
print("dashed A-D thickness (perp):", [(y, round(thickness_row(y, x0,x0+30),2)) for y,x0 in ((600,138),(500,182),(400,226),(350,248))])
print("dashed A-E thickness (perp):", [(y, round(thickness_row(y, x0,x0+30),2)) for y,x0 in ((600,138),(500,181),(400,224),(350,246))])

# 2) dash pattern along vertical dashed line: profile of ink along x=264.5 (sum over columns 262..267)
print("\ndash profile along vertical D1D (y 100..520):")
prof = ink[:, 262:268].sum(axis=1)
ys = np.arange(100, 521)
s = "".join("#" if v>3.0 else ("+" if v>0.6 else ".") for v in prof[100:521])
print(s)
runs=[]
inrun=False
for y in ys:
    v = prof[y]
    if v>0.6 and not inrun: start=y; inrun=True
    elif v<=0.6 and inrun: runs.append((start,y-1)); inrun=False
if inrun: runs.append((start,ys[-1]))
print("runs:", runs)
print("lengths:", [b-a1+1 for a1,b in runs])
print("gaps:", [runs[i+1][0]-runs[i][1]-1 for i in range(len(runs)-1)])
