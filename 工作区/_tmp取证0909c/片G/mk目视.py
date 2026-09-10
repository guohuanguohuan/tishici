import pymupdf
PT = 72 / 25.4
doc = pymupdf.open(r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf')
OUT = r'C:\提示词\工作区\_tmp取证0909c\片G\目视-'
JOBS = [('g6三联-p2c2', 2, 108.8, 110, 192.8, 143),
        ('g1棱柱-p3c2', 3, 120, 74, 182, 152),
        ('g2正方体E-p4c1', 4, 25, 40, 95, 96),
        ('g3正方体6-p5c1', 5, 14, 80, 104, 160),
        ('g4二面角-p6c1', 6, 17.2, 118, 101.2, 165),
        ('g5折叠-p6c2', 6, 108.8, 146, 192.8, 192)]
for name, pno, x0, y0, x1, y1 in JOBS:
    pix = doc[pno - 1].get_pixmap(dpi=170, clip=pymupdf.Rect(x0 * PT, y0 * PT, x1 * PT, y1 * PT))
    pix.save(OUT + name + '.png')
    print(name, pix.width, pix.height)
