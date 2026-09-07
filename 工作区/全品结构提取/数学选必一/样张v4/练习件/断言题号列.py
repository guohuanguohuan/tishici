# -*- coding: utf-8 -*-
r"""题号列恒空断言（v4 练习件版）：main.pdf 逐页核验「图／表／答案行」x0 ≥ 栏左+7mm（-0.5pt 容差）。
背景：\jx／\jans 流水号悬挂 7mm——题号顶格（栏左），后续行与一切图/表从题号右缘（栏左+7mm）起排。
断言口径（主会话定）：范围仅图/表/答案行三类；选项/①段 2em 缩进不在范围。
登记排除项（探针实证）：
  · multicol 栏线（v4 columnseprule=0 实际不画线，过滤保留为防御）；
  · \huaxing 花形组行 tcbox 左竖边（白底黑边圆角框顶格元素，stroke 高 8~30pt 且 x0−栏左≤3pt，登记豁免）；
  · 答案行首「1．」黑体：沿用墨迹口径（锚定行按 300dpi 像素墨迹左缘认定）。
v4 预期：raster 图 0（题6 正方体图＝嵌题侧 TikZ 矢量 30mm、题11 平行六面体图＝题下居中
TikZ 矢量，拍板24 矢量化；pymupdf get_images 不含矢量绘图）；答案行 11（^\d+．【答案】，p2）。"""
import re

import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\练习件"
PT = 72 / 25.4
MARGIN = 15 * PT                    # 42.52pt 栏左
INDENT = 7 * PT                     # 19.84pt 题号列宽
TH = MARGIN + INDENT - 0.5          # 左栏阈值 61.86pt
COLSEP = 7.5 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2   # 244.49pt
MID = MARGIN + COLW + COLSEP / 2             # 297.64pt 栏中缝
COLL = (MARGIN, MARGIN + COLW + COLSEP)      # 左/右栏左
TH_R = TH + COLW + COLSEP                    # 右栏阈值

def ink_left(page, bb, dpi=300):
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
tot_fig = tot_rule = tot_ans = tot_exempt = tot_viol = 0
for pno, page in enumerate(doc, 1):
    # 答案条目行只在含【答案】文本的页统计（v4：p1 题区题面无答案，p1 题号行不属答案行）
    page_has_ans = '【答案】' in page.get_text('text')
    def th(x0):
        return TH if x0 < MID else TH_R

    figs = []
    for img in page.get_images(full=True):
        figs += page.get_image_rects(img[0])
    fig_viol = [(r, th(r.x0)) for r in figs if r.x0 < th(r.x0) - 1e-6]

    rules = exempt = exempt_hua = 0
    viol_r = []
    for d in page.get_drawings():
        r = d['rect']
        if not (r.width <= 2.0 and r.height >= 4.0):
            continue
        if abs(r.x0 - MID) < 1.0:
            continue   # multicol 栏线（登记排除）
        if 8.0 <= r.height <= 30.0 and any(0.5 <= r.x0 - cl <= 3.0 for cl in COLL):
            exempt_hua += 1   # \huaxing 花形组行 tcbox 左竖边（登记豁免）
            continue
        rules += 1
        if r.x0 < th(r.x0) - 1e-6:
            viol_r.append((r, th(r.x0)))

    ans = viol_a = 0
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            txt = ''.join(sp['text'] for sp in ln['spans']).strip()
            # v4 口径：行首「N．」顶格即答案条目行（\ansul 下划线盒会致「N．」与
            # 「【答案】」被 PDF 拆行，不得要求同行；续行悬挂缩进 7mm 不会误入）
            if not page_has_ans:
                continue
            if not re.match(r'\d+．', txt):
                continue
            cl_ = MARGIN if ln['bbox'][0] < MID else MARGIN + COLW + COLSEP
            if ln['bbox'][0] > cl_ + 3:
                continue   # 行首非顶格（续行/行中分数片），非答案条目行
            ans += 1
            ink = ink_left(page, ln['bbox'])
            # 练习件答案行＝流水号行（题号），设计为顶格（hangafter=1，题号列内合法）；
            # 反向断言：墨迹应落在题号列 [栏左, 栏左+7mm] 内——越出即结构错误
            cl = MARGIN if ln['bbox'][0] < MID else MARGIN + COLW + COLSEP
            if not (cl - 0.5 <= ink <= cl + INDENT + 2):
                viol_a += 1
                print(f'   违规答案行 墨迹 x0={ink:.2f} 不在题号列 [{cl - 0.5:.2f},{cl + INDENT + 2:.2f}] y={ln["bbox"][1]:.1f}')

    nv = len(fig_viol) + len(viol_r) + viol_a
    tot_fig += len(figs); tot_rule += rules - exempt; tot_ans += ans
    tot_exempt += exempt; tot_viol += nv
    print(f'p{pno} {"OK" if nv == 0 else "!!"} 图 {len(figs)} | 表线 {rules - exempt}(花形豁免{exempt_hua}) '
          f'| 答案行 {ans} | 违规 {nv}')
    for r, t in fig_viol:
        print(f'   违规图 x0={r.x0:.2f} < {t:.2f} y={r.y0:.1f}')
    for r, t in viol_r:
        print(f'   违规表线 x0={r.x0:.2f} < {t:.2f} y={r.y0:.1f}~{r.y1:.1f}')

print(f'—— 合计：raster 图 {tot_fig}、表线 {tot_rule}、答案行 {tot_ans}，'
      f'违规 {tot_viol}（必须=0）；答案行预期 11、raster 图预期 0（TikZ 矢量化，拍板24）')
ok = tot_viol == 0 and tot_ans == 11 and tot_fig == 0
print('断言结果：', '通过' if ok else '未通过')
raise SystemExit(0 if ok else 1)
