# -*- coding: utf-8 -*-
"""视觉回归取页：按锚文本在 PDF 内搜页，渲染 993px 宽 PNG。"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '回归')

# (件PDF名, 锚文本, 输出名) —— 锚命中页与下一页各渲一张
JOBS = [
 ('人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）', '内切球之圆锥模型', 'I1_圆锥模型区'),
 ('人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）', '外接球之切瓜模型', 'I1_切瓜模型区'),
 ('人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）', '1.2.3.2.3-4', 'B_p034法一法二'),
 ('人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）', '1.2.4.2.11-13', 'B_p061去重'),
 ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）', '几何性质法', 'C_p050_AB1'),
 ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）', '最小时，再求', 'C_p058_最小时'),
 ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）', '建立空间直角坐标系', 'C_p058_B1D'),
 ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）', '墙角模型', 'C_墙角区'),
 ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）', '汉堡模型', 'C_汉堡区'),
 ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）', '双外心模型', 'C_双外心区'),
 ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）', '切瓜模型', 'C_切瓜区'),
 ('人教B版选必1 第2章 平面解析几何·知识清单（完成）', '性质证明', 'I2_p024分数线'),
 ('人教B版选必1 第2章 平面解析几何·知识清单（完成）', '可以写为', 'I2_P0区'),
 ('人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）', '方向角为', 'E_题33'),
 ('人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）', '因为直线过点', 'E_题9'),
 ('人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）', '证明如下：（i）', 'F_合并段'),
 ('人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）', '综上所述，命题成立', 'F_末页'),
 ('人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）', '两连线斜率之积', 'G_编注1'),
 ('人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）', '把斜率积化为', 'G_编注2'),
]
for name, anchor, out in JOBS:
    pdf = os.path.join(OUT, name + '.pdf')
    d = pymupdf.open(pdf)
    hits = []
    for pno in range(len(d)):
        if d[pno].search_for(anchor):
            hits.append(pno)
    if not hits:
        print('!! 锚未命中:', name[:16], anchor)
        continue
    p0 = hits[0]
    for p in {p0, min(p0+1, len(d)-1)}:
        pg = d[p]
        z = 993.0 / pg.rect.width
        pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z))
        fp = os.path.join(OUT, '%s_p%03d.png' % (out, p+1))
        pix.save(fp)
        print('渲染 %s（锚@%d）' % (os.path.basename(fp), p0+1))
    d.close()
# SM 与册目录页全页
for name, out in (('人教B版选必1·使用说明', 'SM'), ('人教B版选必1·册目录页', '目录页')):
    d = pymupdf.open(os.path.join(OUT, name + '.pdf'))
    for p in range(len(d)):
        pg = d[p]
        z = 993.0 / pg.rect.width
        pg.get_pixmap(matrix=pymupdf.Matrix(z, z)).save(os.path.join(OUT, '%s_p%03d.png' % (out, p+1)))
    print('渲染 %s 全 %d 页' % (out, len(d)))
    d.close()
print('RENDER DONE')
