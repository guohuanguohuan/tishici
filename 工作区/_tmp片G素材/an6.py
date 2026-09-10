from PIL import Image
import numpy as np
im = Image.open(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png").convert("L")
a = np.array(im); b = a < 128
x0,x1,y0,y1 = 240, 330, 176, 236
sub = b[y0:y1, x0:x1]
hdr = "    " + "".join(str((x0+i)//100%10) for i in range(x1-x0))
hdr2= "    " + "".join(str((x0+i)//10%10) for i in range(x1-x0))
hdr3= "    " + "".join(str((x0+i)%10) for i in range(x1-x0))
print(hdr); print(hdr2); print(hdr3)
for i,row in enumerate(sub):
    print(f"{y0+i:4d}" + "".join("#" if v else "." for v in row))
