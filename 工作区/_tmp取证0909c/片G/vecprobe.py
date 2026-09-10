import pymupdf
PT = 72.0 / 25.4
d = pymupdf.open(r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf')
print('pages', d.page_count)
for pno, p in enumerate(d, 1):
    try:
        cl = p.cluster_drawings()
    except Exception as e:
        print('p%d cluster err %s' % (pno, e)); continue
    big = [r for r in cl if (r.width / PT) > 12 and (r.height / PT) > 8]
    print('p%-2d clusters=%-3d big(>12x8mm)=%d' % (pno, len(cl), len(big)))
    for r in sorted(big, key=lambda r: (r.y0, r.x0)):
        print('     x %.2f-%.2f  y %.2f-%.2f  w=%.2fmm h=%.2fmm' % (
            r.x0 / PT, r.x1 / PT, r.y0 / PT, r.y1 / PT, r.width / PT, r.height / PT))
