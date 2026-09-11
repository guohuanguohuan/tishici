# 实测位图门值.py —— 回退轮0910 条3：位图口径六图实测（供 _测v4断言.py 定窗）
# 口径：pymupdf get_image_info(xrefs=True) 取六图矩形；图内真墨矩形＝PIL 原生位图墨 bbox 映射；
#       前距/下距/零侵入＝600dpi 真墨级；置宽＝PDF 矩形宽；栏心偏＝矩形心中 − 栏心。
import os
import numpy as np
import pymupdf
from PIL import Image

BASE = 'C:/提示词/工作区/字替对照-0909/variantF/'
PT = 72 / 25.4
MARGIN = 17.2 * PT
COLSEP = 7.6 * PT
PAGE_W = 595.276
COLW = (PAGE_W - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = [MARGIN, MARGIN + COLW + COLSEP]
BODY_SIZE = (9.6, 11.2)
BODY_MINW = 4.0 * PT
PAD05 = 0.5 * PT          # 图矩形外扩 0.5mm
LAB_PAD = 2.0             # 正文行墨渲染外扩（pt）

FRAG = {(1408, 374): 'g6-triple', (691, 1159): 'g1-prism', (764, 764): 'g2-cubeE',
        (521, 496): 'g3-cube6', (788, 424): 'g4-dihedral', (1798, 1350): 'g5-fold'}
PNG = {'g6-triple': 'media/media/sub3_B_4.png', 'g1-prism': 'media/media/image1.png',
       'g2-cubeE': 'media/media/image2.png', 'g3-cube6': 'media/media/image3.png',
       'g4-dihedral': 'media/media/image4.png', 'g5-fold': 'media/media/image5.png'}
DECL = {'g6-triple': 84.0, 'g1-prism': 28.8, 'g2-cubeE': 32.7,
        'g3-cube6': 54.1, 'g4-dihedral': 47.5, 'g5-fold': 42.5}
ORDER = ['g6-triple', 'g1-prism', 'g2-cubeE', 'g3-cube6', 'g4-dihedral', 'g5-fold']

doc = pymupdf.open(BASE + 'main.pdf')


def text_lines(page):
    ls = []
    for b in page.get_text('dict')['blocks']:
        if b.get('type') != 0:
            continue
        for ln in b.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if not t:
                continue
            ls.append(dict(t=t, r=pymupdf.Rect(ln['bbox']),
                           sz=max(sp['size'] for sp in ln['spans'])))
    return ls


def is_body(L):
    return BODY_SIZE[0] <= L['sz'] <= BODY_SIZE[1] and L['r'].width >= BODY_MINW


def line_ink600(page, r):
    """区域 600dpi 真墨 bbox（pt）；无墨 None。"""
    pm = page.get_pixmap(dpi=600, colorspace=pymupdf.csGRAY, clip=r)
    a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
    m = a < 128
    if not m.any():
        return None
    ys, xs = np.nonzero(m)
    sc = 72.0 / 600
    return pymupdf.Rect(r.x0 + xs.min() * sc, r.y0 + ys.min() * sc,
                        r.x0 + (xs.max() + 1) * sc, r.y0 + (ys.max() + 1) * sc)


INKB = {}
for f, fn in PNG.items():
    im = Image.open(BASE + fn).convert('RGBA')
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
    g = np.asarray(Image.alpha_composite(bg, im).convert('L'))
    m = g < 128
    ys, xs = np.nonzero(m)
    px, py = im.size
    INKB[f] = (xs.min() / px, ys.min() / py, (xs.max() + 1) / px, (ys.max() + 1) / py)

rows = []
for pno in range(1, doc.page_count + 1):
    for info in doc[pno - 1].get_image_info(xrefs=True):
        r = pymupdf.Rect(info['bbox'])
        key = (info['width'], info['height'])
        rows.append((pno, r, key, info['xref']))
print('PDF 内位图对象数 =', len(rows))

figs = []
for pno, r, key, xref in rows:
    f = FRAG[key]
    col = 1 if (r.x0 + r.x1) / 2 < MID else 2
    cl = COLL[col - 1]
    fx0, fy0, fx1, fy1 = INKB[f]
    ir = pymupdf.Rect(r.x0 + fx0 * r.width, r.y0 + fy0 * r.height,
                      r.x0 + fx1 * r.width, r.y0 + fy1 * r.height)   # 图内真墨矩形
    pg = doc[pno - 1]
    body = [L for L in text_lines(pg) if is_body(L)
            and cl - 2 <= (L['r'].x0 + L['r'].x1) / 2 <= cl + COLW + 2]
    # 600dpi 正文行墨
    for L in body:
        # 墨＝行自身 bbox 内 600dpi 真墨（不外扩，避免邻图行混入图墨）
        L['ink'] = line_ink600(pg, L['r']) or L['r']
    above = [L for L in body if L['ink'].y1 <= ir.y0 + 0.3]
    below = [L for L in body if L['ink'].y0 >= ir.y1 - 0.3]
    up = max(above, key=lambda z: z['ink'].y1) if above else None
    dn = min(below, key=lambda z: z['ink'].y0) if below else None
    gap_u = (ir.y0 - up['ink'].y1) / PT if up else None
    gap_d = (dn['ink'].y0 - ir.y1) / PT if dn else None
    dev = ((r.x0 + r.x1) / 2 - (cl + COLW / 2)) / PT
    wdev = r.width / PT - DECL[f]
    infl = pymupdf.Rect(r.x0 - PAD05, r.y0 - PAD05, r.x1 + PAD05, r.y1 + PAD05)
    hits = []
    for L in body:
        if L['r'].intersects(infl) or (L['ink'] and L['ink'].intersects(infl)):
            hits.append(L['t'][:18])
    figs.append((f, pno, col, wdev, dev, gap_u, gap_d, len(hits),
                 r.width / PT, r.height / PT, up['t'][:12] if up else '—', dn['t'][:12] if dn else '—',
                 hits[:2]))
figs.sort(key=lambda z: ORDER.index(z[0]))
print(f"{'图':10s} {'落位':6s} {'置宽':7s} {'宽偏':6s} {'栏心偏':7s} {'前距':6s} {'下距':6s} {'侵入':4s} 矩形mm 上邻/下邻")
for (f, p, c, wdev, dev, gu, gd, nh, rw, rh, ut, dt, hs) in figs:
    print(f'{f:10s} p{p}c{c}  {rw:6.2f} {wdev:+6.2f} {dev:+7.2f} '
          f'{gu if gu is None else round(gu,2)}  {gd if gd is None else round(gd,2)}  {nh}   '
          f'{rw:.1f}x{rh:.1f}  [{ut}]/[{dt}] {hs if hs else ""}')
gu = [g[5] for g in figs]
gd = [g[6] for g in figs]
dv = [abs(g[4]) for g in figs]
wd = [abs(g[3]) for g in figs]
print('前距 min/max =', min(gu), max(gu), '→ 窗 [%s, %s]' % (round(min(gu) - 0.25, 2), round(max(gu) + 0.25, 2)))
print('下距 min/max =', min(gd), max(gd), '→ 窗 [%s, %s]' % (round(min(gd) - 0.25, 2), round(max(gd) + 0.25, 2)))
print('栏心偏 max =', round(max(dv), 3), '→ 窗 ±%s' % round(max(dv) + 0.25, 2))
print('置宽偏差 max =', round(max(wd), 3), 'mm（门 ±0.5）')
