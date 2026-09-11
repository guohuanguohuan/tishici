# -*- coding: utf-8 -*-
"""排版病0911 D 笔 after 图：练习线 p2 花形行（重叠量 -6.07→-5.1mm 后）与 before 同几何渲染。
before 几何反解：基础巩固 1820×263 @dpi220 → clip(0,48.8,595.28,134.8)；
综合提升 1576×263 → 高 86.1pt，菱形顶 by v8 y177.2 反推 y0=149.4、x 幅 516pt 右缘锚 595.28 → x0=79.28。
after 同高带、按新菱形顶重新定 y0（基础巩固顶仍 76.3；综合提升新顶 159.3→y0=131.5）。"""
import pymupdf
SRC = r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\练习线\main.pdf'
OUT = r'C:\提示词\工作区\_tmp取证0909c\片I-裁5页码块0911\查验0911'
H = 86.07
d = pymupdf.open(SRC)
p = d[1]  # 练习线 p2
# 实测菱形顶
tops = sorted(g['rect'].y0 for g in p.get_drawings() if 4 < g['rect'].width < 38 and 10 < g['rect'].height < 30)
print('diamond tops p2:', [round(t, 1) for t in tops][:6])
y_jc = 76.3
y_zh = round(tops[4], 1)  # 第 5 枚起＝综合提升组
def save(name, clip):
    pm = p.get_pixmap(dpi=220, clip=clip)
    pm.save(OUT + '\\' + name)
    print(name, pm.width, pm.height)
save('练习线p2-基础巩固-after.png', pymupdf.Rect(0, y_jc - 27.5, 595.28, y_jc - 27.5 + H))
save('练习线p2-综合提升-after.png', pymupdf.Rect(79.28, y_zh - 27.8, 595.28, y_zh - 27.8 + H))
save('练习线p2-全页-after.png', pymupdf.Rect(0, 0, 595.28, p.rect.height))
d.close()
