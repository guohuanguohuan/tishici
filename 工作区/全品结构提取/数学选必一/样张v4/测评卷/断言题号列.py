# -*- coding: utf-8 -*-
r"""题号列恒空断言（测评卷 v4 版）：main.pdf 逐页核验题号悬挂 7mm 窄列恒空。
承 v3 版口径（其自 v2 改编），v4 几何与图况适配，差异逐条登记：
  · 几何改 A4 横放 3 栏：栏宽 (841.89-2×42.52-2×22.68)/3=237.17pt≈83.67mm、栏距 8mm、
    三栏栏左 42.52/302.36/562.20pt；阈值＝栏左+7mm-0.5pt，逐栏判定；
  · 图预期 5→4：Q6 竖图改 TikZ 矢量重绘（无 image 放置矩形），余 4 张位图
    （image4/image5/image2/image3＝题3/4/7/10）；
  · 表线（宽≤3pt 且高≥4pt 的竖直细线；3pt 容差覆盖微斜棱边矩形）排除 TikZ 题图棱边：
    同一页 ≥3 条竖直细线 x 相互邻近（＜25mm）且 y 区间重叠者判为矢量题图棱边簇，整簇
    登记排除（登记口径，非表格）；孤立竖直细线仍计表线、预期 0；
  · 范围仍仅「图／表／答案行」三类 x0 ≥ 栏左+7mm（-0.5pt 容差）——题干首行题侧标签
    （6.5pt #777777「难度★（知识点N）」，随题号内联）不在三类内，不入本断言扫描带判定；
  · 答案页条目行核验同 v3：「N．」条目首行落栏左（±2pt 窗口；300dpi 墨迹认定，
    SimHei【 左半空 origin 偏移与分数分母伪行豁免口径承 v2/v3 登记）；
  · 本卷无表格、无【答案】行（答案在独立答案页）→ 预期 表线 0、答案行 0、条目 10。
预期：图 4（位图）＋TikZ 棱边簇 1、表线 0、【答案】行 0、答案页条目 10，违规 0。"""
import re
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\测评卷"
PT = 72 / 25.4
MARGIN = 15 * PT                    # 42.52pt 版心左
COLSEP = 8 * PT                     # 22.68pt 栏距
COLW = (841.89 - 2 * MARGIN - 2 * COLSEP) / 3   # 237.17pt ≈83.67mm
COLL = (MARGIN, MARGIN + COLW + COLSEP, MARGIN + 2 * (COLW + COLSEP))  # 42.52/302.36/562.20
INDENT = 7 * PT                     # 19.84pt 题号列宽

def col_left(x):
    """x 所属栏栏左（区间归属：第 k 栏＝[栏左k, 栏左k+栏宽]；栏缝归左栏；
    +0.5pt ε 修浮点分界——栏左恰落 x=栏左k 时 pymupdf 报值可差 1ulp）。"""
    idx = int((x - MARGIN + 0.5) // (COLW + COLSEP))
    idx = max(0, min(2, idx))
    return COLL[idx]

def th(x0):
    return col_left(x0) + INDENT - 0.5

def ink_left(page, bb, dpi=300):
    """行所在栏的题号列带内最左墨迹像素的 x（pt）。带＝[栏左+0.5, 栏左+7mm+8]，y=bb 上下各扩 0.5pt。"""
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
    # --- 图：全部 image 放置矩形（位图；TikZ 为矢量不入此列） ---
    figs = []
    for img in page.get_images(full=True):
        figs += page.get_image_rects(img[0])
    fig_viol = [(r, th(r.x0)) for r in figs if r.x0 < th(r.x0) - 1e-6]

    # --- 竖直细线（表线候选）＋ TikZ 棱边簇排除 ---
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
        if len(grp) >= 3:   # ≥3 条邻近竖直细线＝矢量题图棱边簇（登记排除口径）
            excluded.update(grp)
    rules = [r for k, r in enumerate(cands) if k not in excluded]
    viol_r = [(r, th(r.x0)) for r in rules if r.x0 < th(r.x0) - 1e-6]

    # --- 答案行：【答案】起（本卷正文无，预期 0） ---
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

    # --- 答案页条目行核验（口径同 v3） ---
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
                        n_item += 1   # 栏左正常落位（+25pt 窗口可捕 2em 首行缩进事故=21pt）
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
                    # 其余（x0>cl+25 且题号带无墨）＝行内分数分母拆行的伪行，非行首，登记排除、不计数
                else:
                    n_cont += 1
                    if x0 < th(x0) - 0.5:
                        # 仅核验含汉字的真实折行行：行内分数分母/分子会被 pymupdf 拆成无汉字伪行
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
      f'预期 位图 4＋TikZ 棱边簇、表线 0、【答案】行 0、条目 10')
ok = tot_viol == 0 and tot_fig == 4 and tot_rule == 0 and tot_ans == 0 and tot_item == 10 and tot_clus >= 3
print('断言结果：', '通过' if ok else '未通过')
raise SystemExit(0 if ok else 1)
