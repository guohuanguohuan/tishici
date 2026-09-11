#!/usr/bin/env python
# 靠齐样张包 v7 拼装（2026-09-11；答案制A 落地版）
# 结构与 v6 差异：导学件＝去答案版全件 5 页（替换 v6 的 vf p2/p3 两页演示）；
# 新增《导学件答案册 v1》4 页；其余件序不变（练习线/答案册样张/测评卷/册目录页/流程图/导学增量）。
import pymupdf, os
base = r'工作区/字替对照-0909/靠齐样张-0910'
FONT = 'C:/提示词/工作区/字替对照-0909/variantF/fonts/FZFSK.TTF'
out = os.path.join(base, '靠齐样张包-v7-21页0911.pdf')
doc = pymupdf.open()
cover = doc.new_page(width=595.276, height=841.89)
L = [
    ('全品靠齐 · 样张包 v7（21 页）｜答案制A 落地版', 20, 90),
    ('2026-09-11 · 自 v6 变更：', 10.5, 125),
    ('① 导学件＝去答案版（7→5 页）：正文【答案】【分析】【详解】【点睛】63 块全移出，', 10.5, 148),
    ('   保留【诊断分析】[解析]（判断域）与【素养小结】；双断言 54✓/0✗＋顶格过。', 10.5, 168),
    ('② 新增《导学件答案册 v1》（4 页）：23 题同号入册（[答案]23/分析9/详解9/点睛2，', 10.5, 194),
    ('   题型行18/总结9）；页码块按裁5 出血到纸边（同导学件档）。', 10.5, 214),
    ('③ 测评卷：Q6 题下【答案】/【详解】块按答案制A 移出卷面（原为旧任务书内联演示）。', 10.5, 240),
    ('④ 答案册样张：页码块裁5 出血＋数字 10.7pt（与导学件同档）。', 10.5, 260),
    ('', 11, 280),
    ('件序：① 导学件 5 页 ② 导学件答案册 v1 4 页 ③ 练习线 2 页 ④ 答案册样张 2 页', 11.5, 310),
    ('⑤ 测评卷 2 页 ⑥ 册目录页 2 页 ⑦ 方法小结流程图 1 页 ⑧ 导学增量 2 页', 11.5, 332),
    ('', 11, 356),
    ('【请裁】① 冻结＝L1 基线；② [解法一]/[解法二] 拟入答案册词表（小点）。', 12.5, 395),
]
for txt, size, y in L:
    if txt:
        cover.insert_text((60, y), txt, fontsize=size, fontfile=FONT, fontname='fz')
vf = pymupdf.open('C:/提示词/工作区/字替对照-0909/variantF/main.pdf')
doc.insert_pdf(vf); vf.close()                                    # 导学件 全件 5 页
v1 = pymupdf.open('C:/提示词/工作区/字替对照-0909/导学件答案册-v1/main.pdf')
doc.insert_pdf(v1); v1.close()                                    # 导学件答案册 v1 4 页
for d in ['练习线', '答案册', '测评卷', '册目录页', '流程图', '导学增量']:
    src = pymupdf.open(os.path.join(base, d, 'main.pdf'))
    doc.insert_pdf(src); src.close()
doc.save(out)
print('saved:', out, '| pages =', pymupdf.open(out).page_count)
