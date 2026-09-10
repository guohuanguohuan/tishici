# -*- coding: utf-8 -*-
"""探针：用「线宽实测比」独立定件内实际缩放比 s_件（与字体无关），检验 g5 残差是否归零。"""
import sys, importlib.util, collections
sys.stdout.reconfigure(encoding='utf-8')
import pymupdf
def load(alias, path):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
aw = load('aw', '权威实测.py')
PT = aw.PT
doc = pymupdf.open(aw.MAIN)
cand = []
for pno in range(1, doc.page_count + 1):
    stk = aw.strokes(doc[pno - 1])
    for c in aw.clusters(stk):
        cand.append((pno, doc[pno - 1], stk, c))
cand.sort(key=lambda z: (z[0], z[3][0].y0))

def widths(stk, idx):
    """按线宽(含无描边=0.4默认)统计笔画对象数；返回 {round(w,3): count}"""
    d = collections.Counter()
    for i in idx:
        w = stk[i].get('width')
        w = 0.4 if w is None else float(w)
        d[round(w, 3)] += 1
    return d

for i, (tag, sn, wbox, frag, at) in enumerate(aw.MAP):
    pno, page, stk, clus = cand[i]
    r = clus[0]
    near = pymupdf.Rect(r.x0 - .3*PT, r.y0 - .3*PT, r.x1 + .3*PT, r.y1 + .3*PT)
    col, cl = (1, aw.MARGIN) if r.x0 < aw.MID else (2, aw.MARGIN + aw.COLW + aw.COLSEP)
    idx = [j for j, s in enumerate(stk) if near.intersects(s['rect']) and s['rect'].x0 >= cl and s['rect'].x1 <= cl + aw.COLW]
    sd = pymupdf.open(aw.SRC + sn); sp = sd[0]
    sstk = aw.strokes(sp)
    scs = aw.clusters(sstk)
    sr = pymupdf.Rect(scs[0][0])
    for c in scs[1:]:
        sr |= c[0]
    snear = pymupdf.Rect(sr.x0 - .3*PT, sr.y0 - .3*PT, sr.x1 + .3*PT, sr.y1 + .3*PT)
    sidx = [j for j, s in enumerate(sstk) if snear.intersects(s['rect'])]
    wd, swd = widths(stk, idx), widths(sstk, sidx)
    pairs = sorted(set(wd) & set(swd))
    ratio = [round(w / v, 4) for w, v in zip(sorted(wd, reverse=True), sorted(swd, reverse=True))]
    print('%-9s 件内宽%s ｜ 素材宽%s ｜ 逐档比(降序对位) %s ｜ 页宽折算k=%.4f' % (
        tag, dict(sorted(wd.items(), reverse=True)), dict(sorted(swd.items(), reverse=True)), ratio, wbox / (sp.rect.width/PT)))
