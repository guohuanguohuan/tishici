import sys
import pymupdf

pdf = sys.argv[1]
doc = pymupdf.open(pdf)
last = doc[len(doc) - 1]
hits = last.search_for('笔记与错题整理')
for h in hits:
    print('文字 rect y0=%.1f y1=%.1f x0=%.1f' % (h.y0, h.y1, h.x0))
for dr in last.get_drawings():
    r = dr['rect']
    if dr['fill'] is None and dr['color'] is not None and r.width > 60:
        c = dr['color']
        print('线 y0=%.1f y1=%.1f x0=%.1f x1=%.1f w=%.1f color=%s' % (r.y0, r.y1, r.x0, r.x1, r.width, ['%.3f' % v for v in c]))
doc.close()
