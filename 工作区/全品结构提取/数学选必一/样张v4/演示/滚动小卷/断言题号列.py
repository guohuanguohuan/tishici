# -*- coding: utf-8 -*-
r"""题号列恒空断言（演示波④滚动小卷版）：承 样张v4/测评卷/断言题号列.py 拷贝改造，差异逐条登记：
  · 路径改 演示/滚动小卷；
  · 图预期 2（位图）：image4.png（题6 二面角，承测评卷提取件）＋gundong_paliujmian.png
    （题13 平行六面体，自讲练件（上）docx rId13 新提取）；TikZ 矢量 1：题9 直三棱柱
    （承测评卷 Q6 重绘代码）——棱边簇排除逻辑同测评卷（≥3 条邻近竖直细线整簇豁免）；
  · 表线预期 0（本卷无表格；直三棱柱竖棱 3 条成簇豁免，孤立竖细线预期不出现）；
  · 【答案】行预期 0（滚动小卷同测评卷口径：答案与解析另起页集中，正文无题后答案行）；
  · 答案页条目预期 14（题1–14，每题一条 \daan 条目）。
预期：位图 2＋TikZ 棱边簇、表线 0、【答案】行 0、条目 14，违规 0。"""
import re
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\演示\滚动小卷"
PT = 72 / 25.4
MARGIN = 15 * PT
COLSEP = 8 * PT
COLW = (841.89 - 2 * MARGIN - 2 * COLSEP) / 3
COLL = (MARGIN, MARGIN + COLW + COLSEP, MARGIN + 2 * (COLW + COLSEP))
INDENT = 7 * PT

def col_left(x):
    idx = int((x - MARGIN + 0.5) // (COLW + COLSEP))
    idx = max(0, min(2, idx))
    return COLL[idx]

def th(x0):
    return col_left(x0) + INDENT - 0.5

def ink_left(page, bb, dpi=300):
    cl = col_left(bb[0])
    clip = pymupdf.Rect(cl + 0.5, bb[1] - 0.5, cl + INDENT + 8, bb[3] + 0.5)
    pix = page.get_pixmap(dpi=dpi, clip=clip)
    w, h, n = pix.width, pix.height, pix.n
    s = pix.samples
    for x in range(w):
        for y in range(h):
            off = (y * w + x) * n
            if (s[off] + s[off + 1] + s[off + 2]) / 3 < 128:
                return clip.x0 + x / (dpi / 72.0)
    return 1e9

doc = pymupdf.open(BASE + r"\main.pdf")
ans_start = None
for pno, page in enumerate(doc, 1):
    if '参考答案与解析' in page.get_text():
        ans_start = pno
        break
print(f'答案页起始于 p{ans_start}')

tot_fig = tot_rule = tot_clus = tot_ans = tot_item = tot_cont = tot_viol = 0
for pno, page in enumerate(doc, 1):
    figs = []
    for img in page.get_images(full=True):
        figs += page.get_image_rects(img[0])
    fig_viol = [(r, th(r.x0)) for r in figs if r.x0 < th(r.x0) - 1e-6]

    cands = []
    for d in page.get_drawings():
        r = d['rect']
        if not (r.width <= 4.5 and r.height >= 4.0):
            continue
        cands.append(r)
    excluded = set()
    for i, ri in enumerate(cands):
        if i in excluded:
            continue
        grp = [i]
        for j, rj in enumerate(cands):
            if j <= i or j in excluded:
                continue
            if abs(rj.x0 - ri.x0) < 25 * PT and not (rj.y1 < ri.y0 - 1 or rj.y0 > ri.y1 + 1):
                grp.append(j)
        if len(grp) >= 3:
            excluded.update(grp)
    rules = [r for k, r in enumerate(cands) if k not in excluded]
    viol_r = [(r, th(r.x0)) for r in rules if r.x0 < th(r.x0) - 1e-6]

    ans = viol_a = 0
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            txt = ''.join(sp['text'] for sp in ln['spans']).strip()
            if not txt.startswith('【答案】'):
                continue
            ans += 1
            ink = ink_left(page, ln['bbox'])
            if ink < th(ln['bbox'][0]) - 0.5:
                viol_a += 1
                print(f'   违规答案行 墨迹 x0={ink:.2f} < {th(ln["bbox"][0]):.2f} y={ln["bbox"][1]:.1f}')

    viol_i = viol_c = 0
    n_item = n_cont = 0
    if ans_start and pno >= ans_start:
        for blk in page.get_text('dict')['blocks']:
            for ln in blk.get('lines', []):
                txt = ''.join(sp['text'] for sp in ln['spans']).strip()
                if not txt:
                    continue
                x0 = ln['bbox'][0]
                if re.match(r'^\d{1,2}．', txt):
                    cl = col_left(x0)
                    if cl - 2.0 <= x0 <= cl + 25.0:
                        n_item += 1
                        continue
                    ink = ink_left(page, ln['bbox'])
                    if x0 < cl - 2.0 and ink < cl - 0.5:
                        n_item += 1
                        viol_i += 1
                        print(f'   违规条目首行 x0={x0:.2f} ink={ink:.2f} < 栏左 {cl:.2f} p{pno} y={ln["bbox"][1]:.1f} 「{txt[:16]}」')
                    elif x0 > cl + 25.0 and ink <= cl + 2.0:
                        n_item += 1
                        viol_i += 1
                        print(f'   违规条目首行 x0={x0:.2f} 题号带内有墨 p{pno} y={ln["bbox"][1]:.1f} 「{txt[:16]}」')
                else:
                    n_cont += 1
                    if x0 < th(x0) - 0.5:
                        if re.search(r'[\u4e00-\u9fff]', txt):
                            ink = ink_left(page, ln['bbox'])
                            if ink < th(x0) - 0.5:
                                viol_c += 1
                                print(f'   违规续行 x0={x0:.2f} ink={ink:.2f} < {th(x0):.2f} p{pno} y={ln["bbox"][1]:.1f} 「{txt[:16]}」')

    nv = len(fig_viol) + len(viol_r) + viol_a + viol_i + viol_c
    tot_fig += len(figs); tot_rule += len(rules); tot_clus += len(excluded)
    tot_ans += ans
    tot_item += n_item; tot_cont += n_cont; tot_viol += nv
    print(f'p{pno} {"OK" if nv == 0 else "!!"} 图 {len(figs)} | 竖细线 {len(cands)}（题图棱边簇排除 {len(excluded)}）'
          f' | 表线 {len(rules)} | 答案行 {ans} | 答案页条目 {n_item}/续行 {n_cont} | 违规 {nv}')
    for r, t in fig_viol:
        print(f'   违规图 x0={r.x0:.2f} < {t:.2f} y={r.y0:.1f}')
    for r, t in viol_r:
        print(f'   违规表线 x0={r.x0:.2f} < {t:.2f} y={r.y0:.1f}~{r.y1:.1f}')

print(f'—— 合计：位图 {tot_fig}、表线 {tot_rule}（TikZ 棱边簇排除 {tot_clus}）、【答案】行 {tot_ans}、'
      f'答案页条目 {tot_item}/续行 {tot_cont}，违规 {tot_viol}（必须=0）；'
      f'预期 位图 2＋TikZ 棱边簇、表线 0、【答案】行 0、条目 14')
ok = tot_viol == 0 and tot_fig == 2 and tot_rule == 0 and tot_ans == 0 and tot_item == 14
print('断言结果：', '通过' if ok else '未通过')
raise SystemExit(0 if ok else 1)
