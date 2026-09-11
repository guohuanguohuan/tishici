#!/usr/bin/env python
# 靠齐样张包 v11 拼装（2026-09-11；v10→v11 两笔：①P0 勘误 探九变式1 答案 √13/2→√7/2（钉值门防回卷）
#   ②测评卷偶页页脚品牌位换「羿郭工作室」。件序与页数构成不变；余形制全承 v10。v10 包自本件起作废。
import pymupdf, os
base = r'工作区/字替对照-0909/靠齐样张-0910'
FONT = 'C:/提示词/工作区/字替对照-0909/variantF/fonts/FZFSK.TTF'
out = os.path.join(base, '靠齐样张包-v11-21页0911.pdf')
doc = pymupdf.open()
cover = doc.new_page(width=595.276, height=841.89)
L = [
    ('全品靠齐 · 样张包 v11（21 页）｜勘误＋品牌版', 20, 90),
    ('2026-09-11 · 自 v10 变更两笔，余形制全承 v10：', 10.5, 122),
    ('① P0 勘误：册 v1 p4 探究点九·变式1 答案 √13/2→√7/2。', 10.5, 146),
    ('   源解析补角笔误，逻辑闸全量档逮出（双臂盲解＋两裁判＋主脑', 10.5, 164),
    ('   五方一致）。防回卷：组装body.py 已立钉值门——素材加载后', 10.5, 182),
    ('   硬断言该答案值含 \\sqrt{7}，不符即中止组装（负测已验）。', 10.5, 200),
    ('   v10 包该页作废。', 10.5, 218),
    ('② 品牌：测评卷偶页页脚原全品牌位换「羿郭工作室」', 10.5, 244),
    ('   （用户拍板落位；联系方式按批不入册）。三0 复验过。', 10.5, 262),
    ('件序：① 导学件 5 页 ② 导学件答案册 v1 4 页 ③ 练习线 2 页 ④ 答案册样张 2 页', 11.5, 298),
    ('⑤ 测评卷 2 页 ⑥ 册目录页 2 页 ⑦ 方法小结流程图 1 页 ⑧ 导学增量 2 页', 11.5, 320),
    ('【v10 作废】本包取代 v10。【请裁】冻结前置＝逻辑闸全量过＋', 12.5, 356),
    ('《冻结前不满意清单》全钩；词表 [解法一]/[解法二] 已批（0911），', 12.5, 376),
    ('免复答。', 12.5, 396),
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
n = doc.page_count
print('实测总页数 =', n, '（封面含）')
assert n == 21, '页数≠21：改封面数字重跑'
doc.save(out)
print('saved:', out, '| pages =', pymupdf.open(out).page_count)
