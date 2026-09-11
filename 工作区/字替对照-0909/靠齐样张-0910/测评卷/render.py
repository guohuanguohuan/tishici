"""测评卷渲染链：先清 png/，再 150dpi 出图。"""
import os
import glob
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "png")

for f in glob.glob(os.path.join(PNG, "*.png")):
    os.remove(f)

doc = pymupdf.open(os.path.join(HERE, "main.pdf"))
for i, page in enumerate(doc, 1):
    out = os.path.join(PNG, "page%d.png" % i)
    page.get_pixmap(dpi=150).save(out)
    print("wrote", out)
