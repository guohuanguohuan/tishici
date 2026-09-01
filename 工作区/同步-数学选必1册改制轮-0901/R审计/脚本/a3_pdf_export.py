# -*- coding: utf-8 -*-
"""R1审计 PDF导出（ExportAsFixedFormat备用路径，本地副本）。X1/I1/B/E全件；其余前5页。"""
import os, shutil, sys, time
sys.stdout.reconfigure(encoding='utf-8')
import win32com.client as wc

D = r'C:\提示词\高中数学\高中数学同步'
PDFDIR = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\PDF'
FILES = [
 ('X1','人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', True),
 ('I1','人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', True),
 ('B','人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', True),
 ('E','人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', True),
 ('X2','人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', False),
 ('I2','人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', False),
 ('C','人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', False),
 ('F','人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', False),
 ('G','人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', False),
 ('H','人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', False),
]
word = wc.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for code, fn, full in FILES:
        src = os.path.join(D, fn)
        local = os.path.join(PDFDIR, code + '_local.docx')
        shutil.copy2(src, local)
        pdf = os.path.join(PDFDIR, code + '.pdf')
        doc = word.Documents.Open(local, ReadOnly=True, AddToRecentFiles=False)
        try:
            if full:
                doc.ExportAsFixedFormat(pdf, 17, False, 0, 0)
            else:
                doc.ExportAsFixedFormat(pdf, 17, False, 0, 3, 1, 5)
            print(code, 'exported', os.path.getsize(pdf), 'full' if full else 'p1-5', flush=True)
        finally:
            doc.Close(False)
        os.remove(local)
finally:
    word.Quit()
print('ALL DONE')
