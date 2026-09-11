# -*- coding: utf-8 -*-
"""裁图小工具：python _crop.py <pdf> <页> <x0mm> <y0mm> <x1mm> <y1mm> <out.png> [dpi]"""
import io
import sys

import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
a = sys.argv[1:]
pdf, pno = a[0], int(a[1])
x0, y0, x1, y1 = (float(v) for v in a[2:6])
out = a[6]
dpi = int(a[7]) if len(a) > 7 else 300
PT = 72 / 25.4
doc = pymupdf.open(pdf)
pg = doc[pno - 1]
clip = pymupdf.Rect(x0 * PT, y0 * PT, x1 * PT, y1 * PT)
pg.get_pixmap(dpi=dpi, clip=clip).save(out)
print(out, clip)
