from PIL import Image
import numpy as np
from scipy import ndimage
im = Image.open(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png").convert("L")
a = np.array(im)
b = a < 128
lab, n = ndimage.label(b, structure=np.ones((3,3),int))
print("components:", n)
objs = ndimage.find_objects(lab)
rows=[]
for i,sl in enumerate(objs, start=1):
    ys, xs = sl
    h = ys.stop-ys.start; w = xs.stop-xs.start
    area = int((lab[sl]==i).sum())
    rows.append((area,w,h,xs.start,ys.start,xs.stop,ys.stop,i))
rows.sort(reverse=True)
for r in rows[:25]:
    print(f"area={r[0]:7d} w={r[1]:4d} h={r[2]:4d} x=[{r[3]:4d},{r[4]}] y=[{r[5]:4d},{r[6]}]")
