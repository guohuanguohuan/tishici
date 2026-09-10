from PIL import Image
import numpy as np
im = Image.open(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png").convert("L")
a = np.array(im); b = a < 128
sub = b[185:225, 265:315]
for i,row in enumerate(sub):
    print(185+i, "".join("#" if v else "." for v in row))
