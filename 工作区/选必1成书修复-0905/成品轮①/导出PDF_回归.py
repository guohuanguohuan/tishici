# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import win32com.client as wc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '回归')
os.makedirs(OUT, exist_ok=True)
files = [
 '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
 '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
 '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
 '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
 '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
 '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
 '人教B版选必1·使用说明.docx',
 '人教B版选必1·册目录页.docx',
]
word = wc.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for fn in files:
        src = os.path.join(HERE, fn)
        dst = os.path.join(OUT, fn[:-5] + '.pdf')
        doc = word.Documents.Open(src, ReadOnly=True, AddToRecentFiles=False)
        try:
            doc.ExportAsFixedFormat(OutputFileName=dst, ExportFormat=17)  # wdExportFormatPDF
            print('PDF ok:', fn, '->', doc.ComputeStatistics(2), '页')  # wdStatisticPages=2
        finally:
            doc.Close(False)
finally:
    word.Quit()
print('ALL DONE')
