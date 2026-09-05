# -*- coding: utf-8 -*-
"""H 件（2.8 讲练件）成品轮①纠错轮专用：COM 导 PDF + 页数实测。"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import win32com.client as wc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '回归')
os.makedirs(OUT, exist_ok=True)
files = [
 '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
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
