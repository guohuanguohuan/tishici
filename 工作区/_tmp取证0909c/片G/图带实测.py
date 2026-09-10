"""片G 0910 六图下置·行墨洪水测量（取证＋断言共用口径 v3）。

方法：
 1) 种子＝页内「非轴对齐矢量墨」聚簇（斜线/曲线），并要求簇内「斜长笔」（跨度≥5mm）≥3——
    真图 ≥5；表内向量箭头、花形装饰、√× 自绘＝0，判弃。
 2) 图带＝在该簇所在栏内，以 600dpi 逐行扫描墨迹，从簇占据的行区间向上下做洪水扩展：
    凡「距最近墨行 ≤1mm」的行继续纳入，遇连续空白 >1mm 即止——图内标签（TikZ \node 出真文字，
    会破坏「文字带边界」判据）因与线框间隙 <1mm 自动纳入；正文行因与图有 2.3mm/0.4mm 级
    墨缝自动排除。
 3) 实测＝图带内 600dpi 全墨 bbox → 墨宽/墨高/左右缘/栏心偏差；前距＝上邻正文行底→图墨顶；
    下距＝图墨底→下邻正文行顶（正文行＝与本图墨矩形无纵向交叠者）。
 4) 与素材 standalone PDF 用同一口径测得的 (墨宽,墨高) 比对：比值应＝\resizebox 缩放系数
    W目标／素材页宽（同比不失真核验）。
"""
import sys
import pymupdf

PT = 72 / 25.4
MARGIN = 17.2 * PT
COLSEP = 7.6 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
BOT = 20 * PT
DPI = 600
PXMM = DPI / 25.4
MINLONG = 3
FLOOD_GAP = int(round(1.0 * PXMM))     # 洪水可跨的最大空白（像素）


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


def rowmask(page, clip, dpi=DPI, thr=200):
    """返回 (每行最左/最右墨像素数组, 像素→pt 系数)；无墨行为 None。"""
    pix = page.get_pixmap(dpi=dpi, clip=clip)
    s, w, h, n = pix.samples, pix.width, pix.height, pix.n
    rows = []
    for y in range(h):
        base = y * w * n
        mn, mx = -1, -1
        for x in range(w):
            off = base + x * n
            if (s[off] + s[off + 1] + s[off + 2]) / 3 < thr:
                if mn < 0:
                    mn = x
                mx = x
        rows.append(None if mn < 0 else (mn, mx))
    return rows, w, h, 72.0 / dpi


def flood_band(rows, r0, r1):
    """自 [r0,r1] 行区间向上下洪水扩展（空白 ≤FLOOD_GAP 行继续）。"""
    lo, hi = r0, r1
    # 向下
    y = hi + 1
    gap = 0
    while y < len(rows) and gap <= FLOOD_GAP:
        if rows[y]:
            hi = y; gap = 0
        else:
            gap += 1
        y += 1
    # 向上
    y = lo - 1
    gap = 0
    while y >= 0 and gap <= FLOOD_GAP:
        if rows[y]:
            lo = y; gap = 0
        else:
            gap += 1
        y -= 1
    return lo, hi


def text_lines(page, cl):
    ls = []
    for b in page.get_text('dict')['blocks']:
        for ln in b.get('lines', []):
            r = pymupdf.Rect(ln['bbox'])
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t and r.width > 0.5 and cl - 2 <= (r.x0 + r.x1) / 2 <= cl + COLW + 2:
                ls.append((t, r))
    return ls


def measure(path, seeds=None, colw=None, margin=0.0, verbose=True, label=''):
    """seeds=None → 主件口径（栏带＝MARGIN/COLW）；否则按单图 PDF 整页测（margin=0, colw=页宽）。"""
    doc = pymupdf.open(path)
    CW = colw or COLW
    MG = margin if seeds is not None else MARGIN
    rows_out = []
    for pno, page in enumerate(doc, 1):
        H = page.rect.height
        cs = merge_rows(cluster(diag_items(page.get_drawings()), 8 / 25.4 * PT))
        for r, nlong in cs:
            if r.width / PT < 15 or r.height / PT < 10 or nlong < MINLONG:
                continue
            if seeds is None:
                col = 1 if r.x0 < MID else 2
                cl = MARGIN if col == 1 else MARGIN + COLW + COLSEP
            else:
                col, cl = 0, 0.0
            clip = pymupdf.Rect(cl, max(MG - 2, r.y0 - 12 * PT), cl + CW, min(H - MG + 2, r.y1 + 12 * PT))
            rows, w, h, k = rowmask(page, clip)
            sr0 = int((r.y0 - clip.y0) / k)
            sr1 = int((r.y1 - clip.y0) / k)
            sr0 = max(0, min(h - 1, sr0)); sr1 = max(0, min(h - 1, sr1))
            lo, hi = flood_band(rows, sr0, sr1)
            minx = min(rows[y][0] for y in range(lo, hi + 1) if rows[y])
            maxx = max(rows[y][1] for y in range(lo, hi + 1) if rows[y])
            bx0, bx1 = clip.x0 + minx * k, clip.x0 + (maxx + 1) * k
            by0, by1 = clip.y0 + lo * k, clip.y0 + (hi + 1) * k
            # 正文行（与本图墨矩形纵向无交叠）→ 前/下距
            ls = text_lines(page, cl)
            up = max([lr.y1 for t, lr in ls if lr.y1 <= by0 + 0.5 and lr.y1 > MG - 4], default=MG)
            dn = min([lr.y0 for t, lr in ls if lr.y0 >= by1 - 0.5 and lr.y0 < H - MG + 4], default=H - MG)
            rows_out.append(dict(page=pno, col=col, nlong=nlong,
                                 x0=bx0 / PT, y0=by0 / PT, w=(bx1 - bx0) / PT, h=(by1 - by0) / PT,
                                 dev=((bx0 + bx1) / 2 - (cl + CW / 2)) / PT,
                                 gap_up=(by0 - up) / PT, gap_dn=(dn - by1) / PT,
                                 band=(by1 - by0) / PT))
    rows_out.sort(key=lambda d: (d['page'], d['y0']))
    if verbose:
        print(label, 'pages', doc.page_count, '（mm，600dpi 行墨洪水口径；斜长笔＝非轴对齐≥5mm 笔画数）')
        for d in rows_out:
            print(' p{page} c{col} 斜长笔={nlong:3d} x0={x0:7.2f} y0={y0:7.2f} 墨宽={w:6.2f} 墨高={h:6.2f} '
                  '栏心偏={dev:+6.2f} 前距={gap_up:5.2f} 下距={gap_dn:5.2f}'.format(**d))
        print('图数', len(rows_out))
    return rows_out


if __name__ == '__main__':
    measure(sys.argv[1] if len(sys.argv) > 1 else r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf')
