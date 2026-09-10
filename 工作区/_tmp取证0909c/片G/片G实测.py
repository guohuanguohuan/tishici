# -*- coding: utf-8 -*-
r"""片G 0910 六图下置·终版实测（取证表 ＋ 断言适配口径来源）。

定位：页内「非轴对齐矢量墨」（斜线/曲线/小填充块）聚簇并合（同 y 带 x 隙 ≤20mm → 三联三子图成一簇），
      簇内「斜长笔」（非轴对齐且跨度 ≥5mm）≥3 方算图——真图 ≥5；表线/正文/花形/√× 自绘＝0～2。
测量：图带＝同栏内「行宽 ≥15mm」的正文行之间（图内标签系窄块，天然不作边界）；
      带内 600dpi 二值墨 → 8 邻接连通域 →
        线框＝与矢量种子簇相交的连通域之并（件内/素材同法，可比对）；
        全墨＝线框 ∪ 外扩 4mm 内且 ≤14×12mm 的连通域（＝图内标签）；
      前距＝线框顶 − 上邻正文行底；下距＝下邻正文行顶 − 线框底；
      正文相交＝与全墨矩形（外扩 0.5pt）相交的正文行数（零侵入门，须 0）。
核验：素材 standalone 同法测（整页即图）→ 按 \\resizebox 缩放系数折算 → 与件内出 Δ。
"""
import pymupdf

PT = 72 / 25.4
MARGIN = 17.2 * PT
COLSEP = 7.6 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2      # 84.0mm
MID = MARGIN + COLW + COLSEP / 2
BOT = 20 * PT
DPI = 600
MINLONG = 3
BODYLINE_W = 15.0 * PT
SRC = 'C:/提示词/工作区/_tmp片G素材/'
MAIN = 'C:/提示词/工作区/字替对照-0909/variantF/main.pdf'
MAP = [   # (标签, 素材 standalone PDF, \resizebox 置宽 mm, 片段)
    ('g6 三联', 'sub3_投影三联-纯tikz体检.pdf', 84.0, 'figs/g6-triple.tikz'),
    ('g1 棱柱', 'img1_tikz.pdf', 41.1, 'figs/g1-prism.tikz'),
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
                xs = [q.x for q in ps]
                ys = [q.y for q in ps]
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
            a = pymupdf.Rect(rs[i])
            a.x0 -= gap; a.y0 -= gap; a.x1 += gap; a.y1 += gap
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


def ink_components(page, clip, dpi=DPI, thr=200, dilate=2):
    """8 邻接连通域。连通判定用膨胀后掩膜（跨 2px≈0.085mm 触缝，收齐独立路径画的棱），
       但 bbox 取未膨胀掩膜真墨——膨胀只为并域，不放大尺寸。"""
    import numpy as np
    from scipy import ndimage
    pix = page.get_pixmap(dpi=dpi, clip=clip)
    w, h, n, s = pix.width, pix.height, pix.n, pix.samples
    a = np.frombuffer(s, dtype=np.uint8).reshape(h, w, n)[:, :, :3].mean(axis=2)
    mask = a < thr
    st = np.ones((3, 3), bool)
    lab, cnt = ndimage.label(
        ndimage.binary_dilation(mask, st, iterations=dilate) if dilate else mask, structure=st)
    k = 72.0 / dpi
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        sub = mask[sl] & (lab[sl] == i)
        ys, xs = np.nonzero(sub)
        if len(xs) == 0:
            continue
        x0, x1 = xs.min(), xs.max() + 1
        y0, y1 = ys.min(), ys.max() + 1
        out.append(pymupdf.Rect(clip.x0 + (sl[1].start + x0) * k, clip.y0 + (sl[0].start + y0) * k,
                                clip.x0 + (sl[1].start + x1) * k, clip.y0 + (sl[0].start + y1) * k))
    return out


def bboxes(comps, seed=None, with_labels=True, body=None, grow=8.0):
    """seed 连通域之并（线框）；with_labels 再纳入口标签块：距并集 ≤grow mm、尺寸 ≤14×12mm、
       且不完全落在任一正文行框内（排除邻行文字被误收）。"""
    body = body or []
    if seed is None:
        keep = list(comps)
    else:
        keep = [r for r in comps if r.intersects(seed)]
    if not keep:
        return None
    if with_labels:
        for _ in range(4):
            U = keep[0]
            for r in keep[1:]:
                U |= r
            g = pymupdf.Rect(U.x0 - grow * PT, U.y0 - grow * PT, U.x1 + grow * PT, U.y1 + grow * PT)
            add = [r for r in comps
                   if r not in keep and g.contains(r)
                   and r.width <= 14 * PT and r.height <= 12 * PT
                   and not any(br.contains(r) for br in body)]
            if not add:
                break
            keep += add
    B = keep[0]
    for r in keep[1:]:
        B |= r
    return B


def col_lines(page, cl):
    ls = []
    for b in page.get_text('dict')['blocks']:
        for ln in b.get('lines', []):
            r = pymupdf.Rect(ln['bbox'])
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t and r.width >= BODYLINE_W and cl - 2 <= (r.x0 + r.x1) / 2 <= cl + COLW + 2:
                ls.append((t, r))
    return ls


def measure_doc(path):
    doc = pymupdf.open(path)
    res = []
    for pno, page in enumerate(doc, 1):
        H = page.rect.height
        for r, nlong in merge_rows(cluster(diag_items(page.get_drawings()), 8 / 25.4 * PT)):
            if r.width / PT < 15 or r.height / PT < 10 or nlong < MINLONG:
                continue
            col = 1 if r.x0 < MID else 2
            cl = MARGIN if col == 1 else MARGIN + COLW + COLSEP
            # 一遍：宽带（种子外扩 14mm）内取图墨（种子连通域 ∪ 4mm 内小块＝图内标签）
            band = pymupdf.Rect(cl + 0.4, max(MARGIN - 2, r.y0 - 14 * PT),
                                cl + COLW - 0.4, min(H - BOT + 2, r.y1 + 14 * PT))
            comps = ink_components(page, band)
            seed = pymupdf.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1)
            wide = [lr for t, lr in col_lines(page, cl)]
            full = bboxes(comps, seed, body=wide)
            wire = bboxes(comps, seed, with_labels=False)
            if full is None or wire is None:
                continue
            # 二遍：邻正文行＝同栏宽行（≥15mm）且与图墨矩形（外扩 0.3mm）不相交者——
            #        图顶/底标签行（如 D₁ B₁ C₁ 同行）已被图墨矩形覆盖，天然不作边界
            g = pymupdf.Rect(full.x0 - 0.3, full.y0 - 0.3, full.x1 + 0.3, full.y1 + 0.3)
            ls = col_lines(page, cl)
            out = [(t, lr) for t, lr in ls if not lr.intersects(g)]
            up = max([lr.y1 for t, lr in out if lr.y1 <= full.y0], default=MARGIN - 1)
            dn = min([lr.y0 for t, lr in out if lr.y0 >= full.y1], default=H - BOT + 1)
            hits = len(ls) - len(out)
            res.append(dict(page=pno, col=col, nlong=nlong,
                            x0=full.x0 / PT, y0=full.y0 / PT,
                            fw=full.width / PT, fh=full.height / PT,
                            ww=wire.width / PT, wh=wire.height / PT,
                            dev=((full.x0 + full.x1) / 2 - (cl + COLW / 2)) / PT,
                            gap_up=(full.y0 - up) / PT, gap_dn=(dn - full.y1) / PT, hits=hits))
    res.sort(key=lambda d: (d['page'], d['y0']))
    return res


def measure_src(name, wbox):
    """素材 standalone 同法测：同一套「矢量种子＋连通域＋4mm 标签」口径，件内/素材才可比。"""
    doc = pymupdf.open(SRC + name)
    p = doc[0]
    r = p.rect
    clip = pymupdf.Rect(r.x0 + 0.2, r.y0 + 0.2, r.x1 - 0.2, r.y1 - 0.2)
    comps = ink_components(p, clip)
    cs = merge_rows(cluster(diag_items(p.get_drawings()), 8 / 25.4 * PT))
    cs = [c for c in cs if c[0].width / PT >= 15 and c[0].height / PT >= 10 and c[1] >= MINLONG]
    assert cs, name + ' 素材无种子簇'
    seed = cs[0][0]
    for extra, _n in cs[1:]:
        seed |= extra
    seed = pymupdf.Rect(seed.x0 - 1, seed.y0 - 1, seed.x1 + 1, seed.y1 + 1)
    return dict(pw=r.width / PT, ph=r.height / PT,
                fw=bboxes(comps, seed).width / PT, fh=bboxes(comps, seed).height / PT,
                ww=bboxes(comps, seed, with_labels=False).width / PT,
                wh=bboxes(comps, seed, with_labels=False).height / PT,
                k=wbox / (r.width / PT))


if __name__ == '__main__':
    dm = measure_doc(MAIN)
    print('件内实测（mm；600dpi 连通域口径） 图数', len(dm))
    print(' 页 栏 斜长笔  左缘x0   顶y0    全墨宽×高     线框宽×高    栏心偏   前距   下距  正文相交')
    for d in dm:
        print(' p{page} c{col}  {nlong:3d}  {x0:7.2f} {y0:7.2f}  {fw:6.2f}×{fh:6.2f}  {ww:6.2f}×{wh:6.2f}  '
              '{dev:+6.2f} {gap_up:5.2f} {gap_dn:5.2f}   {hits}'.format(**d))
    print()
    print('同比核验（素材 standalone 同法种子口径 ×缩放系数 → 件内）')
    for (tag, sn, wbox, frag), d in zip(MAP, dm):
        m = measure_src(sn, wbox)
        k = m['k']
        print(' {0:<9s} {1:<24s} 素材页 {2:6.2f}×{3:6.2f} 缩 {4:6.4f}  '
              '全墨 预测{5:6.2f}×{6:6.2f} 实测{7:6.2f}×{8:6.2f} Δ{9:+5.2f}/{10:+5.2f}  '
              '线框 预测{11:6.2f}×{12:6.2f} 实测{13:6.2f}×{14:6.2f} Δ{15:+5.2f}/{16:+5.2f}'.format(
                  tag, frag, m['pw'], m['ph'], k,
                  m['fw'] * k, m['fh'] * k, d['fw'], d['fh'],
                  d['fw'] - m['fw'] * k, d['fh'] - m['fh'] * k,
                  m['ww'] * k, m['wh'] * k, d['ww'], d['wh'],
                  d['ww'] - m['ww'] * k, d['wh'] - m['wh'] * k))
