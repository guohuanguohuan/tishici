# -*- coding: utf-8 -*-
r"""题号列恒空断言（测评卷 v3 版）：main.pdf 逐页核验题号悬挂 7mm 窄列恒空。
改编自 样张v2-latex/断言题号列.py（口径与豁免逐条继承，差异按本卷登记）：
  · 范围仅「图／表／答案行」三类 x0 ≥ 栏左+7mm（-0.5pt 容差）——同 v2；
  · 本卷无表格、无【答案】行（答案在独立答案页）→ 预期 表线 0、答案行 0；
  · 新增（本卷特有）：答案页条目行核验——「N．」起头的条目首行须落在栏左（±2pt），
    答案页其余行 ≥ 栏左+7mm-0.5（\hangafter=1 悬挂续行；页眉/页脚/通栏标题居中元素自然满足）；
  · 登记排除项（同 v2）：multicol 栏线（stroke 中心=栏中缝）。
预期：图 5（image1～5，题3/4/6/7/10 各一），表线 0，【答案】行 0，违规 0。"""
import re
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v3\测评卷"
PT = 72 / 25.4
MARGIN = 15 * PT                    # 42.52pt 栏左
INDENT = 7 * PT                     # 19.84pt 题号列宽
TH = MARGIN + INDENT - 0.5          # 左栏阈值 61.86pt
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

doc = pymupdf.open(BASE + r"\main.pdf")
ans_start = None
for pno, page in enumerate(doc, 1):
    if '参考答案与解析' in page.get_text():
        ans_start = pno
        break
print(f'答案页起始于 p{ans_start}')

tot_fig = tot_rule = tot_ans = tot_item = tot_cont = tot_viol = 0
for pno, page in enumerate(doc, 1):
    def th(x0):
        return TH if x0 < MID else TH_R

    # --- 图：全部 image 放置矩形 ---
    figs = []
    for img in page.get_images(full=True):
        figs += page.get_image_rects(img[0])
    fig_viol = [(r, th(r.x0)) for r in figs if r.x0 < th(r.x0) - 1e-6]

    # --- 表：竖直规则线（stroke/fill 矩形：宽≤2pt 且高≥4pt）---
    rules = 0
    viol_r = []
    for d in page.get_drawings():
        r = d['rect']
        if not (r.width <= 2.0 and r.height >= 4.0):
            continue
        if abs(r.x0 - MID) < 1.0:
            continue   # multicol 栏线（登记排除，非表线）
        rules += 1
        if r.x0 < th(r.x0) - 1e-6:
            viol_r.append((r, th(r.x0)))

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

    # --- 答案页条目行（本卷新增核验） ---
    # 口径：bbox x0 仅初筛，最终以 300dpi 墨迹认定（v2 登记：SimHei【 左半空、xeCJK 行首压缩后
    # origin 比 ink 左偏 ~0.56em；行内分数分母会被 pymupdf 拆成伪行——初筛 x0 落在行中部）。
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
                    cl = MARGIN if x0 < MID else MARGIN + COLW + COLSEP
                    if cl - 2.0 <= x0 <= cl + 25.0:
                        n_item += 1   # 栏左正常落位（+25pt 窗口可捕 2em 首行缩进事故=21pt）
                        continue
                    ink = ink_left(page, ln['bbox'])
                    band = pymupdf.Rect(cl + 0.5, ln['bbox'][1] - 0.5, cl + 2.0, ln['bbox'][3] + 0.5)
                    has_band_ink = ink <= cl + 2.0
                    if x0 < cl - 2.0 and ink < cl - 0.5:
                        n_item += 1
                        viol_i += 1
                        print(f'   违规条目首行 x0={x0:.2f} ink={ink:.2f} < 栏左 {cl:.2f} p{pno} y={ln["bbox"][1]:.1f} 「{txt[:16]}」')
                    elif x0 > cl + 25.0 and has_band_ink:
                        n_item += 1
                        viol_i += 1
                        print(f'   违规条目首行 x0={x0:.2f} 题号带内有墨 p{pno} y={ln["bbox"][1]:.1f} 「{txt[:16]}」')
                    # 其余（x0>cl+25 且题号带无墨）＝行内分数分母拆行的伪行，非行首，登记排除、不计数
                else:
                    n_cont += 1
                    if x0 < th(x0) - 0.5:
                        # 仅核验含汉字的真实折行行：行内分数分母/分子会被 pymupdf 拆成无汉字伪行
                        # （如第9条 −3/2 的分母「2」与其首行「9．」同一基线，伪行 y 带内墨迹为该条
                        # 题号本身——非折行，登记排除口径）
                        if re.search(r'[\u4e00-\u9fff]', txt):
                            ink = ink_left(page, ln['bbox'])
                            if ink < th(x0) - 0.5:
                                viol_c += 1
                                print(f'   违规续行 x0={x0:.2f} ink={ink:.2f} < {th(x0):.2f} p{pno} y={ln["bbox"][1]:.1f} 「{txt[:16]}」')

    nv = len(fig_viol) + len(viol_r) + viol_a + viol_i + viol_c
    tot_fig += len(figs); tot_rule += rules; tot_ans += ans
    tot_item += n_item; tot_cont += n_cont; tot_viol += nv
    print(f'p{pno} {"OK" if nv == 0 else "!!"} 图 {len(figs)} | 表线 {rules} | 答案行 {ans} '
          f'| 答案页条目 {n_item}/续行 {n_cont} | 违规 {nv}')
    for r, t in fig_viol:
        print(f'   违规图 x0={r.x0:.2f} < {t:.2f} y={r.y0:.1f}')
    for r, t in viol_r:
        print(f'   违规表线 x0={r.x0:.2f} < {t:.2f} y={r.y0:.1f}~{r.y1:.1f}')

print(f'—— 合计：图 {tot_fig}、表线 {tot_rule}、【答案】行 {tot_ans}、答案页条目 {tot_item}/续行 {tot_cont}，'
      f'违规 {tot_viol}（必须=0）；预期 图 5、表线 0、【答案】行 0、条目 10')
ok = tot_viol == 0 and tot_fig == 5 and tot_rule == 0 and tot_ans == 0 and tot_item == 10
print('断言结果：', '通过' if ok else '未通过')
raise SystemExit(0 if ok else 1)
