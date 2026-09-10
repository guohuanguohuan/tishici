from PIL import Image
import numpy as np
im = Image.open(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png").convert("L")
a = np.array(im); b = a < 128
def col_runs(x, y0=0, y1=764):
    ys = np.nonzero(b[y0:y1, x])[0]+y0
    runs=[]
    if len(ys)==0: return runs
    s=ys[0]; p=ys[0]
    for y in ys[1:]:
        if y==p+1: p=y
        else: runs.append((s,p)); s=y; p=y
    runs.append((s,p)); return runs
print("== dot region columns ==")
for x in range(275, 330, 3):
    print(x, [r for r in col_runs(x, 150, 300)])
print("== rows through dot ==")
def row_runs(y, x0=0, x1=764):
    xs = np.nonzero(b[y, x0:x1])[0]+x0
    runs=[]
    if len(xs)==0: return runs
    s=xs[0]; p=xs[0]
    for x in xs[1:]:
        if x==p+1: p=x
        else: runs.append((s,p)); s=x; p=x
    runs.append((s,p)); return runs
for y in range(190, 225, 2):
    print(y, [r for r in row_runs(y, 240, 380)])
print("== A1C1 line thickness along x ==")
for x in [150,180,210,240,260,270,280,290,300,310,320,340,380,420,460,500,540,580,620,660]:
    ys=[r for r in col_runs(x,120,280)]
    print(x, ys)
