"""片G 0910 六图下置·终版实测（取证表＋断言口径来源）。

定位＝页内「非轴对齐矢量墨」聚簇（斜线/曲线，簇内跨度≥5mm 的斜长笔 ≥3 → 真图；
      表线/正文/花形/√× 自绘不产此类，表内向量箭头斜长笔＝0）＋同 y 带并簇（三联三子图成一簇）。
边界＝同栏内「行宽 ≥15mm」的文字行（图内标签系单字母窄行，天然排除）——
      上邻行底＝前距起算线，下邻行顶＝下距起算线。
实测＝边界带内 600dpi 全墨 bbox → 墨宽/墨高/左缘/右缘/栏心偏差/前距/下距。
同比核验＝素材 standalone PDF 同法测墨 bbox，按其页宽折算缩放系数，预测件内墨尺寸，出 Δ。
"""
import pymupdf

PT = 72 / 25.4
MARGIN = 17.2 * PT
COLSEP = 7.6 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
BOT = 20 * PT
DPI = 600
MINLONG = 3
BODYLINE_W = 15.0 * PT         # 正文行判定：行宽 ≥15mm
SRC = r'C:\提示词\工作区\_tmp片G素材\\'
MAP = [   # (件内顺序标签, 素材 standalone, 置宽目标 mm, 片段文件)
    ('g6 三联', 'sub3_投影三联-纯tikz体检.pdf', 84.0, 'figs/g6-triple.tikz'),
    ('g1 直三棱柱', 'img1_tikz.pdf', 41.1, 'figs/g1-prism.tikz'),
    ('g2 正方体E', 'image2_重绘.pdf', 42.0, 'figs/g2-cubeE.tikz'),
    ('g3 正方体6', 'tikz_tan6.pdf', 84.0, 'figs/g3-cube6.tikz'),
    ('g4 二面角', '片G-image4-二面角-standalone.pdf', 66.3, 'figs/g4-dihedral.tikz'),
    ('g5 折叠', 'fig-image5-fold.pdf', 54.7, 'figs/g5-fold.tikz'),
]


def diag_items(dr):
    out = []
    for o in dr:
        for it in o['items']:
            if it[0] == 'l':
                p1, p2 = it[1], it[2]
                dx, dy = abs(p2.x - p1.x), abs(p2.y - p1.y)
                if dx > 1.0 and dy > 1.0 and max(dx, dy) / PT > 2.0:
                    out.append((pymupdf.Rect(min(p1.x, p2.x) - .3, min(p1.y, p2.y) - .3,
                                             max(p1.x, p2.x) + .3, max(p1.y, p2.y) + .3),
                                max(dx, dy) / PT >= 5.0))
            elif it[0] == 'c':
                ps = it[1:5]
                xs = [q.x for q in ps]; ys = [q.y for q in ps]
                w, h = max(xs) - min(xs), max(ys) - min(ys)
                if max(w, h) / PT > 2.0 and w > 1.0 and h > 1.0:
                    out.append((pymupdf.Rect(min(xs) - .3, min(ys) - .3, max(xs) + .3, max(ys) + .3),
                                max(w, h) / PT >= 5.0))
            elif it[0] == 're':
                r = it[1]
                if 0.6 * PT <= r.width <= 4 * PT and 0.6 * PT <= r.height <= 4 * PT:
                    out.append((pymupdf.Rect(r), False))
        if o.get('fill') is not None:
            r = o['rect']
            if 0.6 * PT <= r.width <= 4 * PT and 0.6 * PT <= r.height <= 4 * PT:
                out.append((pymupdf.Rect(r), False))
    return out


def cluster(pairs, gap):
    rs = [pymupdf.Rect(a) for a, _ in pairs]
    lg = [1 if b else 0 for _, b in pairs]
    par = list(range(len(rs)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    for i in range(len(rs)):
        for j in range(i + 1, len(rs)):
            a = pymupdf.Rect(rs[i]); a.x0 -= gap; a.y0 -= gap; a.x1 += gap; a.y1 += gap
            if a.intersects(rs[j]):
                x, y = find(i), find(j)
                if x != y:
                    par[x] = y
    grp = {}
    for i in range(len(rs)):
        grp.setdefault(find(i), []).append(i)
    out = []
    for g in grp.values():
        r = pymupdf.Rect(rs[g[0]])
        for k in g[1:]:
            r |= rs[k]
        out.append((r, sum(lg[k] for k in g)))
    return out


def merge_rows(cs, ytol=3 * PT, xgap=20 * PT):
    changed = True
    while changed:
        changed = False
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                (a, na), (b, nb) = cs[i], cs[j]
                oy = min(a.y1, b.y1) - max(a.y0, b.y0)
                vgap = max(a.x0, b.x0) - min(a.x1, b.x1)
                ox = min(a.x1, b.x1) - max(a.x0, b.x0)
                hgap = max(a.y0, b.y0) - min(a.y1, b.y1)
                if (oy > -ytol and vgap <= xgap) or (ox > -ytol and hgap <= xgap):
                    cs[i] = (a | b, na + nb)
                    del cs[j]
                    changed = True
                    break
            if changed:
                break
    return cs


def ink_bbox(page, clip, dpi=DPI, thr=200):
    pix = page.get_pixmap(dpi=dpi, clip=clip)
    s, w, h, n = pix.samples, pix.width, pix.height, pix.n
    k = 72.0 / dpi
    minx, maxx, miny, maxy = w, -1, h, -1
    for y in range(h):
        base = y * w * n
        row = False
        for x in range(w):
            off = base + x * n
            if (s[off] + s[off + 1] + s[off + 2]) / 3 < thr:
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
        return None
    return (clip.x0 + minx * k, clip.y0 + miny * k,
            clip.x0 + (maxx + 1) * k, clip.y0 + (maxy + 1) * k)


def col_lines(page, cl, wide_only=True):
    ls = []
    for b in page.get_text('dict')['blocks']:
        for ln in b.get('lines', []):
            r = pymupdf.Rect(ln['bbox'])
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if not t or r.width < 0.5:
                continue
            if not (cl - 2 <= (r.x0 + r.x1) / 2 <= cl + COLW + 2):
                continue
            if wide_only and r.width < BODYLINE_W:
                continue
            ls.append((t, r))
    return ls


def ink_components(page, clip, dpi=DPI, thr=200):
    """带内二值墨 → 8 邻接连通域列表 [(rect_pt, npx)]。"""
    import numpy as np
    from scipy import ndimage
    pix = page.get_pixmap(dpi=dpi, clip=clip)
    w, h, n, s = pix.width, pix.height, pix.n, pix.samples
    a = np.frombuffer(s, dtype=np.uint8).reshape(h, w, n)[:, :, :3].mean(axis=2)
    mask = a < thr
    lab, cnt = ndimage.label(mask, structure=np.ones((3, 3)))
    k = 72.0 / dpi
    out = []
    if cnt:
        objs = ndimage.find_objects(lab)
        for i, sl in enumerate(objs, 1):
            if sl is None:
                continue
            y0, y1 = sl[0].start, sl[0].stop
            x0, x1 = sl[1].start, sl[1].stop
            out.append((pymupdf.Rect(clip.x0 + x0 * k, clip.y0 + y0 * k,
                                     clip.x0 + x1 * k, clip.y0 + y1 * k),
                        int((lab[sl] == i).sum())))
    return out


def fig_bbox(page, clip, seed, dpi=DPI, wire_only=False):
    """图墨 bbox：
       wire＝与矢量种子簇相交的连通域之并（＝线框，件内与素材同法，可比对）；
       full＝wire ∪ 外扩 4mm 内且 ≤14×12mm 的连通域（＝图内标签，TikZ \\node 出真文字），
             用于「不侵入文字」的缝隙核验。标签判据取小到只收字母/下标级小块。"""
    comps = ink_components(page, clip, dpi)
    keep = [r for r, _ in comps if pymupdf.Rect(r).intersects(seed)]
    if not keep:
        return None
    if not wire_only:
        for _ in range(3):
            U = pymupdf.Rect(keep[0])
            for r in keep[1:]:
                U |= r
            g = pymupdf.Rect(U.x0 - 4 * PT, U.y0 - 4 * PT, U.x1 + 4 * PT, U.y1 + 4 * PT)
            add = [r for r, _ in comps
                   if r not in keep and g.contains(pymupdf.Rect(r))
                   and r.width <= 14 * PT and r.height <= 12 * PT]
            if not add:
                break
            keep += add
    B = pymupdf.Rect(keep[0])
    for r in keep[1:]:
        B |= r
    return B


def doc_measures(path):
    doc = pymupdf.open(path)
    res = []
    for pno, page in enumerate(doc, 1):
        H = page.rect.height
        cs = merge_rows(cluster(diag_items(page.get_drawings()), 8 / 25.4 * PT))
        for r, nlong in cs:
            if r.width / PT < 15 or r.height / PT < 10 or nlong < MINLONG:
                continue
            col = 1 if r.x0 < MID else 2
            cl = MARGIN if col == 1 else MARGIN + COLW + COLSEP
            ls = col_lines(page, cl)
            up = max([lr.y1 for t, lr in ls if lr.y1 <= r.y0 + 1], default=MARGIN - 1)
            dn = min([lr.y0 for t, lr in ls if lr.y0 >= r.y1 - 1], default=H - BOT + 1)
            band = pymupdf.Rect(cl + 0.4, up + 0.5, cl + COLW - 0.4, max(dn - 0.5, r.y1 + 2 * PT))
            seed = pymupdf.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1)
            B = fig_bbox(page, band, seed)
            W = fig_bbox(page, band, seed, wire_only=True)
            if B is None or W is None:
                continue
            res.append(dict(page=pno, col=col, nlong=nlong, x0=B.x0 / PT, y0=B.y0 / PT,
                            w=B.width / PT, h=B.height / PT,
                            ww=W.width / PT, wh=W.height / PT, wx0=W.x0 / PT, wy0=W.y0 / PT,
                            dev=((B.x0 + B.x1) / 2 - (cl + COLW / 2)) / PT,
                            gap_up=(B.y0 - up) / PT, gap_dn=(dn - B.y1) / PT))
    res.sort(key=lambda d: (d['page'], d['y0']))
    return res


def src_measure(name):
    """素材 standalone 整页墨 bbox＋线框 bbox（border=0pt 壳，页＝片段声明 bbox）。"""
    doc = pymupdf.open(SRC + name)
    p = doc[0]
    r = p.rect
    clip = pymupdf.Rect(r.x0 + 0.2, r.y0 + 0.2, r.x1 - 0.2, r.y1 - 0.2)
    ib = ink_bbox(p, clip)
    comps = ink_components(p, clip)
    B = pymupdf.Rect(comps[0][0])
    for q, _ in comps[1:]:
        B |= q
    return (r.width / PT, r.height / PT, (ib[2] - ib[0]) / PT, (ib[3] - ib[1]) / PT,
            B.width / PT, B.height / PT)


if __name__ == '__main__':
    dm = doc_measures(r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf')
    print('件内实测（mm，600dpi 全墨口径；带内正文行界＝行宽≥15mm）  图数', len(dm))
    for d in dm:
        print(' p{page} c{col} 斜长笔={nlong:3d}  x0={x0:7.2f} y0={y0:7.2f} 墨宽={w:6.2f} 墨高={h:6.2f} '
              '栏心偏={dev:+6.2f} 前距={gap_up:5.2f} 下距={gap_dn:5.2f}'.format(**d))
    print()
    print('同比核验（素材 standalone → 件内；预测＝素材墨尺寸 × 缩放系数）')
    for (tag, sn, wbox, frag), d in zip(MAP, dm):
        pw, ph, sw, sh, bw, bh = src_measure(sn)
        k = wbox / pw
        print(' {0:<10s} {1:<26s} 素材页 {2:6.2f}×{3:6.2f} 缩 {4:6.4f}  '
              '预测墨 {5:6.2f}×{6:6.2f} 实测墨 {7:6.2f}×{8:6.2f} Δ={9:+5.2f}/{10:+5.2f}  '
              '长宽比 素材{11:6.4f} 件内{12:6.4f} Δ={13:+.4f}'.format(

                  tag, frag, pw, ph, k, sw * k, sh * k, d['w'], d['h'],
                  d['w'] - sw * k, d['h'] - sh * k, sh / sw, d['h'] / d['w'],
                  d['h'] / d['w'] - sh / sw))