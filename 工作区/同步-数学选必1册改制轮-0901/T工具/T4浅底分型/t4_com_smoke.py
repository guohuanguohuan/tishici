# -*- coding: utf-8 -*-
"""T4 COM冒烟＋PDF抽查2页渲染（一次性脚本）"""
import os, sys
base = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\T工具\T4浅底分型'
files = [
    (os.path.join(base, r'副本\人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'), 'x2'),
    (os.path.join(base, r'副本\人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'), 'f'),
    (os.path.join(base, r'副本\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'), 'i2'),
]
import win32com.client as wc
word = wc.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for path, tag in files:
        doc = word.Documents.Open(path, ReadOnly=True)
        pages = doc.ComputeStatistics(2)  # wdStatisticPages
        paras = doc.Paragraphs.Count
        print('%s: 开卷OK 页数=%d 段数=%d' % (tag, pages, paras))
        # 导前2页PDF（wdExportFromTo=3: From=1, To=2）
        pdf1 = os.path.join(base, 'pdf_%s_p1.pdf' % tag)
        doc.ExportAsFixedFormat(pdf1, 17, False, 0, 3, 1, 2)
        doc.Close(False)
        print('%s: 已导 %s' % (tag, pdf1))
finally:
    word.Quit()
print('COM Quit 完成')
