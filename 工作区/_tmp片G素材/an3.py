from PIL import Image
import numpy as np
im = Image.open(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png").convert("L")
a = np.array(im); b = a < 128

def col_runs(x):
    ys = np.nonzero(b[:, x])[0]
    if len(ys)==0: return []
    runs=[]; s=ys[0]; p=ys[0]
    for y in ys[1:]:
        if y==p+1: p=y
        else: runs.append((s,p)); s=y; p=y
    runs.append((s,p)); return runs

def row_runs(y):
    xs = np.nonzero(b[y, :])[0]
    if len(xs)==0: return []
    runs=[]; s=xs[0]; p=xs[0]
    for x in xs[1:]:
        if x==p+1: p=x
        else: runs.append((s,p)); s=x; p=x
    runs.append((s,p)); return runs

for x in [106,110,140,200,264,300,400,500,528,534,600,680,685]:
    print("col", x, col_runs(x))
print()
for y in [94,100,150,200,240,246,260,300,400,505,512,517,600,668,674]:
    print("row", y, row_runs(y))
