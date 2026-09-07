# -*- coding: utf-8 -*-
r"""题号列恒空断言：main_v2.pdf 逐页核验「图／表／答案行」x0 ≥ 栏左+7mm（-0.5pt 容差）。
背景：\timu 题号悬挂 7mm——题号顶格（栏左），后续行与一切图/表/答案行从题号右缘（栏左+7mm）起排。
断言口径（主会话定）：范围仅图/表/答案行三类；选项/①段顶格对齐全品不在范围；
T0 章首导航表在 multicols 外通栏、无题号语境——登记豁免。
登记排除项（均不在三类范围，探针实证）：
  · multicol 栏线（stroke 中心 x=栏中缝 297.64pt，非表线）；
  · \zutit 探究点黑条 \rule{2.25pt}{13pt}（stroke 中心=栏左+1.125pt，顶格，组标题元素）；
  · 答案行首字【：SimHei【 左半空、xeCJK 行首压缩后 origin 比 ink 左偏 0.56em
    （p4 600dpi 像素实测墨迹左缘 62.44pt ≥ 阈 62.36pt；origin/bbox 口径均伪报 56.48）
    ——锚定行按 300dpi 像素墨迹左缘认定；续行由 \hangafter=0 结构保证（同页像素实测 62.36）。"""
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v2-latex"
PT = 72 / 25.4
MARGIN = 15 * PT                    # 42.52pt 栏左
INDENT = 7 * PT                     # 19.84pt 题号列宽
TH = MARGIN + INDENT - 0.5          # 左栏阈值 61.86pt（登记口径 x0≥61.9pt）
COLSEP = 7.5 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2   # 244.49pt
MID = MARGIN + COLW + COLSEP / 2             # 297.64pt 栏中缝（栏线 stroke 中心）
COLL = (MARGIN, MARGIN + COLW + COLSEP)      # 左/右栏左 42.52 / 308.27
TH_R = TH + COLW + COLSEP                    # 右栏阈值 327.61pt

def ink_left(page, bb, dpi=300):
    """行所在栏的题号列带内最左墨迹像素的 x（pt）。带＝[栏左+0.5, 栏左+7mm+8]，y=bb 上下各扩 0.5pt。"""
    cl = MARGIN if bb[0] < MID else MARGIN + COLW + COLSEP
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

doc = pymupdf.open(BASE + r"\main_v2.pdf")
tot_fig = tot_rule = tot_ans = tot_exempt = tot_viol = 0
for pno, page in enumerate(doc, 1):
    def th(x0):
        return TH if x0 < MID else TH_R

    # --- 图：全部 image 放置矩形 ---
    figs = []
    for img in page.get_images(full=True):
        figs += page.get_image_rects(img[0])
    fig_viol = [(r, th(r.x0)) for r in figs if r.x0 < th(r.x0) - 1e-6]

    # --- 表：竖直规则线（stroke/fill 矩形：宽≤2pt 且高≥4pt） ---
    T0 = []
    if pno == 1:   # 通栏区 y 带 = p1 上宽幅横线（章标题下通栏线＋T0 导航表横线）所夹范围
        wide = [d['rect'] for d in page.get_drawings() if d['rect'].width > 300]
        if wide:
            T0 = [min(r.y0 for r in wide), max(r.y1 for r in wide)]
    rules = exempt = 0
    viol_r = []
    for d in page.get_drawings():
        r = d['rect']
        if not (r.width <= 2.0 and r.height >= 4.0):
            continue
        if abs(r.x0 - MID) < 1.0:
            continue   # multicol 栏线（登记排除，非表线）
        if 12.0 <= r.height <= 14.0 and any(0.5 <= r.x0 - cl <= 2.5 for cl in COLL):
            continue   # \zutit 探究点黑条（登记排除，组标题顶格，不在三类范围）
        rules += 1
        if r.x0 < th(r.x0) - 1e-6:
            if pno == 1 and T0 and T0[0] - 1 <= r.y0 and r.y1 <= T0[1] + 1:
                exempt += 1   # T0 章首导航表最左竖线（multicols 外通栏、无题号语境，登记豁免）
            else:
                viol_r.append((r, th(r.x0)))

    # --- 答案行：锚定行（【答案】起）按像素墨迹左缘认定 ---
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

    nv = len(fig_viol) + len(viol_r) + viol_a
    tot_fig += len(figs); tot_rule += rules - exempt; tot_ans += ans
    tot_exempt += exempt; tot_viol += nv
    print(f'p{pno} {"OK" if nv == 0 else "!!"} 图 {len(figs)} | 表线 {rules - exempt}(T0豁免{exempt}) '
          f'| 答案行 {ans} | 违规 {nv}')
    for r, t in fig_viol:
        print(f'   违规图 x0={r.x0:.2f} < {t:.2f} y={r.y0:.1f}')
    for r, t in viol_r:
        print(f'   违规表线 x0={r.x0:.2f} < {t:.2f} y={r.y0:.1f}~{r.y1:.1f}')

print(f'—— 合计：图 {tot_fig}、表线 {tot_rule}（T0 豁免 {tot_exempt}）、答案行 {tot_ans}，'
      f'违规 {tot_viol}（必须=0）；答案行预期 10、图预期 9')
ok = tot_viol == 0 and tot_ans == 10 and tot_fig == 9
print('断言结果：', '通过' if ok else '未通过')
raise SystemExit(0 if ok else 1)
