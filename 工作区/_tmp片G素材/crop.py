import sys
from PIL import Image
im = Image.open(r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png").convert("L")
x0,y0,x1,y1,scale,out = int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
c = im.crop((x0,y0,x1,y1)).resize(((x1-x0)*scale,(y1-y0)*scale), Image.NEAREST)
c.save(out); print(out, c.size)
