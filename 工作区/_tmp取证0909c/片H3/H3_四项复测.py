# -*- coding: utf-8 -*-
"""H3 四项复测：E5 页码块 / E6 栏线灰 / E8 句末标点 / 学习目标后隙。参数＝PDF 路径。"""
import sys
import numpy as np
import pymupdf
from PIL import Image
import io
from collections import Counter
from scipy import ndimage

PDF = sys.argv[1] if len(sys.argv) > 1 else r'C:/提示词/工作区/字替对照-0909/variantF/main.pdf'
PXMM = 14.1732
PTMM = 72 / 25.4

def gray(pno, dpi=360):
    pix = pymupdf.open(PDF)[pno].get_pixmap(dpi=dpi)
    return np.asarray(Image.open(io.BytesIO(pix.tobytes('png'))).convert('L')).astype(np.int16)

def runs_of(seg, thr=128):
    rs, h = [], seg.shape[0]
    for r in range(h):
        c = 0
        for v in (seg[r] < thr):
            if v: c += 1
            elif c: rs.append(c); c = 0
        if c: rs.append(c)
    return Counter(rs).most_common(4)

doc = pymupdf.open(PDF)
print('pages =', doc.page_count)

print('\n== E5 页码块 ==')
for pno in range(doc.page_count):
    g = gray(pno)
    H, W = g.shape
    sub = g[H*4//5:, :]
    lab, n = ndimage.label(np.abs(sub-221) <= 14, structure=np.ones((3,3)))
    for sl in ndimage.find_objects(lab):
        ys, xs = sl
        if xs.stop-xs.start < 200 or ys.stop-ys.start < 60: continue
        y0,y1,x0,x1 = ys.start+H*4//5, ys.stop+H*4//5, xs.start, xs.stop
        seg = g[y0:y1, x0:x1]
        dys, dxs = np.nonzero(seg < 128)
        nx0,nx1,ny0,ny1 = dxs.min(), dxs.max()+1, dys.min(), dys.max()+1
        num = seg[ny0:ny1, nx0:nx1]
        vals = num[num < 200]
        odd = pno % 2 == 0
        inner = nx0/PXMM if odd else (x1-x0-nx1)/PXMM
        mid = runs_of(num[ (ny1-ny0)//3 : 2*(ny1-ny0)//3, :])
        print(f'p{pno+1} 块 {((x1-x0)/PXMM):.2f}×{((y1-y0)/PXMM):.2f}mm  '
              f'右缘距纸右{(W-x1)/PXMM:.2f} 左缘{x0/PXMM:.2f} 底距纸底{(H-y1)/PXMM:.2f}  '
              f'数字 ink 高{(ny1-ny0)/PXMM:.2f}mm({ny1-ny0}px) 灰min{vals.min()}中位{int(np.median(vals))} '
              f'距块{"左" if odd else "右"}{inner:.2f}mm runs_mid{mid}')

print('\n== 数字 span（rawdict）==')
for pno in range(doc.page_count):
    pg = doc[pno]
    for b in pg.get_text('rawdict')['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            for sp in l['spans']:
                t = ''.join(c['c'] for c in sp['chars']).strip()
                if t == str(pno+1) and sp['bbox'][1] > pg.rect.height*0.9:
                    print(f'p{pno+1} [{t}] {sp["font"]} {sp["size"]:.2f} color={sp["color"]:#08x} bbox={[round(v,1) for v in sp["bbox"]]}')

print('\n== E6 栏线 ==')
for pno in range(doc.page_count):
    pg = doc[pno]
    for d in pg.get_drawings():
        r = d['rect']
        if r.width <= 1.5 and r.height >= 0.5*(pg.rect.height - 19.6*PTMM - 20*PTMM):
            c = d.get('color') or d.get('fill')
            if c and abs(r.x0 - pg.rect.width/2) < 3:
                rgb = tuple(round(v*255) for v in (c if isinstance(c, tuple) else (c.r, c.g, c.b)))
                print(f'p{pno+1} 栏线 w={d.get("width"):.3f}pt color={rgb} y[{r.y0:.0f},{r.y1:.0f}]')
                break
# 渲染芯
vals = []
for pno in range(doc.page_count):
    pg = doc[pno]
    mid = pg.rect.width/2
    pix = pg.get_pixmap(dpi=300, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(mid-2, 100, mid+2, pg.rect.height-60))
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    col = min(range(pix.width), key=lambda c: abs((mid-2)+(c+0.5)/(300/72.0)-mid))
    vs = sorted(a[:, col][a[:, col] < 250].tolist())
    if vs: vals.append(vs[len(vs)//2])
print('栏线渲染芯中位 =', sorted(vals)[len(vals)//2] if vals else None, '（全品靶 188）')

print('\n== E8 标点 ==')
cnt = Counter()
for pno in range(doc.page_count):
    for b in doc[pno].get_text('rawdict')['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            for sp in l['spans']:
                for c in sp['chars']:
                    if c['c'] in '。．.':
                        cnt[c['c']] += 1
print('PDF 字符计数:', {repr(k): v for k, v in sorted(cnt.items())})

print('\n== 学习目标后隙（p1）==')
page = doc[0]
rows = []
for b in page.get_text('rawdict')['blocks']:
    if b['type'] != 0: continue
    for l in b['lines']:
        cs = [c for sp in l['spans'] for c in sp['chars']]
        t = ''.join(c['c'] for c in cs)
        if t in ('1.', '2.', '3.') and 180 < l['bbox'][1] < 300:
            rows.append((t, cs, l['bbox'][1]))
for t, cs, y in rows:
    db = cs[1]['bbox']
    best = None
    for b in page.get_text('rawdict')['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            if not any('FZKTK' in sp['font'] for sp in l['spans']): continue
            if abs(l['bbox'][1] - y) < 16:
                for sp in l['spans']:
                    if 'FZKTK' in sp['font']:
                        ch = sp['chars'][0]
                        if best is None or ch['bbox'][0] < best[1][0]:
                            best = (ch['c'], ch['bbox'])
    if not best: 
        print(f'{t} 未配对内容行'); continue
    px = 600/72.0
    r = pymupdf.Rect(db[0]-1, min(db[1], best[1][1])-1, best[1][2]+1, max(db[3], best[1][3])+1)
    pix = page.get_pixmap(dpi=600, clip=r)
    a = np.asarray(Image.open(io.BytesIO(pix.tobytes('png'))).convert('L'))
    m = a < 160
    xs = np.nonzero(m.any(axis=0))[0]
    cl = []
    if len(xs):
        s0 = prev = xs[0]
        for x in xs[1:]:
            if x - prev > 3: cl.append((s0, prev)); s0 = x
            prev = x
        cl.append((s0, prev))
    gap = (cl[1][0]-cl[0][1]-1)/px*25.4/72 if len(cl) >= 2 else None
    print(f'{t} 内容首字{best[0]!r} 内容bbox_x0={best[1][0]:.2f}pt(={best[1][0]/PTMM:.2f}mm) dot_bbox_x1={db[2]:.2f} '
          f'ink隙={"%.3f" % gap if gap else "?"}mm 簇{cl[:3]}')
