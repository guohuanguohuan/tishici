# -*- coding: utf-8 -*-
"""意见31 取证：表格行高＋格内净空实测（我方 main.pdf vs 全品页图）。只读，产物全写本目录。"""
import os
import numpy as np
from PIL import Image
import fitz

OUT = os.path.dirname(os.path.abspath(__file__))
QPDIR = r'C:\提示词\工作区\全品结构提取\数学选必一\导学案页图'
PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
PX6 = 600 / 25.4
PX3 = 360 / 25.4


def max_run(v):
    d = np.diff(np.concatenate(([0], v.astype(np.int8), [0])))
    s = np.where(d == 1)[0]
    e = np.where(d == -1)[0]
    return 0 if len(s) == 0 else int((e - s).max())


def cluster1d(idx, gap):
    out, cur = [], [idx[0]]
    for v in idx[1:]:
        if v - cur[-1] <= gap:
            cur.append(v)
        else:
            out.append(cur)
            cur = [v]
    out.append(cur)
    return out


def hbands(cov_rows, thr):
    idx = np.where(cov_rows > thr)[0]
    if len(idx) == 0:
        return []
    out, s, p = [], idx[0], idx[0]
    for v in idx[1:]:
        if v - p > 1:
            out.append((s, p))
            s = v
        p = v
    out.append((s, p))
    return out


def text_bands(cell_dark):
    ink = cell_dark.any(axis=1)
    idx = np.where(ink)[0]
    if len(idx) == 0:
        return []
    out, s, p = [], idx[0], idx[0]
    for v in idx[1:]:
        if v - p > 2:
            out.append((s, p))
            s = v
        p = v
    out.append((s, p))
    return out


def vdilate(mask, k=2):
    """竖向膨胀 k px：桥接竖向断线，不影响横向覆盖"""
    v = mask
    for _ in range(k):
        v = v | np.roll(v, 1, axis=0) | np.roll(v, -1, axis=0)
    return v


def analyze_page(arr, PXMM, tag, thr_rule=170, thr_text=110, cov_thr=0.85, save_prefix=None, bridge_gap=0):
    """返回 [(table dict)]；table: x0,x1, rules=[(s,e)...], rows=[{pitch,pads...}]"""
    H, W = arr.shape
    dark = arr < thr_rule
    darkv = vdilate(dark, bridge_gap) if bridge_gap else dark
    run = np.array([max_run(darkv[:, x]) for x in range(W)])
    vx = np.where((run > 15 * PXMM) & (run < 160 * PXMM))[0]
    if len(vx) < 2:
        print(f'{tag}: 无竖线（无表）')
        return []
    vb = [int(np.mean(c)) for c in cluster1d(vx, 3)]
    # 栏间竖线（run>170mm）定位页中缝，分组不得跨缝
    sep_candidates = np.where(run > 170 * PXMM)[0]
    sep_x = int(np.mean(sep_candidates)) if len(sep_candidates) else -1
    tables, used = [], set()
    for i in range(len(vb) - 1):
        if i in used:
            continue
        grp, j = [vb[i]], i
        while j + 1 < len(vb) and vb[j + 1] - vb[j] < 45 * PXMM:
            if sep_x > 0 and vb[j] < sep_x <= vb[j + 1]:
                break
            j += 1
            grp.append(vb[j])
            used.add(j)
        used.add(i)
        if len(grp) >= 3:
            tables.append(grp)
    results = []
    for ti, grp in enumerate(tables):
        x0, x1 = grp[0], grp[-1]
        cov = darkv[:, x0 + 4:x1 - 4].sum(axis=1) / (x1 - x0 - 8)
        rbs = hbands(cov, cov_thr)
        if len(rbs) < 3:
            continue
        # 带缘回精：在 raw（未膨胀）覆盖上重找每条带的真边界
        rawcov = dark[:, x0 + 4:x1 - 4].sum(axis=1) / (x1 - x0 - 8)
        ref = []
        for s, e in rbs:
            lo, hi = max(0, s - 4), min(H - 1, e + 4)
            idx = np.where(rawcov[lo:hi + 1] > 0.5)[0]
            if len(idx):
                ref.append((lo + idx[0], lo + idx[-1]))
            else:
                ref.append((s, e))
        rbs = ref
        # 连续表体段（行高 < 60mm）
        segs, cur = [], [rbs[0]]
        for b in rbs[1:]:
            if b[0] - cur[-1][1] < 60 * PXMM:
                cur.append(b)
            else:
                segs.append(cur)
                cur = [b]
        segs.append(cur)
        segs = [sg for sg in segs if len(sg) >= 3]
        for si, seg in enumerate(segs):
            th = [(e - s + 1) / PXMM for s, e in seg]
            pitches = [(seg[k + 1][0] - seg[k][0]) / PXMM for k in range(len(seg) - 1)]
            print(f'\n== {tag} 表{ti+1}.{si+1}: x=[{x0},{x1}] y=[{seg[0][0]},{seg[-1][1]}] '
                  f'w={(x1-x0)/PXMM:.2f}mm 横线数={len(seg)} '
                  f'线厚(mm)={[round(t,2) for t in th]}')
            print(f'   行距(rule顶-顶, mm)={[round(p,2) for p in pitches]}')
            rows = []
            for ri in range(len(seg) - 1):
                (as_, ae), (bs, be) = seg[ri], seg[ri + 1]
                pitch = (bs - as_) / PXMM
                cells = []
                for ci in range(len(grp) - 1):
                    cx0, cx1 = grp[ci] + 4, grp[ci + 1] - 4
                    cell = arr[ae + 2:bs - 1, cx0:cx1]  # 规则带外缘内缩2px 防 AA
                    cdark = cell < thr_text
                    if cdark.sum() < 15:
                        cells.append(None)
                        continue
                    ys, xs = np.where(cdark)
                    padT = (ys.min() + 2) / PXMM          # 从上规则带外缘起算
                    padB = ((bs - 1 - ae - 1) - ys.max() + 1) / PXMM
                    tb = text_bands(cdark)
                    lead = [(tb[k + 1][0] - tb[k][0]) / PXMM for k in range(len(tb) - 1)]
                    cells.append(dict(padT=padT, padB=padB, nlines=len(tb),
                                      leading=[round(l, 2) for l in lead],
                                      texth=(tb[-1][1] - tb[0][0] + 1) / PXMM))
                rows.append((pitch, cells))
                cs = ' | '.join('空' if c is None else
                                f"T{c['padT']:.2f}/B{c['padB']:.2f}/{c['nlines']}行"
                                + (f'/行距{c["leading"]}' if c['leading'] else '')
                                for c in cells)
                print(f'   r{ri} pitch={pitch:.2f}mm: {cs}')
            results.append(dict(tag=tag, x0=x0, x1=x1, seg=seg, rows=rows,
                                ruleth=th, pitches=pitches))
            if save_prefix:
                Image.fromarray(arr[max(0, seg[0][0] - 8):seg[-1][1] + 8,
                                    max(0, x0 - 8):x1 + 8]).save(
                    f'{save_prefix}_t{ti+1}_{si+1}.png')
    return results


def main():
    rep = []
    # ---- 我方：600dpi 渲染 p1–p3 ----
    doc = fitz.open(PDF)
    for pno in range(3):
        pix = doc[pno].get_pixmap(dpi=600, colorspace=fitz.csGRAY)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        Image.fromarray(arr).save(os.path.join(OUT, f'_us_p{pno+1}_600.png'))
        r = analyze_page(arr, PX6, f'我方p{pno+1}',
                         save_prefix=os.path.join(OUT, f'_us_p{pno+1}'))
        rep += r
    # ---- 全品：360dpi 扫描页全部 19 页 ----
    for n in range(1, 20):
        p = os.path.join(QPDIR, f'p{n:02d}.png')
        arr = np.asarray(Image.open(p).convert('L'))
        r = analyze_page(arr, PX3, f'全品p{n:02d}')
        if not r:
            r = analyze_page(arr, PX3, f'全品p{n:02d}(桥断线)', bridge_gap=3)
        rep += r
    print('\n---- 汇总：单行格判定（≤2 文本行且行距空档大） ----')
    for t in rep:
        singles = [(p, c) for p, c in t['rows']
                   if all(cc is None or cc['nlines'] == 1 for cc in c)]
        if singles:
            ts = [cc['padT'] for p, c in singles for cc in c if cc]
            bs = [cc['padB'] for p, c in singles for cc in c if cc]
            ps = [p for p, c in singles]
            print(f"{t['tag']} 表x[{t['x0']},{t['x1']}]: 单行行数={len(singles)} "
                  f"pitch中位={np.median(ps):.2f} padT中位={np.median(ts):.2f} padB中位={np.median(bs):.2f}")


if __name__ == '__main__':
    main()
