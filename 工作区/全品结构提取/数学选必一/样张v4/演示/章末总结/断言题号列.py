# -*- coding: utf-8 -*-
r"""题号列恒空断言（演示波④章末总结版）：承 演示/滚动小卷/断言题号列.py 拷贝改造，差异逐条登记：
  · 路径改 演示/章末总结；版式改 A4 竖放双栏（MARGIN 15mm、栏缝 7.5mm、
    COLW=(595.276−2×42.52−21.26)/2≈244.49pt）——滚动小卷为横放三栏；
  · 位图预期 2：image3.png（题型一例1 正方体，承测评卷提取件）＋zhangmo_jiejingti.png
    （题型二变式1 平行六面体，讲练件（下）docx rId15 提取）；无 TikZ；
  · 【答案】行预期 4（题型一例1／变式1＋题型二例1／变式1，题后紧跟口径＝拍板12 同构）；
  · 例/变式条目预期 4（例1×2＋变式1×2，行首「例1」「变式1」在栏左＝块首惯用位）；
  · 表线预期 0（本件无表格；\kongbai／\ansul 下划线为横细线不入竖细线候选，棱边簇豁免逻辑保留）;
  · 本件无答案页（答案题后紧跟），故滚动小卷的「答案页条目/续行」分页门取消，续行检查全页执行：
    栏左 ±2pt 内的行＝块首行（花形行、◆题型标题、例/变式题号、【类型总述】标签等惯用位）豁免；
    花形行 tcbox 内文字行（题型归类／高考题组，x0 在 tcbox 内边距处≈栏左+5pt）按行首文字豁免。
预期：位图 2、表线 0、【答案】行 4、例/变式条目 4，违规 0。"""
import re
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\演示\章末总结"
PT = 72 / 25.4
MARGIN = 15 * PT
COLSEP = 7.5 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
COLL = (MARGIN, MARGIN + COLW + COLSEP)
INDENT = 7 * PT

def col_left(x):
    idx = int((x - MARGIN + 0.5) // (COLW + COLSEP))
    idx = max(0, min(1, idx))
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

tot_fig = tot_rule = tot_clus = tot_ans = tot_li = tot_cont = tot_viol = 0
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
    li = 0
    viol_c = 0
    n_cont = 0
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            txt = ''.join(sp['text'] for sp in ln['spans']).strip()
            if not txt:
                continue
            if txt.startswith('【答案】'):
                ans += 1
                ink = ink_left(page, ln['bbox'])
                if ink < th(ln['bbox'][0]) - 0.5:
                    viol_a += 1
                    print(f'   违规答案行 墨迹 x0={ink:.2f} < {th(ln["bbox"][0]):.2f} y={ln["bbox"][1]:.1f}')
                continue
            if re.match(r'^例1|^变式1', txt):
                li += 1
                x0 = ln['bbox'][0]
                if x0 > col_left(x0) + 2.0:
                    ink = ink_left(page, ln['bbox'])
                    if ink <= col_left(x0) + 2.0:
                        viol_c += 1
                        print(f'   违规例变条目 题号带内有墨 x0={x0:.2f} ink={ink:.2f} p{pno} y={ln["bbox"][1]:.1f} 「{txt[:16]}」')
                continue
            if re.match(r'^题型归类$|^高考题组$', txt):
                continue
            x0 = ln['bbox'][0]
            cl = col_left(x0)
            if x0 <= cl + 2.0:
                continue
            n_cont += 1
            if x0 < th(x0) - 0.5:
                if re.search(r'[\u4e00-\u9fff]', txt):
                    ink = ink_left(page, ln['bbox'])
                    if ink < th(x0) - 0.5:
                        viol_c += 1
                        print(f'   违规续行 x0={x0:.2f} ink={ink:.2f} < {th(x0):.2f} p{pno} y={ln["bbox"][1]:.1f} 「{txt[:16]}」')

    nv = len(fig_viol) + len(viol_r) + viol_a + viol_c
    tot_fig += len(figs); tot_rule += len(rules); tot_clus += len(excluded)
    tot_ans += ans; tot_li += li; tot_cont += n_cont; tot_viol += nv
    print(f'p{pno} {"OK" if nv == 0 else "!!"} 图 {len(figs)} | 竖细线 {len(cands)}（簇排除 {len(excluded)}）'
          f' | 表线 {len(rules)} | 答案行 {ans} | 例变条目 {li}/续行 {n_cont} | 违规 {nv}')
    for r, t in fig_viol:
        print(f'   违规图 x0={r.x0:.2f} < {t:.2f} y={r.y0:.1f}')
    for r, t in viol_r:
        print(f'   违规表线 x0={r.x0:.2f} < {t:.2f} y={r.y0:.1f}~{r.y1:.1f}')

print(f'—— 合计：位图 {tot_fig}、表线 {tot_rule}（簇排除 {tot_clus}）、【答案】行 {tot_ans}、'
      f'例变条目 {tot_li}/续行 {tot_cont}，违规 {tot_viol}（必须=0）；'
      f'预期 位图 2、表线 0、【答案】行 4、例变条目 4')
ok = tot_viol == 0 and tot_fig == 2 and tot_rule == 0 and tot_ans == 4 and tot_li == 4
print('断言结果：', '通过' if ok else '未通过')
raise SystemExit(0 if ok else 1)
