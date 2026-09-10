# -*- coding: utf-8 -*-
"""探针：旧口径「吞标签」逐图定位——件内侧/素材侧各吞了哪些文本层标签，压线余量多少 mm。"""
import sys, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
import pymupdf
def load(alias, path):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
lg = load('lg', '片G实测.py')
aw = load('aw', '权威实测.py')
PT = lg.PT
SRC = lg.SRC

def oldseed(page):
    cs = lg.merge_rows(lg.cluster(lg.diag_items(page.get_drawings()), 8 / 25.4 * PT))
    cs = [c for c in cs if c[0].width / PT >= 15 and c[0].height / PT >= 10 and c[1] >= lg.MINLONG]
    r = pymupdf.Rect(cs[0][0])
    for e, _ in cs[1:]:
        r |= e
    return pymupdf.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1)

doc = pymupdf.open(aw.MAIN)
cand = []
for pno in range(1, doc.page_count + 1):
    stk = aw.strokes(doc[pno - 1])
    for c in aw.clusters(stk):
        cand.append((pno, doc[pno - 1], stk, c))
cand.sort(key=lambda z: (z[0], z[3][0].y0))

for i, (tag, sn, wbox, frag, at) in enumerate(aw.MAP):
    pno, page, stk, clus = cand[i]
    lines = aw.text_lines(page)
    d = aw.measure_fig(page, stk, clus, lines, box_mm=wbox)
    seed = oldseed(page)
    W = d['W']
    R = pymupdf.Rect(W.x0 - 1.0, W.y0 - 1.0, W.x1 + 1.0, W.y1 + 1.0)
    col = d['col']; cl = d['cl']
    band = pymupdf.Rect(cl + 0.4, max(lg.MARGIN - 2, seed.y0 - 14 * PT),
                        cl + lg.COLW - 0.4, min(page.rect.height - lg.BOT + 2, seed.y1 + 14 * PT))
    comps = lg.ink_components(page, band)
    sw = [c for c in comps if c.intersects(seed) and not R.contains(c)]
    # 素材侧
    sd = pymupdf.open(SRC + sn); sp = sd[0]
    sseed = oldseed(sp)
    sW = aw.measure_fig(sp, aw.strokes(sp), aw.clusters(aw.strokes(sp))[0], aw.text_lines(sp), src=True)['W'] if False else None
    print('%-9s p%dc%d 件内seed x[%.2f,%.2f] y[%.2f,%.2f] 吞块 %d 个' % (
        tag, pno, col, seed.x0/PT, seed.x1/PT, seed.y0/PT, seed.y1/PT, len(sw)))
    for c in sorted(sw, key=lambda z: -(z.width*z.height)):
        who = [L['t'][:6] for L in d['labs'] if c.intersects(L['ink'])]
        print('    件内吞 mm x[%6.2f,%6.2f] y[%6.2f,%6.2f] w%5.2f h%5.2f 越W界 %s 标签=%s' % (
            c.x0/PT, c.x1/PT, c.y0/PT, c.y1/PT, c.width/PT, c.height/PT,
            'x0%+.2f x1%+.2f y0%+.2f y1%+.2f' % ((c.x0-W.x0)/PT, (c.x1-W.x1)/PT, (c.y0-W.y0)/PT, (c.y1-W.y1)/PT),
            ','.join(who) or '?'))
