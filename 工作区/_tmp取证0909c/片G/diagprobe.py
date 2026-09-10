import pymupdf
import sys
PT = 72 / 25.4
MARGIN = 17.2 * PT
COLSEP = 7.6 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2


def diag_items(dr):
    """返回页内「非轴对齐」墨迹小矩形（斜线/曲线/填充块）——表线与文字带不产此类。"""
    out = []
    for o in dr:
        for it in o['items']:
            if it[0] == 'l':
                p1, p2 = it[1], it[2]
                dx, dy = abs(p2.x - p1.x), abs(p2.y - p1.y)
                if dx > 1.0 and dy > 1.0 and max(dx, dy) / PT > 2.0:      # 斜线 ≥2mm
                    out.append(pymupdf.Rect(min(p1.x, p2.x) - 0.3, min(p1.y, p2.y) - 0.3,
                                            max(p1.x, p2.x) + 0.3, max(p1.y, p2.y) + 0.3))
            elif it[0] == 'c':
                p1, p2, p3, p4 = it[1], it[2], it[3], it[4]
                xs = [p.x for p in (p1, p2, p3, p4)]
                ys = [p.y for p in (p1, p2, p3, p4)]
                w, h = max(xs) - min(xs), max(ys) - min(ys)
                if max(w, h) / PT > 2.0 and (w > 1.0 and h > 1.0):
                    out.append(pymupdf.Rect(min(xs) - 0.3, min(ys) - 0.3, max(xs) + 0.3, max(ys) + 0.3))
            elif it[0] == 're':
                r = it[1]
                if 0.6 * PT <= r.width <= 4 * PT and 0.6 * PT <= r.height <= 4 * PT:  # 实心小方块/点
                    out.append(pymupdf.Rect(r))
        if o.get('fill') is not None:
            r = o['rect']
            if 0.6 * PT <= r.width <= 4 * PT and 0.6 * PT <= r.height <= 4 * PT:
                out.append(pymupdf.Rect(r))
    return out


def cluster(rects, gap=6 / 25.4 * PT):
    rs = [pymupdf.Rect(r) for r in rects]
    changed = True
    while changed:
        changed = False
        res = []
        while rs:
            a = rs.pop()
            hit = None
            for i, b in enumerate(rs):
                ra = pymupdf.Rect(a.x0 - gap, a.y0 - gap, a.x1 + gap, a.y1 + gap)
                if ra.intersects(b) or a.intersects(b):
                    hit = i
                    break
            if hit is None:
                res.append(a)
            else:
                b = rs.pop(hit)
                a |= b
                rs.append(a)
                changed = True
        rs = res
    return rs


doc = pymupdf.open(sys.argv[1] if len(sys.argv) > 1 else 'main.pdf')
print('pages', doc.page_count)
tot = 0
for pno, p in enumerate(doc, 1):
    cs = cluster(diag_items(p.get_drawings()))
    for r in sorted(cs, key=lambda r: (r.y0, r.x0)):
        w, h = r.width / PT, r.height / PT
        if w < 15 or h < 15:
            continue
        col = 1 if r.x0 < MID else 2
        cl = MARGIN if col == 1 else MARGIN + COLW + COLSEP
        dev = ((r.x0 + r.x1) / 2 - (cl + COLW / 2)) / PT
        tot += 1
        print('p{0} c{1} x0={2:6.2f} y0={3:6.2f} w={4:6.2f} h={5:6.2f} dev={6:+5.2f}mm'.format(
            pno, col, r.x0 / PT, r.y0 / PT, w, h, dev))
print('TOTAL 图候选', tot)
