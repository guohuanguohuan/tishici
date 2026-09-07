# -*- coding: utf-8 -*-
"""
全品学练考·高中数学·选择性必修第一册(RJB) 版式参数实测（投影分析法）
------------------------------------------------------------------
口径：横 14.176 px/mm（2977px/210mm），纵 14.057 px/mm（4176px/297mm）
      pt = mm / 0.3528（1pt = 0.3528mm）
方法：灰度→阈值二值化→行/列投影→行带、栏线、悬挂缩进、题块、挖空线、
      页眉页脚、答题栏几何测量
运行：python 测量脚本.py  →  打印每页关键结果 + 跨页汇总，写 测量结果.json
页码换算：练习册 pNN ↔ 书页码 NN-5；导学案 pNN ↔ 书页码 NN+135
练习册书页码为偶数（pNN 为奇数）的页带左侧答题栏
"""
import json, os, sys, statistics
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))

W, H = 2977, 4176
PXMM_X = W / 210.0          # 14.176
PXMM_Y = H / 297.0          # 14.057
MM_PER_PT = 25.4 / 72.0     # 0.3528

def med(v):  return statistics.median(v) if v else None
def rng(v):  return (min(v), max(v)) if v else (None, None)

def load_gray(path):
    return np.asarray(Image.open(path).convert("L"))

def bands(has, min_gap=6, min_h=4):
    idx = np.flatnonzero(has)
    if idx.size == 0: return []
    out, s, p = [], int(idx[0]), int(idx[0])
    for i in idx[1:]:
        i = int(i)
        if i - p > min_gap:
            if p - s + 1 >= min_h: out.append((s, p))
            s = i
        p = i
    if p - s + 1 >= min_h: out.append((s, p))
    return out

def runs(bool_1d, min_len=1):
    idx = np.flatnonzero(bool_1d)
    if idx.size == 0: return []
    out, s, p = [], int(idx[0]), int(idx[0])
    for i in idx[1:]:
        i = int(i)
        if i - p > 1:
            if p - s + 1 >= min_len: out.append((s, p))
            s = i
        p = i
    if p - s + 1 >= min_len: out.append((s, p))
    return out

def cluster(xs, binw=4, merge=10, min_n=2):
    if not xs: return []
    xs = sorted(xs)
    groups = [[xs[0]]]
    for x in xs[1:]:
        if x - groups[-1][-1] <= binw: groups[-1].append(x)
        else: groups.append([x])
    merged = []
    for g in groups:
        if merged and g[0] - merged[-1][-1] <= merge: merged[-1].extend(g)
        else: merged.append(list(g))
    cl = [(int(np.mean(g)), len(g)) for g in merged if len(g) >= min_n]
    return sorted(cl, key=lambda t: -t[1])

# ---------------------------------------------------------------- 页面结构
def find_rule_v(G):
    B = G < 210
    colink = B[1000:3500].sum(axis=0)
    out = []
    for s, e in bands(colink > 1500, min_gap=4, min_h=1):
        if e - s + 1 <= 10:
            xs = (s + e) // 2
            out.append(dict(x=(s, e), cx=xs, wdt=e - s + 1, gray=int(np.median(G[1000:3500, xs]))))
    return out

def text_extent(G, y0=650, y1=3850, thr=160, xmin=0):
    B = G[y0:y1] < thr
    colsum = B.sum(axis=0)
    colsum[:xmin] = 0
    idx = np.flatnonzero(colsum > 2)
    return (int(idx[0]), int(idx[-1])) if idx.size else None

def line_bands(G, x0, x1, y0=250, y1=3900, thr=160, min_gap=6, min_h=5, ink=2):
    prof = (G[y0:y1, max(x0, 0):min(x1 + 1, W)] < thr).sum(axis=1)
    return [(s + y0, e + y0) for s, e in bands(prof > ink, min_gap=min_gap, min_h=min_h)]

def band_lefts(G, x0, x1, lbs, thr=160):
    out = []
    for s, e in lbs:
        seg = G[s:e + 1, max(x0, 0):x1 + 1] < thr
        cols = np.flatnonzero(seg.any(axis=0))
        out.append(int(cols[0]) + x0 if cols.size else None)
    return out

def band_rights(G, x0, x1, lbs, thr=160):
    out = []
    for s, e in lbs:
        seg = G[s:e + 1, max(x0, 0):x1 + 1] < thr
        cols = np.flatnonzero(seg.any(axis=0))
        out.append(int(cols[-1]) + x0 if cols.size else None)
    return out

def char_advance(G, x0, x1, lbs, heights, h_lo, h_hi, thr=160):
    advs = []
    for (s, e), h in zip(lbs, heights):
        if not (h_lo <= h <= h_hi) or (e - s) < 20: continue
        proj = (G[s:e + 1, x0:x1 + 1] < thr).sum(axis=0) > 0
        rs = runs(proj, min_len=8)
        for r1, r2 in zip(rs, rs[1:]):
            if 0 <= r2[0] - r1[1] <= 12:
                advs.append(r2[0] - r1[0])
    return med(advs) if advs else None

# ---------------------------------------------------------------- 页眉
def header_info(G, book):
    d = {}
    prof = (G[:700] < 160).sum(axis=1)
    d["top_ink"] = int(np.flatnonzero(prof > 3)[0]) if (prof > 3).any() else None
    scan = G[240:530, 415:2450] < 128
    for s, e in bands(scan.any(axis=1), min_gap=12, min_h=4):
        h = e - s + 1
        seg = scan[s:e + 1]
        cc = np.flatnonzero(seg.any(axis=0))
        xext = (415 + int(cc[0]), 415 + int(cc[-1]))
        dens = float(seg[:, cc[0]:cc[-1] + 1].mean())
        yext = (240 + s, 240 + e)
        if h >= 80 and dens >= 0.22:
            d["chap_title"] = dict(y=yext, h=h, x=xext, dens=round(dens, 2))
        elif 42 <= h <= 78 and dens >= 0.22 and abs((xext[0] + xext[1]) / 2 - W / 2) < 280:
            d["lesson_title"] = dict(y=yext, h=h, x=xext, dens=round(dens, 2))
    if d.get("chap_title"):
        seg = G[240:540, 40:412] < 225
        rr = np.flatnonzero(seg.any(axis=1)); cc = np.flatnonzero(seg.any(axis=0))
        if rr.size:
            d["deco"] = dict(x=(40 + int(cc[0]), 40 + int(cc[-1])),
                             y=(240 + int(rr[0]), 240 + int(rr[-1])))
        for y in range(470, 660):
            row = G[y, 100:2800] < 230
            if row.sum() > 1800:
                rr2 = runs(row, min_len=100)
                d["rule"] = dict(y=y, gray=int(np.median(G[y, 100:2800][row])),
                                 x=(100 + rr2[0][0], 100 + rr2[-1][1]),
                                 thick=sum(1 for yy in range(y - 3, y + 4)
                                           if (G[yy, 100:2800] < 230).sum() > 1800))
                break
        if book == "导学案页图":
            qy1 = d.get("rule", {}).get("y", 640) - 8
            qr = G[250:qy1, 2450:2960] < 200
            rr = np.flatnonzero(qr.sum(axis=1) > 10); cc = np.flatnonzero(qr.sum(axis=0) > 10)
            if rr.size > 40:
                d["qr"] = dict(x=(2450 + int(cc[0]), 2450 + int(cc[-1])),
                               y=(250 + int(rr[0]), 250 + int(rr[-1])))
    return d

# ---------------------------------------------------------------- 栏目花形标签
def find_labels(G, zones):
    out = []
    for zi, (zx0, zx1) in enumerate(zones):
        wl = zx0 - 15 if zi == 0 else zx0
        lim = zx0 + (25 if zi == 0 else 60)
        for (s, e) in line_bands(G, wl, zx1):
            h = e - s + 1
            if not (44 <= h <= 120) or s < 440: continue
            ls = band_lefts(G, wl, zx1, [(s, e)])[0]
            if ls is None or ls > lim: continue
            seg = G[s:e + 1, max(ls - 6, 0):min(ls + 620, zx1)] < 160
            top3 = seg[:3]
            mr_top = max([r[1] - r[0] + 1 for r in runs(top3.any(axis=0))] or [0])
            if mr_top > 22: continue
            rr = np.flatnonzero(seg.any(axis=1)); cc = np.flatnonzero(seg.any(axis=0))
            proj = seg.any(axis=0)
            rs = runs(proj, min_len=2)
            groups, cur = [], [rs[0]]
            for r in rs[1:]:
                if r[0] - cur[-1][1] <= 28: cur.append(r)
                else: groups.append(cur); cur = [r]
            groups.append(cur)
            blk = groups[0]
            bw = blk[-1][1] - blk[0][0] + 1
            if not (200 <= bw <= 400): continue
            bx0, bx1 = ls - 6 + blk[0][0], ls - 6 + blk[-1][1]
            # 灰/黑横线与行末说明（导学案）
            seg2 = G[s:min(e + 62, e + 62), zx0:zx1] < 230
            grows = [r for r in runs(seg2.any(axis=0), min_len=150) if r[0] + zx0 > bx1 + 8]
            rule = (zx0 + grows[0][0], zx0 + grows[-1][1]) if grows else None
            cap = None
            if rule:
                cseg = G[s:e + 62, rule[1] + 8:zx1] < 160
                cc2 = np.flatnonzero(cseg.any(axis=0))
                if cc2.size: cap = (rule[1] + 8 + int(cc2[0]), rule[1] + 8 + int(cc2[-1]))
            out.append(dict(zone=zi, band=(s, e), h=h, block=(bx0, bx1), bw=bx1 - bx0 + 1,
                            bh=int(rr[-1] - rr[0] + 1), rule=rule, caption=cap))
    return out

# ---------------------------------------------------------------- 挖空线
def underlines(G, zones, labels):
    lab_rows = set()
    for lb in labels:
        lab_rows.update(range(lb["band"][0] - 6, lb["band"][1] + 66))
    raw = []
    for zi, (zx0, zx1) in enumerate(zones):
        lbs = line_bands(G, zx0, zx1)
        tops = [s for s, e in lbs]
        bots = [e for s, e in lbs]
        for y in range(650, 3880):
            if y in lab_rows: continue
            for a, b in runs(G[y, max(zx0, 60):min(zx1, 2800)] < 160, min_len=140):
                L = b - a + 1
                if L > 820: continue
                xa, xb = a + max(zx0, 60), b + max(zx0, 60)
                c = (xa + xb) // 2
                if (G[max(y - 20, 0):y + 21, c] < 160).sum() > 14: continue
                up = (G[max(y - 24, 0):max(y - 8, 1), xa:xb + 1] < 160).mean()
                dn = (G[y + 8:y + 25, xa:xb + 1] < 160).mean()
                if up >= 0.05 or dn >= 0.05: continue
                # 必须落在正文行带内（行高≤95；blank 基线可略低于带底，容差 +16）
                bi = [i for i, (s2, e2) in enumerate(lbs) if s2 - 6 <= y <= e2 + 16]
                if not bi: continue
                i = bi[0]
                if bots[i] - tops[i] > 95: continue
                ok_grid = False
                if i > 0 and 55 <= tops[i] - bots[i - 1] + (bots[i - 1] - tops[i - 1]) <= 175: ok_grid = True
                if i + 1 < len(lbs) and 55 <= tops[i + 1] - bots[i] + (bots[i + 1] - tops[i + 1]) <= 175: ok_grid = True
                if not ok_grid: continue
                # 同一行内挖空线须伴随文字（左侧 420px 或右侧 120px 有墨）
                rowseg = G[tops[i]:bots[i] + 1, zx0:zx1] < 160
                leftok = rowseg[:, max(xa - 420 - zx0, 0):xa - zx0].any() if xa - 420 >= zx0 else False
                rightok = rowseg[:, xb - zx0 + 2:xb - zx0 + 122].any() if xb + 122 <= zx1 else False
                if not (leftok or rightok): continue
                raw.append((y, xa, xb, L))
    raw.sort()
    ded = []
    for u in raw:
        if any(abs(u[0] - v[0]) <= 3 and abs(u[1] - v[1]) <= 12 for v in ded): continue
        ded.append(u)
    return ded

# ---------------------------------------------------------------- 页脚
def footer_info(G):
    d = {}
    reg = G[3890:4030, :]
    fill = (reg >= 190) & (reg <= 248)
    cs = [c for c in bands(fill.sum(axis=0) > 30, min_gap=8, min_h=40) if c[1] - c[0] > 80]
    rs = [r for r in bands(fill.sum(axis=1) > 60, min_gap=8, min_h=30) if r[1] - r[0] > 40]
    if cs and rs:
        x0, x1 = cs[0]
        y0, y1 = 3890 + rs[0][0], 3890 + rs[0][1]
        inside = G[y0:y1 + 1, x0:x1 + 1]
        m = (inside >= 190) & (inside <= 248)
        d["pagenum_block"] = dict(x=(x0, x1), y=(y0, y1), w=x1 - x0 + 1, hh=y1 - y0 + 1,
                                  fill=int(np.median(inside[m])) if m.any() else None,
                                  side="right" if (x0 + x1) / 2 > W / 2 else "left")
        dg = inside < 100
        rr = np.flatnonzero(dg.any(axis=1))
        if rr.size: d["digits_h"] = int(rr[-1] - rr[0] + 1)
    B = G[3910:4000, :] < 160
    if d.get("pagenum_block"):
        bx = d["pagenum_block"]["x"]
        B[:, max(bx[0] - 8, 0):bx[1] + 8] = False
    rr = np.flatnonzero(B.any(axis=1)); cc = np.flatnonzero(B.any(axis=0))
    if rr.size:
        d["footer_text"] = dict(y=(3910 + int(rr[0]), 3910 + int(rr[-1])), h=int(rr[-1] - rr[0] + 1),
                                x=(int(cc[0]), int(cc[-1])))
    return d

# ---------------------------------------------------------------- 答题栏（练习册偶数页）
def answer_column(G):
    L = G < 225
    strip = L[250:3850, 20:340]
    vb = [20 + s for s, e in bands(strip.sum(axis=0) > 900, min_gap=4, min_h=1) if e - s + 1 <= 8]
    hb = [250 + s for s, e in bands(strip.sum(axis=1) > 150, min_gap=5, min_h=1)]
    nums = bands((G[600:3800, 195:265] < 170).sum(axis=1) > 2, min_gap=30, min_h=6)
    pits = [b - a for a, b in zip([n[0] for n in nums], [n[0] for n in nums][1:])] if len(nums) > 1 else []
    box_x = None
    for y in hb[:4]:
        rr = runs(L[y, 20:340], min_len=60)
        if rr:
            box_x = (20 + rr[0][0], 20 + rr[-1][1]); break
    return dict(vlines=vb, box_x=box_x,
                head_seps=hb[:4], row_pitch=med([b - a for a, b in zip(hb, hb[1:])]) if len(hb) > 2 else None,
                n_seps=len(hb), n_num_rows=len(nums), num_pitch=med(pits) if pits else None)

# ---------------------------------------------------------------- 主流程
def analyze(book, fname):
    path = os.path.join(BASE, book, fname)
    G = load_gray(path)
    nn = int(fname[1:3])
    even = (book == "练习册页图") and ((nn - 5) % 2 == 0)
    res = dict(book=book, page=fname, even=even)

    rules = find_rule_v(G)
    res["rule_v"] = [(r["cx"], r["wdt"], r["gray"]) for r in rules]
    ext = text_extent(G, xmin=300 if even else 0)
    res["extent"] = ext
    res["header"] = header_info(G, book)
    res["footer"] = footer_info(G)
    if not rules:
        res.update(zones=[], colstats=[], labels=[],
                   underlines=dict(n=0, lens=[], sample=[]))
        return res
    rx = rules[0]["cx"]
    x0, x1 = ext
    zones = [(x0, rx - 10), (rx + 10, x1)]
    res["zones"] = zones
    labels = find_labels(G, zones)
    res["labels"] = labels

    colstats = []
    for zi, (zx0, zx1) in enumerate(zones):
        wl = zx0 - 15 if zi == 0 else zx0
        lbs = line_bands(G, wl, zx1)
        heights = [e - s + 1 for s, e in lbs]
        tops = [s for s, e in lbs]
        pits = [b - a for a, b in zip(tops, tops[1:]) if 55 <= b - a <= 170]
        hs = [h for h in heights if 30 <= h <= 95]
        p25 = int(np.percentile(hs, 25)) if hs else 46
        ls = band_lefts(G, wl, zx1, lbs)
        rts = band_rights(G, wl, zx1, lbs)
        adv = char_advance(G, wl, zx1, lbs, heights, p25 - 3, p25 + 6)
        lab_bands = [l["band"] for l in labels if l["zone"] == zi]
        qlo = 0 if zi == 0 else 30   # zone1: 排除溢过栏线的左栏尾墨（ls-zx0≈0）
        qcand = [i for i, x in enumerate(ls)
                 if x is not None and qlo <= x - zx0 <= (25 if zi == 0 else 60)
                 and not any(lb[0] - 8 <= tops[i] <= lb[1] + 8 for lb in lab_bands)]
        qtops = [tops[i] for i in qcand]
        qpit = [b - a for a, b in zip(qtops, qtops[1:]) if 70 <= b - a <= 600]
        qblk = [tops[qcand[k]] - lbs[qcand[k - 1]][1] for k in range(1, len(qcand))
                if lbs[qcand[k - 1]][1] - lbs[qcand[k - 1]][0] + 1 <= 70]
        qblk = [g for g in qblk if 0 <= g <= 260]
        colstats.append(dict(zone=(zx0, zx1), n=len(lbs), pitch=med(pits),
                             body_h=p25, h_med=med(hs),
                             adv=adv, q_starts=len(qtops),
                             q_pitch=med(qpit) if qpit else None,
                             q_blank=med(qblk) if qblk else None,
                             left_clusters=cluster([x for x in ls if x is not None])[:4],
                             right_clusters=cluster([x for x in rts if x is not None])[:3]))
    res["colstats"] = colstats

    ul = underlines(G, zones, labels)
    res["underlines"] = dict(n=len(ul), lens=[u[3] for u in ul], sample=ul[:4])
    if even:
        res["anscol"] = answer_column(G)
    if book == "导学案页图":
        hd = res["header"]
        anchor = hd.get("lesson_title") or hd.get("chap_title")
        if anchor:
            t_bot = anchor["y"][1]
            lbs = line_bands(G, x0, x1, y0=t_bot + 10, y1=min(t_bot + 1500, 3850))
            full = []
            for s, e in lbs:
                seg = G[s:e + 1, x0:x1 + 1] < 160
                cc = np.flatnonzero(seg.any(axis=0))
                if not cc.size: continue
                lf = int(cc[0]) + x0
                if lf < 390:
                    if full: break      # 目标清单结束（回行/正文/标签行均自左缘起）
                    continue            # 清单前的【学习目标】标签等
                if lf <= 700: full.append((s, e, lf))
            if len(full) >= 2:
                hs = [e - s + 1 for s, e, _ in full]
                tp = [s for s, e, _ in full]
                lfs = [lf for _, _, lf in full]
                pits = [b - a for a, b in zip(tp, tp[1:]) if 55 <= b - a <= 170]
                hb = med([h for h in hs if 30 <= h <= 90])
                res["objectives"] = dict(n=len(full), pitch=med(pits), h=hb, ys=[s for s, e, _ in full],
                                         left=med(lfs),
                                         adv=char_advance(G, x0, x1, [(s, e) for s, e, _ in full], hs,
                                                          (hb or 44) - 4, (hb or 44) + 6))
    return res

# ---------------------------------------------------------------- 汇总
def flat(v):
    out = []
    for x in v:
        if isinstance(x, (list, tuple)): out.extend(flat(x))
        elif x is not None: out.append(x)
    return out

def summarize(allres):
    S = {}
    for book in ("练习册页图", "导学案页图"):
        rs = [r for r in allres if r["book"] == book]
        b = dict(pages=[r["page"] for r in rs])
        def P(f): return flat([f(r) for r in rs])
        b["pitch_all"] = med(P(lambda r: [c["pitch"] for c in r["colstats"]]))
        b["pitch_rng"] = rng(P(lambda r: [c["pitch"] for c in r["colstats"]]))
        b["body_h_p25"] = med(P(lambda r: [c["body_h"] for c in r["colstats"]]))
        b["adv_all"] = med(P(lambda r: [c["adv"] for c in r["colstats"]]))
        b["q_blank"] = med(P(lambda r: [c["q_blank"] for c in r["colstats"]]))
        b["rule_v"] = med(P(lambda r: [rv[0] for rv in r["rule_v"]]))
        for par, sel in (("odd", lambda r: not r["even"]), ("even", lambda r: r["even"])):
            xs0 = [r["extent"][0] for r in rs if sel(r) and r["extent"]]
            xs1 = [r["extent"][1] for r in rs if sel(r) and r["extent"]]
            b[f"x0_{par}"] = med(xs0); b[f"x1_{par}"] = med(xs1)
        b["top_ink"] = med(P(lambda r: [r["header"]["top_ink"]]))
        b["uline"] = dict(n=sum(len(r["underlines"]["lens"]) for r in rs),
                          med=med(P(lambda r: r["underlines"]["lens"])),
                          rng=rng(P(lambda r: r["underlines"]["lens"])))
        b["labels"] = [dict(page=r["page"], **l) for r in rs for l in r["labels"]]
        b["chap_h"] = med(P(lambda r: [r["header"].get("chap_title", {}).get("h")]))
        b["lesson_h"] = med(P(lambda r: [r["header"].get("lesson_title", {}).get("h")]))
        b["obj"] = dict(pitch=med(P(lambda r: [r.get("objectives", {}).get("pitch")])),
                        h=med(P(lambda r: [r.get("objectives", {}).get("h")])),
                        adv=med(P(lambda r: [r.get("objectives", {}).get("adv")])))
        if book == "练习册页图":
            ac = [r["anscol"] for r in rs if "anscol" in r and r["anscol"].get("box_x")]
            if ac:
                b["anscol"] = dict(box_x=med([a["box_x"][0] for a in ac]), box_x1=med([a["box_x"][1] for a in ac]),
                                   row_pitch=med([a["row_pitch"] for a in ac if a["row_pitch"]]),
                                   n_rows=med([a["n_num_rows"] for a in ac]),
                                   num_pitch=med([a["num_pitch"] for a in ac if a["num_pitch"]]))
        S[book] = b
    return S

PAGES = {
    "练习册页图": ["p06.png", "p07.png", "p08.png", "p09.png", "p14.png", "p15.png"],
    "导学案页图": ["p04.png", "p05.png", "p06.png", "p07.png", "p08.png", "p09.png"],
}

if __name__ == "__main__":
    allres = []
    for book, pages in PAGES.items():
        for f in pages:
            p = os.path.join(BASE, book, f)
            if not os.path.exists(p):
                print("missing", p); continue
            r = analyze(book, f)
            allres.append(r)
            hd = r["header"]
            print(f"== {book[:3]} {f} even={r['even']} rule_v={r['rule_v']} extent={r['extent']}")
            print(f"   header: top={hd['top_ink']} chap={hd.get('chap_title')} lesson={hd.get('lesson_title')} "
                  f"deco={hd.get('deco')} rule={hd.get('rule')} qr={hd.get('qr')}")
            for c in r["colstats"]:
                print(f"   zone{c['zone']} n{c['n']} pitch={c['pitch']} h25={c['body_h']} adv={c['adv']} "
                      f"q{c['q_starts']} qp={c['q_pitch']} qb={c['q_blank']}")
                print(f"      L{c['left_clusters']}  R{c['right_clusters']}")
            print(f"   labels={r['labels']}")
            u = r["underlines"]
            print(f"   uline n={u['n']} med={med(u['lens'])} rng={rng(u['lens'])} sample={u['sample']}")
            print(f"   footer={r['footer']}")
            if "anscol" in r: print(f"   anscol={r['anscol']}")
            if "objectives" in r: print(f"   objectives={r['objectives']}")
    S = summarize(allres)
    with open(os.path.join(BASE, "测量结果.json"), "w", encoding="utf-8") as fj:
        json.dump(dict(per_page=allres, summary=S), fj, ensure_ascii=False, indent=1, default=str)
    print("\n== SUMMARY ==")
    print(json.dumps(S, ensure_ascii=False, indent=1, default=str))
