# -*- coding: utf-8 -*-
"""目验v9：v9 包 6 页全页渲染（同 v8 六图规格：A4 150dpi；测评卷 p2＝A3 横向）。
页映射（页数与 v8 同＝21）：封面 p1／导学件 p1＝包 p2／导学件 p3＝包 p4／册 v1 p1＝包 p7／
答案册样张 p1＝包 p13／测评卷 p2＝包 p16。"""
import pymupdf, os
SRC = r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\靠齐样张包-v9-21页0911.pdf'
OUT = r'C:\提示词\工作区\_tmp取证0909c\片I-裁5页码块0911\目验v9'
os.makedirs(OUT, exist_ok=True)
M = {'封面.png': 1, '导学件p1.png': 2, '导学件p3.png': 4, '册v1p1.png': 7,
     '答案册样张p1.png': 13, '测评卷p2.png': 16}
d = pymupdf.open(SRC)
assert d.page_count == 21, d.page_count
for name, pno in M.items():
    pm = d[pno - 1].get_pixmap(dpi=150)
    pm.save(os.path.join(OUT, name))
    print(name, pm.width, pm.height)
d.close()
