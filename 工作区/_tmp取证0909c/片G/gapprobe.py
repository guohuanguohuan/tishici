import pymupdf
PT = 72 / 25.4
MARGIN = 17.2 * PT
COLSEP = 7.6 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
import sys
doc = pymupdf.open(sys.argv[1] if len(sys.argv) > 1 else 'main.pdf')
print('pages', doc.page_count)
MINHPT = 15 / 25.4 * PT           # 空白带高门限 15mm
for pno, p in enumerate(doc, 1):
    H = p.rect.height
    BOT = 20 * PT
    for ci in (0, 1):
        cl = MARGIN + ci * (COLW + COLSEP)
        bands = []
        for b in p.get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                r = pymupdf.Rect(ln['bbox'])
                cx = (r.x0 + r.x1) / 2
                if not (cl - 2 <= cx <= cl + COLW + 2):
                    continue
                if r.y1 < MARGIN - 2 or r.y0 > H - BOT + 2:
                    continue
                bands.append((r.y0, r.y1))
        bands.sort()
        merged = []
        for y0, y1 in bands:
            if merged and y0 <= merged[-1][1] + 0.5:
                merged[-1] = (merged[-1][0], max(merged[-1][1], y1))
            else:
                merged.append((y0, y1))
        top, bot = MARGIN - 1, H - BOT + 1
        gaps = []
        prev = top
        for y0, y1 in bands:
            pass
        for y0, y1 in merged:
            if y0 - prev > MINHPT:
                gaps.append((prev, y0))
            prev = max(prev, y1)
        if bot - prev > MINHPT:
            gaps.append((prev, bot))
        for g0, g1 in gaps:
            pix = p.get_pixmap(dpi=200, clip=pymupdf.Rect(cl, g0, cl + COLW, g1))
            s, w, h, n = pix.samples, pix.width, pix.height, pix.n
            minx, maxx, miny, maxy = w, -1, h, -1
            for y in range(h):
                row = False
                for x in range(w):
                    off = (y * w + x) * n
                    if (s[off] + s[off + 1] + s[off + 2]) / 3 < 200:
                        row = True
                        if x < minx:
                            minx = x
                        if x > maxx:
                            maxx = x
                if row:
                    if y < miny:
                        miny = y
                    if y > maxy:
                        maxy = y
            if maxx < 0:
                continue
            k = 72.0 / 200
            Wmm = (maxx - minx + 1) * k / PT
            Hmm = (maxy - miny + 1) * k / PT
            if Wmm >= 25 and Hmm >= 15:
                x0 = cl + minx * k
                y0 = g0 + miny * k
                dev = ((x0 + (maxx - minx + 1) * k / 2) - (cl + COLW / 2)) / PT
                print('p{0} c{1} gap={2:.1f}mm ink w={3:.2f} h={4:.2f} x0={5:.2f} y0={6:.2f} dev={7:+.2f}mm'.format(
                    pno, ci + 1, (g1 - g0) / PT, Wmm, Hmm, x0 / PT, y0 / PT, dev))
