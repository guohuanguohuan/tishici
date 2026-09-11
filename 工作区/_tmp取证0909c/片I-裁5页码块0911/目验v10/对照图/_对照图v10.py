# -*- coding: utf-8 -*-
r"""对照图 v10（补发件）：A–E 五笔变更页 v9（左）｜v10（右）横向拼接 PNG，每图配同名 .txt 一行图注。

数据源＝v9 包与 v10 包（件序/页数相同→包内页号一一对应），同一 dpi、同一裁取框，保证可比。
禁动任何生产源文件：本脚本只读两个包 PDF、只写对照图目录。
"""
import io
import os
import sys

import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PT = 72 / 25.4
V9 = r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\靠齐样张包-v9-21页0911.pdf'
V10 = r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\靠齐样张包-v10-21页0911.pdf'
OUT = r'C:\提示词\工作区\_tmp取证0909c\片I-裁5页码块0911\目验v10\对照图'
os.makedirs(OUT, exist_ok=True)
GAP = 18          # 中缝（pt＝px@72dpi）
d9 = pymupdf.open(V9)
d10 = pymupdf.open(V10)
assert d9.page_count == 21 and d10.page_count == 21


def shot(doc, pno, dpi, rect_mm=None):
    pg = doc[pno - 1]
    clip = None
    if rect_mm:
        x0, y0, x1, y1 = rect_mm
        clip = pymupdf.Rect(x0 * PT, y0 * PT, x1 * PT, y1 * PT)
    return pg.get_pixmap(dpi=dpi, clip=clip, colorspace=pymupdf.csGRAY)


def pair(name, cap, pno, dpi, rect_mm=None):
    a = shot(d9, pno, dpi, rect_mm)
    b = shot(d10, pno, dpi, rect_mm)
    doc = pymupdf.open()
    page = doc.new_page(width=a.width + GAP + b.width, height=max(a.height, b.height) + 16)
    page.insert_image(pymupdf.Rect(0, 16, a.width, 16 + a.height), pixmap=a)
    page.insert_image(pymupdf.Rect(a.width + GAP, 16, a.width + GAP + b.width, 16 + b.height), pixmap=b)
    page.draw_line(pymupdf.Point(a.width + GAP / 2, 0), pymupdf.Point(a.width + GAP / 2, page.rect.height),
                   color=(0.6, 0.6, 0.6), width=0.8)
    page.insert_text((6, 12), 'v9 (void)', fontsize=10, fontname='helv')
    page.insert_text((a.width + GAP + 6, 12), 'v10 (current)', fontsize=10, fontname='helv')
    png = os.path.join(OUT, name + '.png')
    page.get_pixmap(dpi=72).save(png)
    with open(os.path.join(OUT, name + '.txt'), 'w', encoding='utf-8') as f:
        f.write(cap + '\n')
    doc.close()
    print(f'{name}.png  {os.path.getsize(png)//1024}KB  {a.width}+{b.width}px')


# ---- 1 封面（变更清单：v9 四点 A–D → v10 五项 A–E＋v9 作废声明） ----
pair('对照-01-封面-变更清单v9四点变v10五项', '图注：封面（包 p1）。左 v9＝排版病轮四点（A–D）；右 v10＝全品严格对齐五项（A–E）＋「v9 作废」与【请裁】冻结 L1 行。', 1, 150)

# ---- 2 A 判断题断行：导学件 p1 全页＋右栏判断行特写 ----
pair('对照-02-导学件p1-A判断行断行优化-全页', '图注：导学件（variantF）p1＝包 p2 全页。A 笔改 \zhentib 宏（句尾开廉价断点＋hbox 封丢胶支路），本页右栏题(1) 由「等.（　）」整块挤次行改为题干完整收行、（　）独落次行贴栏右；全页其余形制不动。', 2, 150)
pair('对照-03-导学件p1右栏判断行-A特写', '图注：A 笔特写＝包 p2 右栏 x105–195mm/y203–228mm（300dpi）。左 v9：行1 尾余空 33.2pt（≈3.4 字）、「等.（　）」挤次行；右 v10：行1 完整收行、余空 19.7pt（≈1.9 字）、（　）独行墨距栏右 1.20mm；下条 (2) 两处右挂形制不变（1.11mm）。', 2, 300, (105, 203, 195, 228))

# ---- 3 B/C 册 v1：p1 全页＋头部块特写＋p3 解析区 ----
pair('对照-04-册v1p1-B层级缩进C填空串-全页', '图注：导学件答案册 v1 p1＝包 p7 全页。B 笔＝题号/标签行顶格、内容与续行及后续段收一档 5.0mm、「知识点N」标题居中；C 笔＝课前预习填空串改按条目分段「N．值　值…」（旧逐空编号 1值2值…11值）。', 7, 150)
pair('对照-05-册v1p1头部块-B缩进C条目分段-特写', '图注：B/C 特写＝包 p7 左栏 x15–104mm/y58–128mm（300dpi）。左 v9：全顶格＋逐空编号；右 v10：知识点标题两行居中、[答案] 标签行顶格、条目分段与续行收一档 5.0mm（≈1.4 字，照全品 p1 实测 70/100px）。', 7, 300, (15, 58, 104, 128))
pair('对照-06-册v1p3解析区-B续行悬挂-全页', '图注：册 v1 p3＝包 p9 全页（解析/详解区）。B 笔使续行与后续段收一档；本页同时是 J4 拉伸侧效登记页（缩进致行宽 84→79mm、断点位移，峰 20.17pt≈0.7 字，已目验无断裂大洞，P2 随下轮处置）。', 9, 150)
pair('对照-07-册v1p3解析行-J4拉伸侧效登记-特写', '图注：J4 侧效特写＝包 p9 左栏 x15–104mm/y205–224mm（300dpi）。右 v10 该行「…，故…」逗号后孔 20.17pt（≈0.7 字，v9 同页峰 8.43pt）——缩进副作用，登记留档，未动全局排版参数。', 9, 300, (15, 205, 104, 224))

# ---- 4 B 答案册样张 p1 ----
pair('对照-08-答案册样张p1-B层级缩进-全页', '图注：答案册样张 p1＝包 p13 全页。B 笔同款宏（与册 v1 逐字节一致）：标签行顶格、[分析]/[详解] 续行收一档、题型行同档；页数 2 页不变、check.py 退出 0、⑥悬挂深度 5.80/7.60mm 仍合靶。', 13, 150)
pair('对照-09-答案册样张p1条目块-B缩进-特写', '图注：B 笔特写＝包 p13 左栏 x15–104mm/y60–128mm（300dpi）。左 v9 续行贴栏左缘；右 v10「与数量积即可.」「所以|a+b|=√7…」等续行收一档 5.15mm，层级一眼可辨。', 13, 300, (15, 60, 104, 128))

# ---- 5 D 测评卷页脚 ----
pair('对照-10-测评卷p2-D页脚品牌串-全页', '图注：测评卷 p2＝包 p16（A3 横向）全页。D 笔＝LE 页脚删「全品学练考」（RO 本无），全包明文「全品」0 次；2 页不变、三0。', 16, 100)
pair('对照-11-测评卷p2页脚-D特写', '图注：D 笔特写＝包 p16 页脚带 x10–100mm/y266–279mm（300dpi）。左 v9 页脚含「全品学练考」（x23.3–36.9mm）；右 v10 该串消失，页脚起首改页码＋「卷」＋「选择性必修第一册」＋「RJB」。', 16, 300, (10, 266, 100, 279))

# ---- 6 E 导学增量 ----
pair('对照-12-导学增量p1-E删生产注记-全页', '图注：导学增量 p1＝包 p20 全页。E 笔＝\gaokaowei 删「[题源待补]」与「〔高考真题位·待源〕」，保留 [精选高考题] 标签行＋45mm 槽位；全件注记串明文 0 次；2 页不变。', 20, 150)
pair('对照-13-导学增量p1高考位-E特写', '图注：E 笔特写＝包 p20 通栏 x12–196mm/y150–220mm（200dpi）。左 v9 两处高考位＝「[精选高考题] [题源待补] 〔高考真题位·待源〕」；右 v10 仅余「[精选高考题]」＋空槽。', 20, 200, (12, 150, 196, 220))

# ---- 7 A 顺修项：增量 v9 左对齐孤括号行（v9 漏检，本轮同修） ----
pair('对照-14-导学增量p2判断行-A顺修左对齐孤括号行', '图注：A 笔顺修 v9 漏检＝包 p21 左栏 x15–104mm/y90–112mm（300dpi）。左 v9：旧宏在全角「．」句尾断在胶上丢胶，（　）成**左对齐**孤括号行（墨距栏右 76.72mm）；右 v10：同宏同修后题干完整收行、（　）独行右对齐贴栏（墨距 1.20mm）。', 21, 300, (15, 90, 104, 112))

d9.close()
d10.close()
print('对照图输出目录：', OUT)
