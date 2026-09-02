# -*- coding: utf-8 -*-
"""R2终审计——PDF导出（X1/C/B三件，本地副本ExportAsFixedFormat；COM用毕Quit）。"""
import os, shutil, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from win32com.client import DispatchEx

D = r'C:\提示词\高中数学\高中数学同步'
W = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\PDF'
FILES = [
 ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
 ('C',  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
 ('B',  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
]
for code, fn in FILES:
    shutil.copy2(os.path.join(D, fn), os.path.join(W, code + '_local.docx'))

word = DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
print('Word version:', word.Version)
try:
    for code, fn in FILES:
        doc = word.Documents.Open(os.path.join(W, code + '_local.docx'), ReadOnly=True)
        doc.ExportAsFixedFormat(os.path.join(W, code + '.pdf'), 17)  # wdExportFormatPDF
        pages = doc.ComputeStatistics(2)  # wdStatisticPages
        print('%s: COM页数=%d' % (code, pages))
        doc.Close(False)
finally:
    word.Quit()
print('DONE')
