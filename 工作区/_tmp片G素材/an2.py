from PIL import Image
import numpy as np
from scipy import ndimage
im = Image.open(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png").convert("L")
a = np.array(im); b = a < 128
lab, n = ndimage.label(b, structure=np.ones((3,3),int))
print("n=",n)
info=[]
for i in range(1, n+1):
    ys, xs = np.nonzero(lab==i)
    x0,x1,y0,y1 = xs.min(), xs.max(), ys.min(), ys.max()
    info.append(dict(i=i, x0=x0,x1=x1,y0=y0,y1=y1,w=x1-x0+1,h=y1-y0+1,area=len(xs),
                     cx=xs.mean(), cy=ys.mean()))
info.sort(key=lambda d:(-d["area"]))
for d in info:
    kind = "H-dash" if d["w"]>2.5*d["h"] else ("V-dash" if d["h"]>2.5*d["w"] else "blob")
    print(f'#{d["i"]:3d} area={d["area"]:6d} w={d["w"]:4d} h={d["h"]:4d} x[{d["x0"]:4d},{d["x1"]:4d}] y[{d["y0"]:4d},{d["y1"]:4d}] c=({d["cx"]:.1f},{d["cy"]:.1f}) {kind}')
