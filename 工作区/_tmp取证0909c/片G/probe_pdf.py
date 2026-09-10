import fitz, math
PT = 72.0 / 25.4          # 1pt = 1/72in; 1mm = 72/25.4 pt
PATH = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
d = fitz.open(PATH)
print('pages', d.page_count)
for pno, p in enumerate(d, 1):
    dr = p.get_drawings()
    seg = 0
    xs, ys = [], []
    for o in dr:
        r = o['rect']
        for it in o['items']:
            if it[0] == 'l':
                if math.hypot(it[2].x - it[1].x, it[2].y - it[1].y) > 2.0:   # >2pt(≈0.7mm) 算一条实线段
                    seg += 1
            elif it[0] == 'c':
                seg += 1
            elif it[0] == 're':
                seg += 1
        if len(dr) and o.get('even_odd') is None:
            pass
    print('p%-3d images=%-2d drawings=%-4d segs=%-5d' % (pno, len(p.get_images()), len(dr), seg))
