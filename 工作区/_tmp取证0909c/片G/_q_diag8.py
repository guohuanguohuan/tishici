# -*- coding: utf-8 -*-
"""探针：g3「吞标签翻转」的逐位证据——素材页 vs 件内页，旧 seed 外接矩形与标签 A 墨顶的相对位置。"""
import sys, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
import pymupdf
def load(alias, path):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
lg = load('lg', '片G实测.py')
PT = lg.PT

def seedrect(page):
    cs = lg.merge_rows(lg.cluster(lg.diag_items(page.get_drawings()), 8/25.4*PT))
    cs = [c for c in cs if c[0].width/PT >= 15 and c[0].height/PT >= 10 and c[1] >= lg.MINLONG]
    r = pymupdf.Rect(cs[0][0])
    for e, _ in cs[1:]:
        r |= e
    return pymupdf.Rect(r.x0-1, r.y0-1, r.x1+1, r.y1+1)

# --- 素材页
sp = pymupdf.open('C:/提示词/工作区/_tmp片G素材/tikz_tan6.pdf')[0]
r = sp.rect
clip = pymupdf.Rect(r.x0+0.2, r.y0+0.2, r.x1-0.2, r.y1-0.2)
S = seedrect(sp)
comps = lg.ink_components(sp, clip)
wire = lg.bboxes(comps, S, with_labels=False)
keep = [c for c in comps if c.intersects(S)]
U = keep[0]
for q in keep[1:]:
    U |= q
print('素材 seed mm x[%.2f,%.2f] y[%.2f,%.2f]' % (S.x0/PT, S.x1/PT, S.y0/PT, S.y1/PT))
print('素材 纯线框(∩seed, 无标签) %.2f×%.2f' % (wire.width/PT, wire.height/PT))
print('素材 旧法(相交seed)       %.2f×%.2f   ← 撑出的部分即被吞标签' % (U.width/PT, U.height/PT))
for c in sorted(keep, key=lambda z: -z.height):
    if not wire.contains(pymupdf.Rect(c.x0-0.5, c.y0-0.5, c.x1+0.5, c.y1+0.5)):
        print('   被吞块 mm x[%7.2f,%7.2f] y[%7.2f,%7.2f] w%5.2f h%5.2f  距seed底 %+.3fmm' % (
            c.x0/PT, c.x1/PT, c.y0/PT, c.y1/PT, c.width/PT, c.height/PT, (c.y0-S.y1)/PT))
# --- 件内页 p5
doc = pymupdf.open(lg.MAIN); p5 = doc[4]
S2 = seedrect(p5)
band = pymupdf.Rect(lg.MARGIN+0.4, max(lg.MARGIN-2, S2.y0-14*PT),
                    lg.MARGIN+lg.COLW-0.4, min(p5.rect.height-lg.BOT+2, S2.y1+14*PT))
comps2 = lg.ink_components(p5, band)
wire2 = lg.bboxes(comps2, S2, with_labels=False)
keep2 = [c for c in comps2 if c.intersects(S2)]
U2 = keep2[0]
for q in keep2[1:]:
    U2 |= q
print('件内 seed mm x[%.2f,%.2f] y[%.2f,%.2f]' % (S2.x0/PT, S2.x1/PT, S2.y0/PT, S2.y1/PT))
print('件内 纯线框 %.2f×%.2f  旧法 %.2f×%.2f  （缩放 k=%.4f）' % (
    wire2.width/PT, wire2.height/PT, U2.width/PT, U2.height/PT, lg.MAP[3][2]/86.0))
for c in sorted(comps2, key=lambda z: -z.height)[:8]:
    print('   件内大块 mm x[%7.2f,%7.2f] y[%7.2f,%7.2f] w%5.2f h%5.2f ∩seed=%s 距seed底 %+.3fmm' % (
        c.x0/PT, c.x1/PT, c.y0/PT, c.y1/PT, c.width/PT, c.height/PT, c.intersects(S2), (c.y0-S2.y1)/PT))
