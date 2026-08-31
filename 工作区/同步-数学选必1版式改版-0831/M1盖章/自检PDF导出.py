# -*- coding: utf-8 -*-
"""M1盖章·自检⑥a：PDF导出（本地副本＋Word原生ExportAsFixedFormat按页段导出——公共规则§14备用路径①）。
每部分首件前5页＋P3/P6后卷首页。落盘 PDF子文件夹。独立子进程，用完Quit。"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client

BASE = os.path.dirname(os.path.abspath(__file__))
PDFDIR = os.path.join(BASE, 'PDF')
os.makedirs(PDFDIR, exist_ok=True)
PROD = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
# (源件名, 本地副本名, 导出页from, to, 输出名)
JOBS = [
    ('人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 'X1', 1, 5, 'P1_X1_p1-5.pdf'),
    ('人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', 'I1', 1, 5, 'P2_I1_p1-5.pdf'),
    ('人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', 'B', 1, 5, 'P3_B_p1-5.pdf'),
    ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', 'C', 1, 1, 'P3_C_p1.pdf'),
    ('人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', 'X2', 1, 4, 'P4_X2_p1-4.pdf'),
    ('人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', 'I2', 1, 5, 'P5_I2_p1-5.pdf'),
    ('人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', 'E', 1, 5, 'P6_E_p1-5.pdf'),
    ('人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 'F', 1, 1, 'P6_F_p1.pdf'),
    ('人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 'G', 1, 1, 'P6_G_p1.pdf'),
    ('人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', 'H', 1, 1, 'P6_H_p1.pdf'),
]
copies = []
for src, short, f, t, out in JOBS:
    dst = os.path.join(PDFDIR, short + '.docx')
    if not os.path.isfile(dst):
        shutil.copy2(os.path.join(PROD, src), dst)
    copies.append((dst, f, t, os.path.join(PDFDIR, out)))

word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for dst, f, t, out in copies:
        doc = word.Documents.Open(dst, ReadOnly=True, AddToRecentFiles=False)
        try:
            if os.path.exists(out):
                os.remove(out)
            doc.ExportAsFixedFormat(out, 17, False, 0, 3, f, t)  # wdExportFormatPDF/wdExportOptimizeForPrint/wdExportFromTo
            print('export %s (pages %d-%d) -> %s' % (os.path.basename(dst), f, t, os.path.basename(out)))
        finally:
            doc.Close(False)
finally:
    word.Quit()
print('done')
